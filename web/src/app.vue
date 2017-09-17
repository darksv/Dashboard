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

    function createSocket(app) {
        try {
            let socket = new WebSocket('wss://' + window.location.host + '/ws');
            socket.onopen = e => app.connected = true;
            socket.onclose = e => app.connected = false;
            socket.onerror = e => console.log(e);
            socket.onmessage = e => {
                let message = JSON.parse(e.data),
                    name = message[0],
                    data = message[1];

                switch (name) {
                    case 'channel_updated':
                    {
                        let channel = app.getChannelByUuid(data.channel_uuid);
                        if (channel === undefined) {
                            return;
                        }
                        let newValue = data.value;
                        let oldValue = channel.value;
                        channel.value = newValue;
                        channel.value_updated = data.timestamp;
                        channel.change = Math.sign(newValue - oldValue);
                        break;
                    }
                    case 'channel_logged':
                    {
                        let channel = app.getChannelByUuid(data.channel_uuid);
                        if (channel === undefined) {
                            return;
                        }
                        let label = new Date(data.timestamp).toHourMinute();
                        channel.items.push([label, data.value]);
                    }
                }
            };
        } catch(e) {
            console.log(e);
        }
    }

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
            createSocket(this);
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
        methods: {
            getChannelByUuid(uuid) {
                return this.channels.find(channel => uuid === channel.uuid);
            }
        }
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