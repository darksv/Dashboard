<template>
    <div class="channel-tile" :title="channel.name" :style="{ backgroundColor: backColor, color: fontColor, opacity: channel.disabled ? 0.8 : 1}">
        <small-chart class="minichart" v-if="hasValues" :color="fontColor" :channel="channel"></small-chart>
        <span class="status fa fa-exclamation-triangle" v-if="!hasValues"></span>
        <div v-if="hasValues">
            <span v-if="channel.change === 1" class="fa fa-arrow-up indicator"></span>
            <span v-if="channel.change === -1" class="fa fa-arrow-down indicator"></span>
            <span :data-unit="channel.unit" :title="channel.value_updated" class="value">{{ channel.value.toFixed(2) }}</span>
        </div>
    </div>
</template>

<script>
    import SmallChart from './small-chart.vue';
    import Color from '../color.js';

    export default {
        props: {
            channel: {
                required: true
            },
            user: {
                required: true
            }
        },
        computed: {
            online: function () {
                var diff = (Date.now() - Date.parse(this.channel.value_updated));
                return diff <= 5 * 50 * 1000;
            },
            backColor: function() {
                return this.channel.color || '#000000';
            },
            fontColor: function () {
                return Color.contrast(this.backColor);
            },
            hasValues: function() {
                return this.channel.items.filter(function(x) { return x[1] !== null; }).length > 0;
            }
        },
        components: {
            SmallChart: SmallChart
        }
    }
</script>