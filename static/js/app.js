"use strict";

Chart.defaults.global.defaultFontColor = '#ccc';

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

function hexSplit(hex) {
    if (hex[0] === '#') {
        hex = hex.slice(1);
    }

    return [hex.slice(0, 2), hex.slice(2, 4), hex.slice(4, 6)].map(function (x) {
        return parseInt(x, 16);
    });
}

function hexJoin(r, g, b) {
    return '#' + [r, g, b].map(function(x) {
        return (x < 16 ? '0' : '') + x.toString(16);
    }).join('');
}

function hexToRgba(hex, alpha) {
    var rgb = hexSplit(hex);
    return 'rgba(' + rgb.concat([alpha || 1.0]).join(', ') + ')';
}

function contrastColor(color) {
    var c = hexSplit(color);
    // https://stackoverflow.com/questions/1855884/determine-font-color-based-on-background-color
    // Counting the perceptive luminance - human eye favors green color...
    var a = 1 - ( 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255;
    return (a < 0.5) ? '#000000' : '#FFFFFF';
}

function generateGuid() {
    var result = '';
    for (var j = 0; j < 32; j++) {
        if (j in [8, 12, 16, 20])
            result += '-';
        result += Math.floor(Math.random() * 16).toString(16).toUpperCase();
    }
    return result;
}

function isValidDate(str) {
    return !isNaN(Date.parse(str));
}

const apiClient = axios.create({
    baseURL: window.location.origin + '/api',
    headers: {'Authorization': 'Basic '}
});

const ChannelTile = Vue.component('channel-tile', {
    template: '#channel-tile',
    props: {
        channel: {
            required: true
        },
        user: {
            required: true
        }
    },
    computed: {
        online: function () {
            var diff = (Date.now() - Date.parse(this.channel.value_updated));
            return diff <= 5 * 50 * 1000;
        },
        backColor: function() {
            return this.channel.color || '#000000';
        },
        fontColor: function () {
            return contrastColor(this.backColor);
        },
        hasValues: function() {
            return this.channel.values.filter(function(x) { return x !== null; }).length > 0;
        }
    }
});

const ChannelsPage = Vue.component('channels-page', {
    template: '#channels-page',
    props: {
        channels: {
            required: true,
            type: Array
        },
        user: {
            required: true
        }
    },
    data: function() {
        return {
            enableSort: false,
            showDisabled: false
        }
    },
    watch: {
        channels: function (items) {
            if (!this.enableSort) {
                return;
            }

            var newOrder = items.map(function (x) {
                return x.id;
            });

            apiClient.post('/order?order=' + newOrder.join(','));
        }
    }
});

const MySmallChart = Vue.component('small-chart', {
    template: '<canvas></canvas>',
    props: {
        channel: {
            required: true,
            type: Object
        },
        color: {
            required: false,
            type: String,
            default: '#ffffff'
        },
        maxPoints: {
            required: false,
            type: Number,
            default: 0
        }
    },
    watch: {
        'channel.values': function () {
            var values = [];
            if (this.maxPoints > 0 && this.channel.values.length > this.maxPoints) {
                values = this.channel.values.slice(this.channel.values.length - this.maxPoints);
            } else {
                values = this.channel.values;
            }

            this.chart.data.datasets[0].data = values;
            this.chart.data.labels = values.map(function(x, i) { return i; });
            this.chart.update();
        },
        color: function () {
            this.chart.data.datasets[0].borderColor = this.color;
            this.chart.update();
        }
    },
    mounted: function () {
        this.chart = new Chart(this.$el, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        fill: false,
                        lineTension: 0,
                        pointRadius: 0,
                        borderColor: this.color,
                        data: this.values,
                        label: ''
                    }
                ]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    display: false
                },
                scales: {
                    xAxes: [{
                        display: false
                    }],
                    yAxes: [{
                        display: false
                    }]
                },
                title: {
                    display: false
                }
            }
        });
    }
});

const MyChart = Vue.component('chart', {
    template: '<canvas></canvas>',
    props: {
        labels: {
            required: true,
            type: Array
        },
        values: {
            required: true,
            type: Array
        },
        title: {
            required: true,
            type: String
        },
        color: {
            required: false,
            type: String,
            default: '#ffffff'
        },
        unit: {
            required: true,
            type: String
        },
        maxPoints: {
            required: false,
            type: Number,
            default: 0
        }
    },
    watch: {
        labels: function() {
            if (this.maxPoints > 0 && this.labels.length > this.maxPoints) {
                this.chart.data.labels = this.labels.slice(this.labels.length - this.maxPoints);
            } else {
                this.chart.data.labels = this.labels;
            }
            this.chart.update();
        },
        values: function () {
            if (this.maxPoints > 0 && this.values.length > this.maxPoints) {
                this.chart.data.datasets[0].data = this.values.slice(this.values.length - this.maxPoints);
            } else {
                this.chart.data.datasets[0].data = this.values;
            }
            this.chart.update();
        },
        title: function () {
            this.chart.options.title.text = this.title;
            this.chart.options.scales.yAxes[0].scaleLabel = {
                display: !!this.title,
                labelString: this.title + ' [' + this.unit + ']'
            };
            this.chart.update();
        },
        color: function () {
            this.chart.data.datasets[0].borderColor = hexToRgba(this.color, 0.5);
            this.chart.update();
        },
        unit: function () {
            this.chart.options.scales.yAxes[0].scaleLabel = {
                display: !!this.title,
                labelString: this.title + ' [' + this.unit + ']'
            };
            this.chart.update();
        }
    },
    mounted: function () {
        this.chart = new Chart(this.$el, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        fill: false,
                        lineTension: 0.3,
                        pointRadius: 0,
                        data: [],
                        borderColor: hexToRgba(this.color, 0.5),
                        borderWidth: 2.5,
                        label: ''
                    }
                ]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    display: false
                },
                scales: {
                    yAxes: [{
                        display: true
                    }]
                },
                title: {
                    display: true,
                    text: '',
                    fontSize: 24,
                    padding: 8
                }
            }
        });
    }
});

const ChannelRecentPage = Vue.component('channel-recent-page', {
    template: '#channel-recent-page',
    props: {
        channelId: {
            required: true
        }
    },
    data: function () {
        return {
            items: [],
            title: '',
            color: '',
            unit: ''
        };
    },
    computed: {
        labels: function () {
            return this.items.map(function(item) {
                return item[0];
            });
        },
        values: function () {
            return this.items.map(function(item) {
                return item[1];
            });
        }
    },
    watch: {
        channelId: function() {
            this.update();
        }
    },
    created: function () {
        this.update();
    },
    methods: {
        update: function() {
            var self = this;
            apiClient.get('/channel/' + this.channelId + '/stats?type=recent').then(function (response) {
                var data = response.data;
                self.items = [];
                for (var i = 0; i < data.labels.length; ++i) {
                    self.add(data.labels[i], data.values[i], true);
                }
                self.color = data.color;
                self.title = data.title;
                self.unit = data.unit;
            });
        },
        add: function(label, value, ignoreDuplicatedLabel) {
            if (this.items.length > 0 && this.items.last()[0] === label && ignoreDuplicatedLabel === true){
                return;
            }

            this.items.push([label, value]);
        }
    }
});

const ChannelCustomPage = Vue.component('channel-custom-page', {
    template: '#channel-custom-page',
    data: function () {
        return {
            items: [],
            title: '',
            unit: '',
            from: '',
            to: '',
            fieldsEnabled: true,
            fieldsShown: false,
            maxPoints: 60
        };
    },
    props: {
        channelId: {
            required: true
        }
    },
    computed: {
        formattedFrom: function () {
            return this.from.replace(/-/g, '') + '0000';
        },
        formattedTo: function () {
            return this.to.replace(/-/g, '') + '2359';
        },
        labels: function () {
            return this.items.map(function(item) {
                return item[0];
            });
        },
        values: function () {
            return this.items.map(function(item) {
                return item[1];
            });
        }
    },
    watch: {
        channelId: function() {
            this.update();
        },
        from: function () {
            this.periodChanged = true;
        },
        to: function () {
            this.periodChanged = true;
        }
    },
    created: function () {
        var dateFrom, dateTo;

        if (isValidDate(this.$route.query.from) && isValidDate(this.$route.query.to)) {
            dateFrom = new Date(this.$route.query.from);
            dateTo = new Date(this.$route.query.to);
        } else {
            dateFrom = (new Date).addDays(-30);
            dateTo = (new Date);
        }

        this.periodChanged = true;
        this.from = dateFrom.toISOString().substr(0, 10);
        this.to = dateTo.toISOString().substr(0, 10);
        this.show();
    },
    methods: {
        update: function() {
            var url = '/channel/' + this.channelId + '/stats?type=custom&from=' + this.formattedFrom + '&to=' + this.formattedTo;
            var self = this;
            self.fieldsEnabled = false;
            apiClient.get(url).then(function (response) {
                var data = response.data;
                self.items = [];
                for (var i = 0; i < data.labels.length; ++i) {
                    self.items.push([data.labels[i], data.values[i]]);
                }
                self.title = data.title;
                self.unit = data.unit;
                self.fieldsEnabled = true;
            });
        },
        show: function () {
            if (this.periodChanged !== true) {
                return;
            }

            this.$router.push({
                name: 'channel_custom',
                query: {
                    from: this.from,
                    to: this.to
                }
            });
            this.periodChanged = false;
            this.update();
        },
        toggleFields: function () {
            this.fieldsShown = !this.fieldsShown;

            if (!this.fieldsShown) {
                this.show();
            }
        }
    }
});

const ChannelEditPage = Vue.component('channel-edit-page', {
    template: '#channel-edit-page',
    data: function () {
        return {
            channel: {}
        };
    },
    props: {
        channelId: {
            required: true
        }
    },
    watch: {
        channelId: function () {
            this.update();
        }
    },
    created: function () {
        this.update();
    },
    methods: {
        update: function() {
            var self = this;
            apiClient.get('/channel/' + this.channelId).then(function (response) {
                self.channel = response.data;
            });
        },
        save: function () {
            apiClient.post('/channel/' + this.channelId, this.channel);
        }
    }
});

const LoginPage = Vue.component('login-page', {
    template: '#login-page',
    data: function () {
        return {
            username: '',
            password: ''
        };
    },
    methods: {
        login: function () {
            this.$router.push('/');
        }
    }
});

const router = new VueRouter({
    routes: [
        { path: '/', component: ChannelsPage, name: 'home' },
        { path: '/login', component: LoginPage, name: 'login' },
        { path: '/channel/:channelId/edit', component: ChannelEditPage, name: 'channel_edit', props: true},
        { path: '/channel/:channelId/recent', component: ChannelRecentPage, name: 'channel_recent', props: true },
        { path: '/channel/:channelId/custom', component: ChannelCustomPage, name: 'channel_custom', props: true }
    ]
});

const app = new Vue({
    el: '#app',
    data: {
        channels: [],
        connected: false,
        user: {}
    },
    computed: {
        isLogged: function() {
            return this.user.name !== undefined;
        }
    },
    created: function() {
        var self = this;
        apiClient.get('channels').then(function (response) {
            self.channels = response.data.channels.map(function(channel) {
                channel.values = [1];
                apiClient.get('/channel/' + channel.id + '/stats?type=recent').then(function (response) {
                    channel.values = response.data.values;
                });
                return channel;
            });
        });
        apiClient.get('session').then(function (response) {
           self.user = response.data.user;
        });
    },
    router: router
});

function channelUpdate(channel, newValue) {
    switch (app.$route.name)
    {
        case 'home':
            var oldValue = channel.value;
            channel.value = newValue;
            channel.value_updated = new Date().toISOString();
            channel.change = Math.sign(newValue - oldValue);
            break;

        case 'channel_recent':
            if (parseInt(app.$route.params.channelId) === channel.id) {
                var label = new Date().toHourMinute();
                var currentView = app.$children[0];
                if (currentView !== undefined && currentView.add !== undefined) {
                    currentView.add(label, newValue, true);
                }
            }
            break;
    }
}

// MQTT Client
const clientId = generateGuid();
const defaultConnectOptions = {
    onSuccess: function() {
        client.subscribe('+/+');
        client.subscribe('notify/+');
        app.connected = true;
    }
};

var client = new Paho.MQTT.Client('wss://' + window.location.host + ':9883/ws', clientId);
client.onConnectionLost = function (response) {
    app.connected = false;

    if (response.errorCode === 0) {
        // client requested disconnection, ignore
        return;
    }

    console.log(response.errorMessage);

    var connectOptions = Object.assign(defaultConnectOptions, {
        cleanSession: false
    });
    client.connect(connectOptions);
};

client.onMessageArrived = function (message) {
    try {
        var topic = message.destinationName;
        var payload = message.payloadString;

        var channelUuid = topic.split('/')[1];
        var newValue = parseFloat(payload);

        // temporary fix for invalid negative values
        if (newValue > 4000) {
            newValue -= 4096;
        }

        var channel = app.channels.find(function(channel) {
            return channelUuid === channel.uuid;
        });

        if (channel !== undefined) {
            channelUpdate(channel, newValue);
        }
    } catch(e) {
        console.error(e);
    }
};

client.connect(defaultConnectOptions);
