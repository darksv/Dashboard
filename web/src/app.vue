<template>
    <div class="main">
        <loader v-if="isLoading"/>
        <transition v-else name="fade" mode="out-in" class="page-content">
            <router-view class="view" :channels="channels" :user="user" :client="client"></router-view>
        </transition>
    </div>
</template>

<script lang="ts">
    import {client as ApiClient} from './api-client.ts';
    import SocketClient from './socket-client.ts';
    import Loader from './components/loader.vue';
    import {zip} from './functional.ts';

    function zfill(string: string, width: number): string {
        if (width > string.length) {
            return new Array(width - string.length + 1).join('0') + string;
        }
        return string;
    }

    function toHourMinute(date: Date): string {
        return zfill(date.getHours().toString(), 2) + ':' + zfill(date.getMinutes().toString(), 2);
    }

    export default {
        data: function () {
            return {
                connected: null,
                channels: [],
                user: {},
                client: new SocketClient(
                    'wss://' + window.location.host + '/ws',
                    connected => this.connected = connected
                ),
                originalTitle: document.title,
                isLoading: true
            };
        },
        watch: {
            connected(newValue: boolean) {
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
                channel.value = data.value;
                channel.value_updated = data.timestamp;
            });

            this.client.on('channel_logged', data => {
                let channel = this.getChannelByUuid(data.channel_uuid);
                if (channel === undefined) {
                    return;
                }
                let label = toHourMinute(new Date(data.timestamp));
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