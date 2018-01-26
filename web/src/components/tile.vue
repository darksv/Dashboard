<template>
    <div class="channel-tile" :title="channel.name" :style="{ backgroundColor: backColor, color: fontColor }">
        <chart v-if="hasValues" class="chart" :color="fontColor" :sets="sets" :xAxisDisplay="false"
               :yAxisDisplay="false" :maxPoints="60"/>
        <loader v-if="!ready" :color="fontColor"/>
        <span v-if="ready && !hasValues" class="status fa fa-exclamation-triangle"></span>
        <span v-if="ready && hasValues" class="value" :data-unit="channel.unit"
              :title="channel.value_updated">{{ channel.value.toFixed(2) }}</span>
    </div>
</template>

<script lang="ts">
    import Chart from './chart.vue';
    import Loader from './loader.vue';
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
            backColor() {
                return this.channel.color || '#000000';
            },
            fontColor() {
                return tinycolor(this.backColor).isDark() ? '#FFFFFF' : '#000000';
            },
            hasValues() {
                return this.channel.items.filter(i => i[1] !== null).length > 0;
            },
            ready() {
                return this.channel.items.length !== 0;
            },
            sets() {
                return [{
                    labels: this.channel.items.map(([label,]) => label),
                    values: this.channel.items.map(([,value]) => value),
                    color: this.fontColor
                }];
            }
        },
        components: {
            Chart: Chart,
            Loader: Loader
        }
    }
</script>

<style lang="scss">
    .channel-tile {
        position: relative;
        width: 340px;
        height: 170px;
        margin: 0.5em 0.5em;
        display: flex;
        align-items: center;
        justify-items: center;
        flex-direction: column;
        justify-content: center;
        cursor: default;

        &:hover {
            .action, .indicator, .value {
                display: none;
            }

            .chart {
                display: block !important;
            }
        }

        .chart {
            z-index: 1;
            position: absolute;
            top: 0;
            left: 0;
            width: 340px;
            height: 170px;
            padding: 1em;
            box-sizing: border-box;
            display: none !important;
            cursor: pointer;
        }

        .loader {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            box-sizing: border-box;
        }

        .status {
            z-index: 1;
            position: absolute;
            top: 0;
            left: 0;
            width: 340px;
            height: 170px;
            padding: 1em;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        a {
            text-decoration: none;
            color: inherit;
        }

        span {
            font-size: 3em;
            color: inherit;
        }

        .action {
            display: none;
        }

        .value:after {
            content: attr(data-unit);
            margin-left: 5px;
            font-size: 0.75em;
        }
    }
</style>