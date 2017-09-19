class SocketClient {
    constructor(url, app) {
        this._handlers = {};
        let self = this,
            socket = new WebSocket(url);
        socket.onopen = e => app.connected = true;
        socket.onclose = e => app.connected = false;
        socket.onerror = e => console.log(e);
        socket.onmessage = e => {
            let message = JSON.parse(e.data),
                name = message[0],
                data = message[1];

            if (name in self._handlers) {
                for (let handler of self._handlers[name]) {
                    handler(data);
                }
            } else {
               console.log('unhandled', name);
            }
        };
        this._socket = socket;
    }
    addEventListener(event, handler) {
        if (!(event in this._handlers)) {
            this._handlers[event] = [];
        }
        this._handlers[event].push(handler);
    }
    removeEventListener(event, handler) {
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