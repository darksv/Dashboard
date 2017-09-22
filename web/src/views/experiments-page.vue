<template>
    <div style="height: 100%; margin: 2em">
        <hue-ring :size="200" :hue.sync="h"></hue-ring>
        <hue-ring :size="100" :hue.sync="h"></hue-ring>
        <hue-ring :size="50" :hue.sync="h"></hue-ring>
        <hue-slider :hue.sync="h"></hue-slider>
    </div>
</template>

<script>
    import tinycolor from 'tinycolor2';
    import HueSlider from '../components/hue-slider.vue';
    import ColorPalette from '../components/color-palette.vue';
    import ScheduleEditor from '../components/schedule-editor.vue';
    import HueRing from '../components/hue-ring.vue';
    import SocketClient from "../socket-client";

    class Synchronizer {
        constructor(client, eventName, updater) {
            this._client = client;
            this._eventName = eventName;
            this._delayedSendHandle = -1;
            // By default all changes are local
            // unless it is changed by reception
            // of changes from remote server.
            this._isLocal = true;
            let self = this;
            this._listener = data => {
                self._isLocal = false;
                updater(data.value);
            };
            this.attach();
        }
        change(value) {
            if (this._isLocal) {
                this._sendWithDelay(value, 10);
            }
            this._isLocal = true;
        }
        _sendWithDelay(value, delay) {
            if (this._delayedSendHandle !== null) {
                clearTimeout(this._delayedSendHandle);
            }
            this._delayedSendHandle = setTimeout((self, data) => self._sender(data), delay, this, {
                value,
                timestamp: Date.now()
            });
        }
        _sender(data) {
            this._client.send(this._eventName, data);
        }
        attach() {
            this._client.addEventListener(this._eventName, this._listener);
        }
        detach() {
            this._client.off(this._eventName, this._listener);
        }
    }

    export default {
        props: {
            client: {
                required: true,
                type: SocketClient
            }
        },
        data: function() {
            return {
                h: 0x90,
                s: 0x00,
                v: 0x30,
                selection: {},
                synchronizer: null
            }
        },
        watch: {
            h(value) {
                this.synchronizer.change(value);
            }
        },
        created() {
            this.synchronizer = new Synchronizer(this.client, 'hue', hue => this.h = hue);
        },
        destroyed() {
            this.synchronizer.detach();
        },
        components: {
            HueSlider,
            ColorPalette,
            ScheduleEditor,
            HueRing
        }
    }
</script>