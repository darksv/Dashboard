(function() {
    "use strict";

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

    String.prototype.zfill = function(width) {
        if (width > this.length) {
            return new Array(width - this.length + 1).join('0') + this;
        }
        return this;
    };

    Number.prototype.zfill = function(width) {
        return this.toString().zfill(width);
    };

    if (Notification.permission === 'default') {
        Notification.requestPermission();
    }

    var windowActive = true,
        originalWindowTitle = document.title,
        windowTitlePrefix = '';

    $(window).on('focus', function (e) {
        windowActive = true;
    }).on('blue', function (e) {
        windowActive = false;
    });

    function updateChannelLabel(newValue, timestamp) {
        var channelValueLabel = $('#channel_value'),
            oldValue = parseFloat(channelValueLabel.data('value')),
            diff = newValue - oldValue,
            diffSign = Math.sign(diff),
            changeIndicator = channelValueLabel.prev();

        if (diffSign != 0) {
            changeIndicator.removeClass('glyphicon-arrow-up glyphicon-arrow-down');
        }

        var arrow = '';
        switch (diffSign) {
            case -1:
                changeIndicator.addClass('glyphicon-arrow-down');
                arrow = '↓';
                break;
            case 1:
                changeIndicator.addClass('glyphicon-arrow-up');
                arrow = '↑';
                break;
            case 0:
                // no change
                break;
        }

        var valueWithUnit = newValue + ' ' + channelValueLabel.data('unit');

        channelValueLabel.data('value', newValue);
        channelValueLabel.text(valueWithUnit);
        channelValueLabel.attr('title', new Date(timestamp).toLocaleTimeString());

        windowTitlePrefix = arrow + valueWithUnit;
        document.title = windowTitlePrefix + ' - ' + originalWindowTitle;
    }

    function updateChart(chart, options) {
        var params = {
            'channelId': options.channelId,
            'type': options.type
        };

        if (options.type == 'custom') {
            params['from'] = options.from;
            params['to'] = options.to;
        }

        var url = '/getStats?' + $.param(params);
        $.getJSON(url, function (data) {
            chart.data.labels = data.labels;
            chart.data.datasets[0].data = data.values;
            chart.options.scales.yAxes[0].scaleLabel.labelString = data.title + ' [' + data.unit + ']';
            chart.update();
        });
    }

    function createChart(options) {
        var chart = new Chart(options.target, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        fill: false,
                        lineTension: 0,
                        pointRadius: 0,
                        data: [],
                        borderColor: 'rgba(50, 120, 180, 0.5)',
                        borderWidth: 1.5
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
                            display: false
                        }
                    }]
                }
            }
        });

        if (options.autoUpdate) {
            updateChart(chart, options);
        }
        return chart;
    }

    var realtimeChart = createChart({
        target: document.getElementById('realtime_chart'),
        type: 'recent',
        channelId: page_data.channel_id,
        autoUpdate: true
    });

    var customChartOptions = {
        target: document.getElementById('custom_chart'),
        type: 'custom',
        channelId: page_data.channel_id,
        autoUpdate: false
    };
    var customChart = createChart(customChartOptions);

    var chartSettingsForm = $('#chart_settings');
    var chartFrom = $('input[name=from]', chartSettingsForm);
    var chartTo = $('input[name=to]', chartSettingsForm);
    chartFrom.val((new Date).addDays(-30).toISOString().substr(0, 10));
    chartTo.val((new Date).toISOString().substr(0, 10));

    chartSettingsForm.submit(function (e) {
        if (chartFrom.val().length > 0 && chartTo.val().length > 0) {
            customChartOptions['from'] = chartFrom.val().replace(/-/g, '') + '0000';
            customChartOptions['to'] = chartTo.val().replace(/-/g, '') + '2359';

            updateChart(customChart, customChartOptions);
        }

        e.preventDefault();
        return false;
    }).submit();

    function addToChart(chart, label, value) {
        chart.data.labels.pushAndShift(label);
        chart.data.datasets[0].data.pushAndShift(value);
        chart.update();
    }

    var clientId = navigator.userAgent;

    var client = new Paho.MQTT.Client('wss://xxx:9883/ws', clientId);
    client.onConnectionLost = function (responseObject) {
        if (responseObject.errorCode !== 0)
            console.log('connection lost', responseObject.errorMessage);
    };

    client.onMessageArrived = function (message) {
        if (page_data.endpoint == 'channel_details' && message.destinationName.indexOf(page_data.channel_uuid) !== -1) {
            var label = (new Date).toHourMinute();
            if (realtimeChart.data.labels.last() !== label) {
                addToChart(realtimeChart, label, parseFloat(message.payloadString));
            }

            updateChannelLabel(message.payloadString, Date.now());
        } else if (message.destinationName.startsWith('notify')) {
            new Notification('Informacja', {
                body: message.payloadString
            });
        }
    };

    client.connect({
        onSuccess: function() {
            if (page_data.endpoint === 'channel_details')
                client.subscribe('+/' + page_data.channel_uuid);

            if (page_data.user.name !== null)
                client.subscribe('notify/' + page_data.user.name);
        }
    });
})();