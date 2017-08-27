<template>
    <div class="chart-container">
        <chart v-if="!isLoading" :responsive="true" :points="points" :title="title" :yTitle="yTitle" color="rgba(255, 255, 255, 0.75)" :unit="unit" :maxPoints="60" ></chart>
        <loader v-if="isLoading"></loader>
    </div>
</template>

<script>
    import Chart from '../components/chart.vue';
    import Loader from '../components/loader.vue';
    import { client as ApiClient } from '../api-client.js';

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
                points: [],
                isLoading: true
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
            Chart: Chart,
            Loader: Loader
        },
        mounted: function () {
            this.update();
        },
        methods: {
            update: function () {
                if (!this.channel) {
                    this.isLoading = true;
                    return;
                }
                this.isLoading = false;
                this.title = this.channel.name;
                this.color = this.channel.color;
                this.unit = this.channel.unit;
                this.points = this.channel.items;
            }
        }
    }
</script>