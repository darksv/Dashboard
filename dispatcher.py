import sys
sys.path.append('app')
import config
import asyncio
import logging
import json
import math
from typing import Optional
from collections import defaultdict
from datetime import datetime
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1, QOS_2
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


calculators = defaultdict(lambda: AverageCalculator(
    period=config.MEASUREMENT_AVERAGING_PERIOD,
    start_at=datetime.now().replace(second=0, microsecond=0)
))


async def process_message(client, message):
    packet = message.publish_packet
    topic = packet.variable_header.topic_name
    payload = packet.payload.data.decode('ascii')
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

        calculator = calculators[channel.id]
        calculator.push_value(value)
        if channel.logging_enabled and calculator.has_average:
            value, timestamp = calculator.pop_average()
            log_channel_value(db, channel.id, value, timestamp, ignore_duplicates=True)

            topic = message.topic + '/log'
            payload = json.dumps(dict(value=value, timestamp=timestamp.isoformat())).encode('ascii')
            await client.publish(topic, payload, QOS_2)
            logger.info('published message at %s with %s (QOS: %d)', topic, payload, QOS_2)


# noinspection PyBroadException
async def mqtt_task():
    client_config = dict(
        auto_reconnect=False,
        keep_alive=5,
        ping_delay=1
    )

    client = MQTTClient(config=client_config)
    await client.connect('mqtt://home.spoder.pl/')
    await client.subscribe([
        ('+/+', QOS_1)
    ])

    while True:
        try:
            message = await client.deliver_message(timeout=10)
        except asyncio.TimeoutError:
            break

        try:
            await process_message(client, message)
        except KeyboardInterrupt:
            break
        except:
            logger.exception('exception when processing MQTT message')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mqtt_task())
