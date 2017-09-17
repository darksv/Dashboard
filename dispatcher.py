import sys
sys.path.append('app')
import config
import asyncio
import logging
import json
import math
import websockets
from asyncio.queues import Queue
from typing import Optional
from collections import defaultdict
from datetime import datetime
from core import DB
from core.services.channel_update import AverageCalculator
from core.services.channels import get_or_create_channel, update_channel, log_channel_value
from core.services.devices import get_or_create_device


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def parse_value(val: str) -> Optional[float]:
    result = float(val)
    if not math.isnan(result) and not math.isinf(result):
        return result


client_queue = dict()

calculators = defaultdict(lambda: AverageCalculator(
    period=config.MEASUREMENT_AVERAGING_PERIOD,
    start_at=datetime.now().replace(second=0, microsecond=0)
))


def process_message(client, topic, payload):
    logger.debug('received message topic: %s payload: %s', topic, payload)

    device_uuid, channel_uuid = topic.split('/', 2)
    value = parse_value(payload)
    if value is None:
        logger.warning('invalid payload %s', payload)
        return

    # quick fix for DS18B20 driver error for negative temperatures
    if value > 4000:
        value -= 4096

    with DB.connect() as db:
        device = get_or_create_device(db, device_uuid)
        channel = get_or_create_channel(db, channel_uuid, device_id=device.id)

        update_channel(db, channel.id, value=value, value_updated=datetime.now())
        logger.debug('updated channel %d', channel.id)

        item = json.dumps([
            'channel_updated',
            dict(
                channel_uuid=channel_uuid,
                timestamp=datetime.now().isoformat(),
                value=value
            )
        ])
        for queue in client_queue.values():
            queue.put_nowait(item)

        calculator = calculators[channel.id]
        calculator.push_value(value)
        if channel.logging_enabled and calculator.has_average:
            value, timestamp = calculator.pop_average()
            log_channel_value(db, channel.id, value, timestamp, ignore_duplicates=True)
            for queue in client_queue.values():
                queue.put_nowait(json.dumps([
                    'channel_logged',
                    dict(
                        channel_uuid=channel_uuid,
                        timestamp=timestamp.isoformat(),
                        value=value
                    )
                ]))


def mqtt_client():
    import paho.mqtt.client as mqtt

    def on_connect(client, userdata, flags, rc):
        client.subscribe('+/+')

    def on_message(client, userdata, msg):
        process_message(client, msg.topic, msg.payload.decode('ascii'))

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config.MQTT_HOST, config.MQTT_PORT, 60)
    client.loop_start()


async def consumer_handler(websocket):
    while True:
        await websocket.recv()


async def producer_handler(websocket):
    queue = Queue()
    client_queue[websocket] = queue
    while True:
        try:
            item = queue.get_nowait()
            await websocket.send(item)
        except asyncio.QueueEmpty:
            continue


async def websocket_handler(websocket, path):
    try:
        done, pending = await asyncio.wait(
            [
                consumer_handler(websocket),
                producer_handler(websocket)
            ],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
    except websockets.ConnectionClosed:
        pass
    finally:
        del client_queue[websocket]


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(websocket_handler, '127.0.0.1', 8080)
    start_mqtt = loop.run_in_executor(None, mqtt_client)
    loop.run_until_complete(start_mqtt)
    loop.run_until_complete(start_server)
    loop.run_forever()
