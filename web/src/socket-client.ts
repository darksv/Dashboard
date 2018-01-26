class SocketClient {
    private url: string;
    private handlers: object = {};
    private socket: WebSocket;
    private onConnectionChanged: (boolean) => void;

    constructor(url, onConnectionChanged: (boolean) => void) {
        this.url = url;
        this.onConnectionChanged = onConnectionChanged;
        this.reconnect();
    }

    private onConnected() {
        this.onConnectionChanged(true);
    }

    private onDisconnected() {
        this.onConnectionChanged(false);
        setTimeout(() => this.reconnect(), 1000);
    }

    private reconnect() {
        try {
            this.connect();
        } catch (e) {
            this.onDisconnected();
            console.error(e);
        }
    }

    private connect() {
        let socket = new WebSocket(this.url);
        socket.addEventListener('open', () => this.onConnected());
        socket.addEventListener('close', () => this.onDisconnected());
        socket.addEventListener('error', e => console.error(e));
        socket.addEventListener('message', e => {
            let message = JSON.parse(e.data),
                name = message[0],
                data = message[1];

            if (name in this.handlers) {
                for (let handler of this.handlers[name]) {
                    handler(data);
                }
            } else {
                console.warn('unhandled', name);
            }
        });
        this.socket = socket;
    }

    on(event, handler) {
        if (!(event in this.handlers)) {
            this.handlers[event] = [];
        }
        this.handlers[event].push(handler);
    }

    off(event, handler) {
        if (!(event in this.handlers)) {
            return;
        }
        let handlers = this.handlers[event],
            index = handlers.indexOf(handler);
        this.handlers[event] = handlers.splice(index, 1);
    }

    send(action, data) {
        this.socket.send(JSON.stringify([action, data]));
    }
}

export default SocketClient;