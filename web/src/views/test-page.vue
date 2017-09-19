<template>
    <div :style="{ color: d, background: c, height: '100%', margin: '2em'}">
        <hue-ring :size="200" :hue.sync="h"></hue-ring>
        <hue-ring :size="200" :hue.sync="h"></hue-ring>
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

    export default {
        data: function() {
            return {
                h: 0x90,
                s: 0x00,
                v: 0x30,
                selection: {}
            }
        },
        computed: {
            c: function() {
                return tinycolor({h: this.h, s: this.s, v: this.v}).toRgbString();
            },
            d: function() {
                var color = tinycolor({h: this.h, s: this.s, v: this.v});
                return color.isDark() ? '#ffffff' : '#000000';
            }
        },
        components: {
            HueSlider,
            ColorPalette,
            ScheduleEditor,
            HueRing
        }
    }
</script>