<template>
    <canvas></canvas>
</template>

<script>
    import Chart from 'chart.js';
    import { clampArray } from '../utils.js';

    export default {
        props: {
            channel: {
                required: true,
                type: Object
            },
            color: {
                required: false,
                type: String,
                default: '#ffffff'
            },
            maxPoints: {
                required: false,
                type: Number,
                default: 0
            }
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
                                lineTension: 0,
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
                        responsive: false,
                        maintainAspectRatio: false,
                        tooltips: {
                            enabled: false
                        },
                        hover: {
                            mode: null
                        },
                        legend: {
                            display: false
                        },
                        scales: {
                            yAxes: [{
                                display: false
                            }],
                            xAxes: [{
                                display: false
                            }],
                        },
                        title: {
                            display: false
                        }
                    }
                };
            },
            labels: function() {
                return clampArray(this.channel.items, this.maxPoints).map(function(x) {
                    return x[0];
                });
            },
            values: function() {
                return clampArray(this.channel.items, this.maxPoints).map(function(x) {
                    return x[1];
                });
            }
        },
        watch: {
            config: function(config) {
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