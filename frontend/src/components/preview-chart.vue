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
        watch: {
            'channel.items': function () {
                var items = clampArray(this.channel.items, this.maxPoints);

                this.chart.data.datasets[0].data = items.map(function(x) {
                    return x[1];
                });

                this.chart.data.labels = items.map(function(x) {
                    return x[0];
                });

                this.chart.update();
            },
            color: function () {
                this.chart.data.datasets[0].borderColor = this.color;
                this.chart.update();
            }
        },
        mounted: function () {
            this.chart = new Chart(this.$el, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            fill: false,
                            lineTension: 0,
                            pointRadius: 0,
                            borderColor: this.color,
                            data: this.values,
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
                        xAxes: [{
                            display: false
                        }],
                        yAxes: [{
                            display: false
                        }]
                    },
                    title: {
                        display: false
                    }
                }
            });
        }
    };
</script>