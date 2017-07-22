import sys
sys.path.append('app')
import config
import asyncio
import json
import math
from collections import defaultdict
from datetime import datetime
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1, QOS_2
from core import DB
from core.services.channel_update import AverageCalculator
from core.services.channels import get_or_create_channel, update_channel, log_channel_value
from core.services.devices import get_or_create_device


def parse_value(val: str) -> float:
    result = float(val)
    if math.isnan(result) or math.isinf(result):
        raise ValueError('Only finite float is a valid value (got {0})'.format(result))

    return result


calculators = defaultdict(lambda: AverageCalculator(
    period=config.MEASUREMENT_AVERAGING_PERIOD,
    start_at=datetime.now().replace(second=0, microsecond=0)
))


async def mqtt_task():
    client = MQTTClient()

    await client.connect('mqtt://127.0.0.1/')
    await client.subscribe([
        ('+/+', QOS_1)
    ])

    try:
        while True:
            message = await client.deliver_message()
            packet = message.publish_packet

            topic = packet.variable_header.topic_name
            payload = packet.payload.data.decode('ascii')

            device_uuid, channel_uuid = topic.split('/', 2)
            value = parse_value(payload)

            # quick fix for DS18B20 driver error for negative temperatures
            if value > 4000:
                value -= 4096

            with DB.connect() as db:
                device = get_or_create_device(db, device_uuid)
                channel = get_or_create_channel(db, channel_uuid, device_id=device.id)

                update_channel(db, channel.id, value=value, value_updated=datetime.now())

                calculator = calculators[channel.id]
                calculator.push_value(value)
                if calculator.has_average:
                    value, timestamp = calculator.pop_average()
                    log_channel_value(db, channel.id, value, timestamp, ignore_duplicates=True)

                    topic = message.topic + '/log'
                    payload = json.dumps(dict(value=value, timestamp=timestamp.isoformat())).encode('ascii')
                    await client.publish(topic, payload, QOS_2)

    except ClientException as e:
        print(e)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(mqtt_task())
