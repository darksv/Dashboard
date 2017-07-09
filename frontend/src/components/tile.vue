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

<style lang="scss">
    .tile-container {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        flex-flow: row wrap;
        align-content: center;
        justify-content: center;
        user-select: none;
    }

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

        .sorting-enabled & {
            cursor: move !important;
        }

        .sorting-disabled & {
            &:hover {
                .action, .indicator, .value{
                    display: none
                }

                .minichart {
                    display: block !important;
                }
            }
        }
    }
</style>