<template>
    <canvas></canvas>
</template>

<script>
    import Chart from 'chart.js';
    import tinycolor from 'tinycolor2';
    import {clampArray} from '../utils.js';

    Chart.defaults.global.defaultFontColor = 'rgba(255, 255, 255, 0.75)';

    export default {
        props: {
            sets: {
                required: false,
                type: Array
            },
            points: {
                required: false,
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
            },
            displayLegend: {
                required: false,
                type: Boolean,
                default: false
            }
        },
        data() {
            return {
                chart: null
            };
        },
        computed: {
            config() {
                let datasets = [];
                let labels = [];
                for (let set of this.sets) {
                    datasets.push({
                        fill: false,
                        lineTension: 0.3,
                        pointRadius: 0,
                        data: set.values,
                        borderWidth: 2.5,
                        borderColor: set.color,
                        label: set.title
                    });

                    labels = set.labels;
                }

                return {
                    type: 'line',
                    data: {
                        labels,
                        datasets
                    },
                    options: {
                        animation: false,
                        responsive: this.responsive,
                        maintainAspectRatio: false,
                        legend: {
                            display: this.displayLegend,
                            onClick() {

                            }
                        },
                        scales: {
                            xAxes: [{
                                display: this.xAxisDisplay,
                                scaleLabel: {
                                    display: !!this.xTitle,
                                    labelString: this.xTitle
                                },
                                gridLines: {
                                    color: 'white',
                                    lineWidth: 0.5,
                                    borderDash: [2, 5],
                                },
                            }],
                            yAxes: [{
                                display: this.yAxisDisplay,
                                scaleLabel: {
                                    display: !!this.yTitle,
                                    labelString: this.yTitle
                                },
                                gridLines: {
                                    color: 'white',
                                    lineWidth: 0.5,
                                    borderDash: [2, 5],
                                    zeroLineColor: 'white',
                                    zeroLineWidth: 0.5,
                                },
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
        },
        watch: {
            sets() {
                this.refresh();
            },
            config() {
                this.refresh();
            }
        },
        methods: {
            refresh() {
                this.chart.config.data = this.config.data;
                this.chart.config.options = this.config.options;
                this.chart.update();
            }
        },
        mounted() {
            this.chart = new Chart(this.$el, this.config);
        }
    };
</script>