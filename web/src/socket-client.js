class SocketClient {
    constructor(url, app) {
        let self = this;
        this._url = url;
        this._handlers = {};
        this._onConnected = () => app.connected = true;
        this._onDisconnected = () => {
            app.connected = false;
            setTimeout(() => self._reconnect(), 1000);
        };
        this._reconnect();
    }

    _reconnect() {
        try {
            this._connect();
        } catch (e) {
            this._onDisconnected();
            console.error(e);
        }
    }

    _connect() {
        let self = this,
            socket = new WebSocket(this._url);

        socket.on('open', e => self._onConnected());
        socket.on('close', e => self._onDisconnected());
        socket.on('error', e => console.error(e));
        socket.on('message', e => {
            let message = JSON.parse(e.data),
                name = message[0],
                data = message[1];

            if (name in self._handlers) {
                for (let handler of self._handlers[name]) {
                    handler(data);
                }
            } else {
               console.warn('unhandled', name);
            }
        });
        this._socket = socket;
    }

    on(event, handler) {
        if (!(event in this._handlers)) {
            this._handlers[event] = [];
        }
        this._handlers[event].push(handler);
    }

    off(event, handler) {
        if (!(event in this._handlers)) {
            return;
        }
        let handlers = this._handlers[event],
            index = handlers.indexOf(handler);
        this._handlers[event] = handlers.splice(index, 1);
    }

    send(action, data) {
        this._socket.send(JSON.stringify([action, data]));
    }
}

export default SocketClient;