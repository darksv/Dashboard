<template>
    <div class="main">
        <transition name="fade" mode="out-in" class="page-content">
            <router-view class="view" :channels="channels" :user="user"></router-view>
        </transition>
        <footer>
            <span v-if="connected" class="fa fa-check-circle text-success" title="Connected with server"></span>
            <span v-if="!connected" class="fa fa-times-circle text-danger" title="Not connected"></span>
            <a v-if="isLogged" href="/logout">
                <span class="fa fa-user text-success" :title="'Logged as ' + user.name"></span>
            </a>
            <a v-if="!isLogged" href="/login">
                <span class="fa fa-user text-danger" title="Not logged in"></span>
            </a>
        </footer>
    </div>
</template>

<script>
    import mqtt from 'mqtt';
    import { client as ApiClient } from './api-client.js';
    import guid from './guid';

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
                connected: false,
                channels: [],
                user: {}
            };
        },
        beforeCreate: function () {
            var self = this;
            var client = new mqtt.connect('wss://' + window.location.host + ':9883/ws', {
                clientId: guid.generate()
            });

            client.on('connect', function () {
                client.subscribe('+/+');
                client.subscribe('+/+/log');
                client.subscribe('notify/+');
                self.connected = true;
            });

            client.on('message', function (topic, message) {
                try {
                    var payload = message.toString(),
                        channelUuid = topic.split('/')[1],
                        channel = self.channels.find(function(channel) {
                            return channelUuid === channel.uuid;
                        });

                    if (channel === undefined) {
                        return;
                    }

                    if (topic.endsWith('/log')) {
                        var data = JSON.parse(payload),
                            label = new Date(data.timestamp).toHourMinute();

                        channel.items.push([label, data.value]);
                        return;
                    }

                    var newValue = parseFloat(payload);
                    // temporary fix for invalid negative values
                    if (newValue > 4000) {
                        newValue -= 4096;
                    }

                    var oldValue = channel.value;
                    channel.value = newValue;
                    channel.value_updated = new Date().toISOString();
                    channel.change = Math.sign(newValue - oldValue);
                } catch(e) {
                    console.error(e);
                }
            });

            client.on('close', function () {
                self.connected = false;
            });
        },
        created: function() {
            var self = this;
            ApiClient.get('channels').then(function (response) {
                self.channels = response.data.channels.map(function(channel) {
                    channel.items = [];
                    if (channel.enabled && channel.logging_enabled) {
                        ApiClient.get('/channel/' + channel.id + '/stats?type=recent').then(function (response) {
                            channel.items = response.data.values.map(function (x, i) {
                                return [response.data.labels[i], x];
                            });
                        });
                    }
                    return channel;
                });
            });
            ApiClient.get('session').then(function (response) {
               self.user = response.data.user;
            });
        },
    };
</script>

<style lang="scss">
    .main {
        display: flex;
        flex-direction: column;

    & > footer {
        flex: 0 1;
        text-align: center;
        display: block;
        width: 100%;
        bottom: 0;
        padding: 0;
        margin: 0 0 0.25em 0;
    }
}
</style>