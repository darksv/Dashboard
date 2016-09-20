import math
import paho.mqtt.client as mqtt
import requests
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
            req = requests.get('https://xxx/updateChannel',
                               dict(deviceUuid=device_uuid, channelUuid=channel_uuid, value=value))

            if req.status_code == 200:
                print('Channel update successful')
            else:
                print('Update unsuccessful', req.status_code, req.content)
        except SystemError as e:
            print('Exception', e)


def _start_client(in_background: bool=False):
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        if in_background:
            client.connect_async(config.MQTT_HOST, config.MQTT_PORT, 60)
            client.loop_start()
        else:
            client.connect(config.MQTT_HOST, config.MQTT_PORT, 60)
            client.loop_forever()
    except Exception as e:
        print('exception in thread', e)


def start_client(in_background: bool=False):
    if not in_background:
        while True:
            _start_client(in_background)
    else:
        _start_client(in_background)

if __name__ == '__main__':
    start_client(in_background=False)
