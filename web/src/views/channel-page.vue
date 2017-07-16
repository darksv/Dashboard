<template>
    <router-view :channel="channel"></router-view>
</template>

<script>
    export default {
        props: {
            channels: {
                required: true
            },
            channelId: {
                required: true
            }
        },
        computed: {
            channel: function() {
                var channelId = parseInt(this.channelId);
                return this.channels.find(function (channel) {
                    return channel.id === channelId;
                })
            }
        }
    };
</script>