<template>
    <div :style="{ color: d, background: c, height: '100%', margin: '2em'}">
        <hue-ring :size="200" :hue.sync="h"></hue-ring>
        <hue-ring :size="100" :hue.sync="h"></hue-ring>
        <hue-ring :size="50" :hue.sync="h"></hue-ring>
        <hue-slider :hue.sync="h"></hue-slider>
        <color-palette :hue.sync="h" :saturation.sync="s" :value.sync="v"></color-palette>
        <schedule-editor hourFormat="24h" :selection.sync="selection"></schedule-editor>
        <schedule-editor hourFormat="12h" :selection.sync="selection"></schedule-editor>
        <schedule-editor hourFormat="24h" :selection.sync="selection"></schedule-editor>
        <schedule-editor hourFormat="12h" :selection.sync="selection"></schedule-editor>
        <schedule-editor hourFormat="12h" :selection.sync="selection"></schedule-editor>
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
            this._lastUpdate = 0;
            let self = this;
            this._listener = data => {
                if (data.timestamp > self._lastUpdate) {
                    updater(data.value);
                }
            };
        }
        change(value) {
            let timestamp = Date.now();
            this._client.send(this._eventName, {
                value: value,
                timestamp: timestamp
            });
            this._lastUpdate = timestamp;
        }
        attach() {
            this._client.addEventListener(this._eventName, this._listener);
        }
        detach() {
            this._client.removeEventListener(this._eventName, this._listener);
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
        computed: {
            c() {
                return tinycolor({h: this.h, s: this.s, v: this.v}).toRgbString();
            },
            d() {
                return tinycolor({h: this.h, s: this.s, v: this.v}).isDark() ? '#ffffff' : '#000000';
            }
        },
        created() {
            this.synchronizer = new Synchronizer(this.client, 'hue', hue => this.h = hue);
            this.synchronizer.attach();
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