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
            labels: {
                required: true,
                type: Array
            },
            values: {
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
                        labels: clampArray(this.labels, this.maxPoints),
                        datasets: [
                            {
                                fill: false,
                                lineTension: 0.3,
                                pointRadius: 0,
                                data: clampArray(this.values, this.maxPoints),
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