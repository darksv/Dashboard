<template>
    <div class="channel-page">
        <loader v-if="loading"></loader>
        <router-view v-else :channel="channel"></router-view>
    </div>
</template>

<script>
    import Loader from '../components/loader.vue';

    export default {
        props: {
            channels: {
                required: true
            },
            channelId: {
                required: true
            }
        },
        data() {
            return {
                loading: false
            }
        },
        computed: {
            channel() {
                let channelId = parseInt(this.channelId);
                return this.channels.find(channel => channel.id === channelId);
            }
        },
        created() {
            if (this.channel === undefined) {
                this.loading = true;
            }
        },
        watch: {
            channel(value) {
                if (value !== undefined) {
                    this.loading = false;
                }
            }
        },
        components: {
            Loader
        }
    };
</script>


<style lang="scss">
    .channel-page {
        display: flex;
        justify-content: center;
    }
</style>