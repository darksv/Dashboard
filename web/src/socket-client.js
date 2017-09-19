class SocketClient {
    constructor(url, app) {
        let socket = new WebSocket(url);
        socket.onopen = e => app.connected = true;
        socket.onclose = e => app.connected = false;
        socket.onerror = e => console.log(e);
        socket.onmessage = e => {
            let message = JSON.parse(e.data),
                name = message[0],
                data = message[1];

            switch (name) {
                case 'channel_updated':
                {
                    let channel = app.getChannelByUuid(data.channel_uuid);
                    if (channel === undefined) {
                        return;
                    }
                    let newValue = data.value;
                    let oldValue = channel.value;
                    channel.value = newValue;
                    channel.value_updated = data.timestamp;
                    channel.change = Math.sign(newValue - oldValue);
                    break;
                }
                case 'channel_logged':
                {
                    let channel = app.getChannelByUuid(data.channel_uuid);
                    if (channel === undefined) {
                        return;
                    }
                    let label = new Date(data.timestamp).toHourMinute();
                    channel.items.push([label, data.value]);
                }
            }
        };
        this._socket = socket;
    }
    send(action, data) {
        this._socket.send(JSON.stringify([action, data]));
    }
}

export default SocketClient;