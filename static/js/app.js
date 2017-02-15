"use strict";

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

Array.prototype.pushAndShift = function(item) {
    var shifted = this.shift();
    this.push(item);
    return shifted;
};

function hexToRgba(hex, alpha) {
    if (hex[0] == '#') {
        hex = hex.slice(1);
    }

    var r = parseInt(hex.slice(0, 2), 16),
        g = parseInt(hex.slice(2, 4), 16),
        b = parseInt(hex.slice(4, 6), 16),
        a = alpha || 1.0;

    return 'rgba(' + [r, g, b, a].join(', ') + ')';
}

function generateGuid() {
    var result = '';
    for (var j = 0; j < 32; j++) {
        if (j == 8 || j == 12|| j == 16|| j == 20)
            result += '-';
        result += Math.floor(Math.random() * 16).toString(16).toUpperCase();
    }
    return result;
}

function createChart(options) {
    return new Chart(options.target, {
        animation: false,
        responsive: true,
        type: 'line',
        data: {
            labels: options.labels || [],
            datasets: [
                {
                    fill: false,
                    lineTension: 0,
                    pointRadius: 0,
                    data: options.values || [],
                    borderColor: options.color || 'rgba(0, 0, 144, 0.5)',
                    borderWidth: 2.5
                }
            ]
        },
        options: {
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: !!options.axisTitle,
                        labelString: options.axisTitle || ''
                    }
                }]
            }
        }
    });
}

const Item = Vue.component('item', {
    template: '#channel-item',
    props: {
        channel: {
            required: true
        },
        user: {
            required: true
        }
    }
});

const Home = Vue.component('home', {
    template: '#channel-list',
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

            axios.post('/api/updateOrder', {
                order: newOrder
            }).then(function() {
                console.log('saved!');
            });
        }
    }
});

const ChannelRecent = Vue.component('channel-recent', {
    template: '#channel-recent',
    props: {
        channelId: {
            required: true
        }
    },
    data: function () {
        return {
            stats: {},
            chart: null,
            loading: false
        };
    },
    watch: {
        stats: function () {
            this.chart = createChart({
                target: this.$el,
                type: 'recent',
                labels: this.stats.labels,
                values: this.stats.values,
                axisTitle: this.stats.title + ' [' + this.stats.unit + ']',
                color: hexToRgba(app.channelById(this.channelId).color, 0.75)
            });
        },
        channelId: function() {
            this.loadStats();
        }
    },
    created: function () {
        this.loadStats();
    },
    methods: {
        loadStats: function() {
            var url = '/api/getStats?type=recent&channelId=' + this.channelId;
            var self = this;
            axios.get(url).then(function (response) {
                self.stats = response.data;
            });
        },
        addPoint: function(label, value, ignoreDuplicatedLabel) {
            if (this.chart == null || this.chart.data == null) {
                return;
            }

            if (this.chart.data.labels.last() === label && ignoreDuplicatedLabel) {
                return;
            }

            this.chart.data.labels.pushAndShift(label);
            this.chart.data.datasets[0].data.pushAndShift(value);
            this.chart.update();
        }
    }
});

const ChannelCustom = Vue.component('channel-custom', {
    template: '#channel-custom',
    data: function () {
        return {
            stats: {},
            chart: null,
            from: null,
            to: null
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
        }
    },
    watch: {
        stats: function () {
            this.chart = createChart({
                target: this.$el.querySelector('canvas'),
                type: 'recent',
                labels: this.stats.labels,
                values: this.stats.values,
                axisTitle: this.stats.title + ' [' + this.stats.unit + ']'
            });
        }
    },
    created: function () {
        this.from = (new Date).addDays(-30).toISOString().substr(0, 10);
        this.to = (new Date).toISOString().substr(0, 10);

        this.loadStats();
    },
    methods: {
        loadStats: function() {
            var url = '/api/getStats?channelId=' + this.channelId + '&type=custom&from=' + this.formattedFrom + '&to=' + this.formattedTo;
            var self = this;
            axios.get(url).then(function (response) {
                self.stats = response.data;
            });
        },
        show: function () {
            this.loadStats();
        }
    }
});

const router = new VueRouter({
    routes: [
        { path: '/', component: Home, name: 'home' },
        { path: '/channel/:channelId/recent', component: ChannelRecent, name: 'channel_recent', props: true },
        { path: '/channel/:channelId/custom', component: ChannelCustom, name: 'channel_custom', props: true }
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
            return this.user.name != undefined;
        }
    },
    created: function() {
        var self = this;
        axios.get('/api/channels').then(function (response) {
            self.channels = response.data.channels;
        });
        axios.get('/api/session').then(function (response) {
           self.user = response.data.user;
        });
    },
    methods: {
        channelById: function(channelId) {
            return app.channels.find(function(channel) {
                return channelId == channel.id;
            });
        }
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
            if (app.$route.params.channelId == channel.id) {
                var label = new Date().toHourMinute();
                var currentView = app.$children[0];

                if (currentView.addPoint !== undefined) {
                    currentView.addPoint(label, newValue, true);
                }
            }
            break;
    }
}

// MQTT Client
var clientId = generateGuid();

var client = new Paho.MQTT.Client('wss://xxx:9883/ws', clientId);
client.onConnectionLost = function (response) {
    console.log(response);
    app.connected = false
};

client.onMessageArrived = function (message) {
    var topic = message.destinationName;
    var payload = message.payloadString;

    var channelUuid = topic.split('/')[1];
    var newValue = parseFloat(payload);

    // temporary fix for invalid negative values
    if (newValue > 4000) {
        newValue -= 4096;
    }

    var channel = app.channels.find(function(channel) {
        return channelUuid == channel.uuid;
    });

    if (channel == null) {
        return;
    }

    channelUpdate(channel, newValue);
};

client.connect({
    onSuccess: function() {
        client.subscribe('+/+');
        client.subscribe('notify/+');
        app.connected = true;
    }
});
