<template>
    <canvas></canvas>
</template>

<script>
    import Chart from 'chart.js';
    import tinycolor from 'tinycolor2';
    import { clampArray } from '../utils.js';

    Chart.defaults.global.defaultFontColor = 'rgba(255, 255, 255, 0.75)';

    export default {
        props: {
            points: {
                required: true,
                type: Array
            },
            title: {
                required: false,
                type: String,
                default: ''
            },
            xTitle: {
                required: false,
                type: String,
                default: ''
            },
            xAxisDisplay: {
                required: false,
                type: Boolean,
                default: true
            },
            yTitle: {
                required: false,
                type: String,
                default: ''
            },
            yAxisDisplay: {
                required: false,
                type: Boolean,
                default: true
            },
            maxPoints: {
                required: false,
                type: Number,
                default: 0
            },
            color: {
                required: false,
                type: String,
                default: '#ffffff'
            },
            responsive: {
                required: false,
                type: Boolean,
                default: false
            }
        },
        data: function() {
            return {
                chart: null
            };
        },
        computed: {
            config: function () {
                return {
                    type: 'line',
                    data: {
                        labels: this.labels,
                        datasets: [
                            {
                                fill: false,
                                lineTension: 0.3,
                                pointRadius: 0,
                                data: this.values,
                                borderWidth: 2.5,
                                borderColor: this.color,
                                label: ''
                            }
                        ]
                    },
                    options: {
                        animation: false,
                        responsive: this.responsive,
                        maintainAspectRatio: false,
                        legend: {
                            display: false
                        },
                        scales: {
                            xAxes: [{
                                display: this.xAxisDisplay,
                                scaleLabel: {
                                    display: !!this.xTitle,
                                    labelString: this.xTitle
                                }
                            }],
                            yAxes: [{
                                display: this.yAxisDisplay,
                                scaleLabel: {
                                    display: !!this.yTitle,
                                    labelString: this.yTitle
                                }
                            }]
                        },
                        title: {
                            display: !!this.title,
                            text: this.title,
                            fontSize: 24,
                            padding: 8
                        }
                    }
                };
            },
            labels: function() {
                return clampArray(this.points, this.maxPoints).map(function(point) {
                    return point[0];
                });
            },
            values: function() {
                return clampArray(this.points, this.maxPoints).map(function(point) {
                    return point[1];
                });
            }
        },
        watch: {
            config: function (config) {
                this.chart.config.data = config.data;
                this.chart.config.options = config.options;
                this.chart.update();
            }
        },
        mounted: function () {
            this.chart = new Chart(this.$el, this.config);
        }
    };
</script>