<template>
    <div class="channel-tile" :title="channel.name" :style="{ backgroundColor: backColor, color: fontColor }">
        <small-chart v-if="hasValues" class="minichart" :color="fontColor" :channel="channel"></small-chart>
        <span v-if="!hasValues" class="status fa fa-exclamation-triangle"></span>
        <span v-if="hasValues" class="value" :data-unit="channel.unit" :title="channel.value_updated">{{ channel.value.toFixed(2) }}</span>
    </div>
</template>

<script>
    import SmallChart from './small-chart.vue';
    import tinycolor from 'tinycolor2';

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
            backColor: function() {
                return this.channel.color || '#000000';
            },
            fontColor: function () {
                return tinycolor(this.backColor).isDark() ? '#FFFFFF' : '#000000';
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