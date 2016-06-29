import math
import paho.mqtt.client as mqtt
from app.db import DB
from app.db.channels import get_or_create_channel, update_channel_value
from app.db.devices import get_or_create_device
import config


def on_connect(client, userdata, flags, rc):
    print('Connected (status={0})'.format(rc))

    client.subscribe('#')


def parse_value(val: str) -> float:
    result = float(val)
    if math.isnan(result) or math.isinf(result):
        raise ValueError('Only finite float is a valid value (got {0})'.format(result))

    return result


def on_message(client, userdata, msg):
    try:
        device_uuid, channel_uuid = msg.topic.split('/')
        value = parse_value(msg.payload.decode('ascii'))
    except ValueError:
        print(msg.topic, msg.payload)
    else:
        print('Received channel update: device={0} channel={1} value={2}'.format(device_uuid, channel_uuid, value))

        try:
            device = get_or_create_device(DB, device_uuid)
            channel = get_or_create_channel(DB, channel_uuid, device_id=device.id)
            update_channel_value(DB, channel.id, value)

            print('Channel update successful')
        except SystemError as e:
            print('Exception', e)


def start_client(in_background: bool=False):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config.MQTT_HOST, config.MQTT_PORT, 60)

    if in_background:
        client.loop_start()
    else:
        client.loop_forever()


if __name__ == '__main__':
    start_client(in_background=False)
