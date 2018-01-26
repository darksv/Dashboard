<template>
    <div style="display: flex; justify-content: center; align-items: center">
        <hue-ring :size="200" :hue.sync="h"/>
    </div>
</template>

<script lang="ts">
    import HueSlider from '../components/hue-slider.vue';
    import ColorPalette from '../components/color-palette.vue';
    import ScheduleEditor from '../components/schedule-editor.vue';
    import HueRing from '../components/hue-ring.vue';
    import {SocketClient, WebSocketClient} from "../socket-client.ts";
    import {hsvToRgb} from '../colors.ts';

    class Synchronizer<TValue> {
        private client: SocketClient;
        private eventName: string;
        private delayedSendHandle?: number;
        private listener: (object) => void;
        private isLocal: boolean;

        constructor(client: SocketClient, eventName: string, updater: (TValue) => any) {
            this.client = client;
            this.eventName = eventName;
            this.delayedSendHandle = null;
            // By default all changes are local
            // unless it is changed by reception
            // of changes from remote server.
            this.isLocal = true;
            this.listener = data => {
                this.isLocal = false;
                updater(data.value);
            };
            this.attach();
        }

        change(value: TValue) {
            if (this.isLocal) {
                this.sendWithDelay(value, 10);
            }
            this.isLocal = true;
        }

        private sendWithDelay(value: TValue, delay: number) {
            if (this.delayedSendHandle !== null) {
                clearTimeout(this.delayedSendHandle);
            }
            this.delayedSendHandle = setTimeout((self, data) => self.sender(data), delay, this, {
                value,
                timestamp: Date.now()
            });
        }

        private sender(data: any) {
            this.client.send(this.eventName, data);
        }

        attach() {
            this.client.on(this.eventName, this.listener);
        }

        detach() {
            this.client.off(this.eventName, this.listener);
        }
    }

    export default {
        props: {
            client: {
                required: true
            }
        },
        data: function () {
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
                this.updateHue();
            }
        },
        created() {
            this.synchronizer = new Synchronizer<number>(this.client, 'hue', hue => this.h = hue);
            this.updateHue();
        },
        destroyed() {
            this.synchronizer.detach();
        },
        components: {
            HueSlider,
            ColorPalette,
            ScheduleEditor,
            HueRing
        },
        methods: {
            updateHue() {
                const rgb = hsvToRgb(this.h, 100, 100)
                    .map(x => Math.floor(x).toString())
                    .join(', ');
                const element = <HTMLElement> document.querySelector('.main');
                element.style.backgroundColor = 'rgb(' + rgb + ')';
            }
        }
    }
</script>