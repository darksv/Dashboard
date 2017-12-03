import sys
import logging

sys.path.append('app')
main_logger = logging.getLogger()
main_logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(stream=sys.stderr)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
main_logger.addHandler(stream_handler)
logger = logging.getLogger(__name__)


import config
import asyncio
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
from bus import Bus


def parse_value(val: str) -> Optional[float]:
    try:
        result = float(val)
    except ValueError:
        return None
    else:
        if not math.isnan(result) and not math.isinf(result):
            return result


bus = Bus()
client_queue = dict()

calculators = defaultdict(lambda: AverageCalculator(
    period=config.MEASUREMENT_AVERAGING_PERIOD,
    start_at=datetime.now().replace(second=0, microsecond=0)
))


@bus.on('channel_updated')
@bus.on('channel_logged')
async def channel_event(event, data):
    for queue in client_queue.values():
        await queue.put(json.dumps([event, data]))


@bus.on('mqtt_message')
async def process_message(_event, data):
    device_uuid, channel_uuid = data['topic'].split('/', 2)
    payload = data['payload']
    value = parse_value(payload)
    if value is None:
        logger.warning('invalid payload: {}'.format(payload))
        return

    with DB.connect() as db:
        device = get_or_create_device(db, device_uuid)
        channel = get_or_create_channel(db, channel_uuid, device_id=device.id)
        update_channel(db, channel.id, value=value, value_updated=datetime.now())
        await bus.emit('channel_updated', dict(
            channel_uuid=channel_uuid,
            timestamp=datetime.now().isoformat(),
            value=value
        ))
        calculator = calculators[channel.id]
        calculator.push_value(value)
        if channel.logging_enabled and calculator.has_average:
            value, timestamp = calculator.pop_average()
            log_channel_value(db, channel.id, value, timestamp, ignore_duplicates=True)
            await bus.emit('channel_logged', dict(
                channel_uuid=channel_uuid,
                timestamp=timestamp.isoformat(),
                value=value
            ))


def mqtt_client(loop):
    import paho.mqtt.client as mqtt

    # noinspection PyShadowingNames
    def on_connect(client, _userdata, _flags, _rc):
        client.subscribe('+/+')

    def on_message(_client, _userdata, message):
        topic = message.topic
        payload = message.payload.decode('ascii')
        loop.call_soon_threadsafe(
            lambda: asyncio.ensure_future(
                bus.emit('mqtt_message', dict(
                    topic=topic,
                    payload=payload
                ))
            )
        )

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config.MQTT_HOST, config.MQTT_PORT, 60)
    client.loop_forever(retry_first_connection=True)


async def websocket_receiver(websocket):
    while True:
        data = await websocket.recv()
        for other, queue in client_queue.items():
            if other != websocket:
                await queue.put(data)


async def websocket_sender(websocket):
    queue = Queue()
    client_queue[websocket] = queue
    while True:
        item = await queue.get()
        await websocket.send(item)


async def websocket_handler(websocket, _path):
    try:
        futures = [
            websocket_receiver(websocket),
            websocket_sender(websocket)
        ]
        done, pending = await asyncio.wait(futures, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
    except websockets.ConnectionClosed:
        pass
    finally:
        del client_queue[websocket]


async def tick_1s():
    while True:
        await asyncio.sleep(1.0)
        await bus.emit('tick')


def main():
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(websocket_handler, '0.0.0.0', 8080)
    start_mqtt = loop.run_in_executor(None, mqtt_client, loop)
    asyncio.ensure_future(start_mqtt)
    asyncio.ensure_future(start_server)
    asyncio.ensure_future(tick_1s())
    loop.run_forever()


if __name__ == '__main__':
    main()
