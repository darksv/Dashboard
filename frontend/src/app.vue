<template>
    <div class="main">
        <transition name="fade" mode="out-in" class="page-content">
            <router-view class="view" :channels="channels" :user="user"></router-view>
        </transition>
        <footer>
            <span v-if="connected" class="fa fa-check-circle text-success" title="Połączony z serwerem"></span>
            <span v-if="!connected" class="fa fa-times-circle text-danger" title="Brak połączenia"></span>
            <a v-if="isLogged" href="/logout">
                <span class="fa fa-user text-success" :title="'Zalogowany jako ' + user.name"></span>
            </a>
            <a v-if="!isLogged" href="/login">
                <span class="fa fa-user text-danger" title="Niezalogowany"></span>
            </a>
        </footer>
    </div>
</template>

<script>
    import mqtt from 'mqtt';
    import ApiClient from './api-client.js';
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
                client.subscribe('notify/+');
                self.connected = true;
            });

            client.on('message', function (topic, message) {
                try {
                    var payload = message.toString();

                    var channelUuid = topic.split('/')[1];
                    var newValue = parseFloat(payload);

                    // temporary fix for invalid negative values
                    if (newValue > 4000) {
                        newValue -= 4096;
                    }

                    var channel = self.channels.find(function(channel) {
                        return channelUuid === channel.uuid;
                    });

                    if (channel !== undefined) {
                        var oldValue = channel.value;
                        channel.value = newValue;
                        channel.value_updated = new Date().toISOString();
                        channel.change = Math.sign(newValue - oldValue);

                        if (self.$route.name === 'channel_recent') {
                            if (parseInt(self.$route.params.channelId) === channel.id) {
                                    var label = new Date().toHourMinute();
                                    var currentView = self.$children[0];
                                    if (currentView !== undefined && currentView.add !== undefined) {
                                        currentView.add(label, newValue, true);
                                    }
                                }
                        }
                    }
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
                    channel.values = [1];
                    ApiClient.get('/channel/' + channel.id + '/stats?type=recent').then(function (response) {
                        channel.values = response.data.values;
                    });
                    return channel;
                });
            });
            ApiClient.get('session').then(function (response) {
               self.user = response.data.user;
            });
        },
    };
</script>