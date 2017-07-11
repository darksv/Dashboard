<template>
    <div class="chart-container">
        <chart :labels="labels" :values="values" :title="title" :yTitle="yTitle" :color="color" :unit="unit" :maxPoints="60" ></chart>
    </div>
</template>

<script>
    import Chart from '../components/chart.vue';
    import ApiClient from '../api-client.js';

    export default {
        props: {
            channel: {
                required: true
            }
        },
        watch: {
            channel: {
                deep: true,
                handler: function () {
                    this.update();
                }
            }
        },
        data: function() {
            return {
                title: '',
                color: '#FFFFFF',
                unit: '',
                labels: [],
                values: []
            };
        },
        computed: {
            yTitle: function() {
                return this.title && this.unit
                    ? this.title + ' [' + this.unit + ']'
                    : this.title;
            }
        },
        components: {
            Chart: Chart
        },
        mounted: function () {
            this.update();
        },
        methods: {
            update: function () {
                if (!this.channel) {
                    return;
                }

                this.title = this.channel.name;
                this.color = this.channel.color;
                this.unit = this.channel.unit;
                this.labels = this.channel.items.map(function(item) {
                    return item[0];
                });
                this.values = this.channel.items.map(function(item) {
                    return item[1];
                });
            }
        }
    }
</script>