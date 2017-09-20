<template>
    <div class="main">
        <transition name="fade" mode="out-in" class="page-content">
            <router-view class="view" :channels="channels" :user="user" :client="client"></router-view>
        </transition>
    </div>
</template>

<script>
    import { client as ApiClient } from './api-client.js';
    import SocketClient from './socket-client.js';
    import guid from './guid';
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
        computed: {
            isLogged: function() {
                return this.user.name !== undefined;
            }
        },
        data: function() {
            return {
                connected: null,
                channels: [],
                user: {},
                client: new SocketClient('wss://' + window.location.host + '/ws', this),
                originalTitle: ''
            };
        },
        watch: {
            connected(newValue, oldValue) {
                console.log(newValue, oldValue);
                if (oldValue === null) {
                    return;
                }

                if (!newValue) {
                    this.originalTitle = document.title;
                    document.title = '[Offline] ' + this.originalTitle;
                } else {
                    document.title = this.originalTitle;
                }
            }
        },
        created: function() {
            let app = this;

            app.client.addEventListener('channel_updated', data => {
                let channel = app.getChannelByUuid(data.channel_uuid);
                if (channel === undefined) {
                    return;
                }
                let newValue = data.value;
                let oldValue = channel.value;
                channel.value = newValue;
                channel.value_updated = data.timestamp;
                channel.change = Math.sign(newValue - oldValue);
            });

            app.client.addEventListener('channel_logged', data => {
                let channel = app.getChannelByUuid(data.channel_uuid);
                if (channel === undefined) {
                    return;
                }
                let label = new Date(data.timestamp).toHourMinute();
                channel.items.push([label, data.value]);
            });

            function hasStats(channel) {
                if (!channel.enabled || !channel.logging_enabled) {
                    return false;
                }
                return true;
                // TODO: make some changes to make use of it
                return (Date.now() - Date.parse(channel.value_updated)) / 1000 <= 60 * 30;
            }

            function loadStatsWhenPossible(channel) {
                channel.items = [];
                if (hasStats(channel)) {
                    let endpoint = '/channel/' + channel.id + '/stats?type=recent';
                    ApiClient.get(endpoint).then(response => {
                        let data = response.data,
                            labels = data.labels,
                            values = data.values;
                        channel.items = zip(labels, values);
                    });
                }
                return channel;
            }

            ApiClient.get('channels').then(response => app.channels = response.data.channels.map(loadStatsWhenPossible));
        },
        methods: {
            getChannelByUuid(uuid) {
                return this.channels.find(channel => uuid === channel.uuid);
            }
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