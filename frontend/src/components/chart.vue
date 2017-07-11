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
                required: true,
                type: String
            },
            xTitle: {
                required: false,
                type: String,
                default: ''
            },
            yTitle: {
                required: false,
                type: String,
                default: ''
            },
            maxPoints: {
                required: false,
                type: Number,
                default: 0
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
                                borderColor: '#ffffff',
                                label: ''
                            }
                        ]
                    },
                    options: {
                        animation: false,
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false
                        },
                        scales: {
                            xAxes: [{
                                scaleLabel: {
                                    display: !!this.xTitle,
                                    labelString: this.xTitle
                                }
                            }],
                            yAxes: [{
                                scaleLabel: {
                                    display: !!this.yTitle,
                                    labelString: this.yTitle
                                }
                            }]
                        },
                        title: {
                            display: true,
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