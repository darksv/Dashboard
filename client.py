import json
import math
import traceback
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


def process_watchers(channel_id, value):
    data = requests.get('http://xxx/api/watchers', dict(channel_id=channel_id)).json()
    watchers = data['watchers']
    for watcher in watchers:
        condition = watcher['condition']
        user_id = watcher['user_id']
        message = watcher['message']

        if eval(condition, dict(), dict(value=value)):
            notification = dict(
                title='Ostrzeżenie',
                body=message.replace('value', str(value)),
                url='http://xxx/channel/{0}'.format(channel_id)
            )

            client.publish('notify/{0}'.format(user_id), json.dumps(notification), 2)


def on_message(client, userdata, msg):
    try:
        device_uuid, channel_uuid = msg.topic.split('/')
        value = parse_value(msg.payload.decode('ascii'))

        # quick fix
        if value > 4000:
            value -= 4096

    except Exception as e:
        print(msg.topic, msg.payload, e)
    else:
        print('Received channel update: device={0} channel={1} value={2}'.format(device_uuid, channel_uuid, value))

        try:
            req = requests.get('https://xxx/updateChannel',
                               dict(deviceUuid=device_uuid, channelUuid=channel_uuid, value=value))

            if req.status_code != 200:
                print('Update unsuccessful', req.status_code, req.content)
                return

            channel_id = int(req.content)
            process_watchers(channel_id, value)

        except SystemError as e:
            print('Exception occurred: ', e)


if __name__ == '__main__':
    while True:
        try:
            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(config.MQTT_HOST, config.MQTT_PORT, 60)
            client.loop_forever()
        except Exception as e:
            print(traceback.format_exc())
