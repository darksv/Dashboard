<template>
    <div class="chart-container">
        <chart :points="points" :title="title" :yTitle="yTitle" :color="color" :unit="unit" :maxPoints="60" ></chart>
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
                points: []
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
                this.points = this.channel.items;
            }
        }
    }
</script>