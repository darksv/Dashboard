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

        calculator = calculators[channel.id]
        calculator.push_value(value)
        if channel.logging_enabled and calculator.has_average:
            value, timestamp = calculator.pop_average()
            log_channel_value(db, channel.id, value, timestamp, ignore_duplicates=True)

            topic = topic + '/log'
            payload = json.dumps(dict(value=value, timestamp=timestamp.isoformat())).encode('ascii')
            client.publish(topic, payload, qos=2)
            logger.info('published message at %s with %s (QOS=2)', topic, payload)


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
    client.loop_forever(retry_first_connection=True)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(loop.run_in_executor(None, mqtt_client()))
