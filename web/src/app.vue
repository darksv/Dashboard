<template>
    <div class="main">
        <loader v-if="isLoading"></loader>
        <transition v-else name="fade" mode="out-in" class="page-content">
            <router-view class="view" :channels="channels" :user="user" :client="client"></router-view>
        </transition>
    </div>
</template>

<script>
    import { client as ApiClient } from './api-client.js';
    import SocketClient from './socket-client.js';
    import Loader from './components/loader.vue';
    import { zip } from './functional';

    String.prototype.zfill = function(width) {
        if (width > this.length) {
            return new Array(width - this.length + 1).join('0') + this;
        }
        return this;
    };

    Number.prototype.zfill = function(width) {
        return this.toString().zfill(width);
    };

    Date.prototype.addDays = function(n) {
        return new Date(this.getTime() + n * 24 * 3600 * 1000);
    };

    Date.prototype.toHourMinute = function() {
        return this.getHours().zfill(2) + ':' + this.getMinutes().zfill(2);
    };

    Array.prototype.last = function() {
        return this[this.length - 1];
    };

    export default {
        data() {
            return {
                connected: null,
                channels: [],
                user: {},
                client: new SocketClient('wss://' + window.location.host + '/ws', this),
                originalTitle: document.title,
                isLoading: true
            };
        },
        watch: {
            connected(newValue) {
                let prefix = newValue === true ? '' : '[Offline] ';
                document.title = prefix + this.originalTitle;

                if (newValue === true) {
                    // Update after initiated/recovered connection
                    this.updateChannels();
                }
            }
        },
        created() {
            this.client.on('channel_updated', data => {
                let channel = this.getChannelByUuid(data.channel_uuid);
                if (channel === undefined) {
                    return;
                }
                let newValue = data.value,
                    oldValue = channel.value;
                channel.value = newValue;
                channel.value_updated = data.timestamp;
                channel.change = Math.sign(newValue - oldValue);
            });

            this.client.on('channel_logged', data => {
                let channel = this.getChannelByUuid(data.channel_uuid);
                if (channel === undefined) {
                    return;
                }
                let label = new Date(data.timestamp).toHourMinute();
                if (label !== channel.items.last()) {
                    channel.items.push([label, data.value]);
                }
            });
        },
        methods: {
            getChannelByUuid(uuid) {
                return this.channels.find(channel => uuid === channel.uuid);
            },
            updateChannels() {
                function hasStats(channel) {
                    return channel.enabled && channel.logging_enabled;
                }

                function loadStatsWhenPossible(channel) {
                    channel.items = [];
                    if (hasStats(channel)) {
                        let endpoint = '/channel/' + channel.id + '/stats',
                            options = {
                                params: {
                                    average: 1
                                }
                            };
                        ApiClient.get(endpoint, options).then(response => {
                            let data = response.data,
                                labels = data.labels,
                                values = data.values;
                            channel.items = zip(labels, values);
                        });
                    }
                    return channel;
                }
                this.isLoading = true;
                ApiClient.get('channels').then(response => {
                    this.isLoading = false;
                    this.channels = response.data.channels.map(loadStatsWhenPossible);
                });
            }
        },
        components: {
            Loader
        }
    };
</script>

<style lang="scss">
    .main {
        min-height: 100%;
        display: flex;
        justify-content: center;
    }

    .view {
        flex: 1;
    }
</style>