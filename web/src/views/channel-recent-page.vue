<template>
    <chart :responsive="true" :points="channel.items" :title="channel.name" :yTitle="yTitle" color="rgba(255, 255, 255, 0.75)" :unit="channel.unit" :maxPoints="60" ></chart>
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
        computed: {
            yTitle() {
                let channel = this.channel,
                    title = channel.title,
                    unit = channel.unit;

                return title && unit
                    ? title + ' [' + unit + ']'
                    : title;
            }
        },
        components: {
            Chart,
            Loader
        }
    }
</script>