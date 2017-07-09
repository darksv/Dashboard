<template>
    <canvas></canvas>
</template>

<script>
    import Chart from 'chart.js';
    import tinycolor from 'tinycolor2';

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
            color: {
                required: false,
                type: String,
                default: '#ffffff'
            },
            unit: {
                required: true,
                type: String
            },
            maxPoints: {
                required: false,
                type: Number,
                default: 0
            }
        },
        watch: {
            labels: function() {
                if (this.maxPoints > 0 && this.labels.length > this.maxPoints) {
                    this.chart.data.labels = this.labels.slice(this.labels.length - this.maxPoints);
                } else {
                    this.chart.data.labels = this.labels;
                }
                this.chart.update();
            },
            values: function () {
                if (this.maxPoints > 0 && this.values.length > this.maxPoints) {
                    this.chart.data.datasets[0].data = this.values.slice(this.values.length - this.maxPoints);
                } else {
                    this.chart.data.datasets[0].data = this.values;
                }
                this.chart.update();
            },
            title: function () {
                this.chart.options.title.text = this.title;
                this.chart.options.scales.yAxes[0].scaleLabel = {
                    display: !!this.title,
                    labelString: this.title + ' [' + this.unit + ']'
                };
                this.chart.update();
            },
            color: function () {
                this.chart.data.datasets[0].borderColor = tinycolor(this.color).setAlpha(0.5);
                this.chart.update();
            },
            unit: function () {
                this.chart.options.scales.yAxes[0].scaleLabel = {
                    display: !!this.title,
                    labelString: this.title + ' [' + this.unit + ']'
                };
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
                            lineTension: 0.3,
                            pointRadius: 0,
                            data: [],
                            borderColor: Color.hexToRgba(this.color, 0.5),
                            borderWidth: 2.5,
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
                        yAxes: [{
                            display: true
                        }]
                    },
                    title: {
                        display: true,
                        text: '',
                        fontSize: 24,
                        padding: 8
                    }
                }
            });
        }
    };
</script>