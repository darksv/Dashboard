<template>
    <canvas></canvas>
</template>

<script>
    import Chart from 'chart.js';

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
            'channel.values': function () {
                var values = this.channel.values,
                    redundantPoints = Math.max(0, values.length - this.maxPoints);
                values = this.maxPoints === 0 ? values : values.splice(redundantPoints);
                this.chart.data.datasets[0].data = values;
                this.chart.data.labels = values.map(function(x, i) { return i; });
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