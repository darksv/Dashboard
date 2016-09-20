(function() {
    "use strict";

    if (Notification.permission === 'default') {
        Notification.requestPermission();
    }

    function updateChannelLabel(newValue, timestamp) {
        var channelValueLabel = $('#channel_value'),
            oldValue = parseFloat(channelValueLabel.text()),
            diff = newValue - oldValue,
            diffSign = Math.sign(diff),
            changeIndicator = channelValueLabel.prev();

        if (diffSign != 0) {
            changeIndicator.removeClass('glyphicon-arrow-up glyphicon-arrow-down');
        }

        switch (diffSign) {
            case -1:
                changeIndicator.addClass('glyphicon-arrow-down');
                break;
            case 1:
                changeIndicator.addClass('glyphicon-arrow-up');
                break;
            case 0:
                // no change
                break;
        }

        channelValueLabel.text(newValue);
        channelValueLabel.attr('title', new Date(timestamp).toLocaleTimeString());
    }

    function showRealtimeChart(options) {
        var realtimeChart = new Chart(document.getElementById('realtime_chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        fill: true,
                        lineTension: 0.3,
                        pointRadius: 0,
                        data: []
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
                            display: true,
                            labelString: ''
                        }
                    }]
                }
            }
        });

        var url = '/getStats?' + $.param({'channelId': options.channelId, 'type': 'recent'});
        $.getJSON(url, function (data) {
            realtimeChart.data.labels = data.labels;
            realtimeChart.data.datasets[0].data = data.values;
            realtimeChart.options.scales.yAxes[0].scaleLabel.labelString = data.title + ' [' + data.unit + ']';
            realtimeChart.update();
        });

        return realtimeChart;
    }

    var realtimeChart = showRealtimeChart({channelId: data.channel_id});

    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

    ga('create', 'UA-78299062-1', 'auto');
    ga('send', 'pageview');


    var clientId = navigator.userAgent;

    var client = new Paho.MQTT.Client('wss://xxx:9883/ws', clientId);
    client.onConnectionLost = function (responseObject) {
        if (responseObject.errorCode !== 0)
            console.log('connection lost', responseObject.errorMessage);
    };

    function zfill(x) {
        return (x < 10 ? '0' : '') + x;
    }

    function pushAndShift(arr, item) {
        arr.shift();
        arr.push(item);
    }

    function addToChart(chart, label, value) {
        console.log(chart, label, value);

        pushAndShift(chart.data.labels, label);
        pushAndShift(chart.data.datasets[0].data, value);
        chart.update();
    }

    function lastItem(arr) {
        return arr[arr.length - 1];
    }

    client.onMessageArrived = function (message) {
        if (data.endpoint == 'channel_details' && message.destinationName.indexOf(data.channel_uuid) !== -1) {
            var currentTime = new Date;
            var label = zfill(currentTime.getHours()) + ':' + zfill(currentTime.getMinutes());

            if (lastItem(realtimeChart.data.labels) !== label) {
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
            if (data.endpoint === 'channel_details')
                client.subscribe('+/' + data.channel_uuid);

            if (data.user.name !== null)
                client.subscribe('notify/' + data.user.name);
        }
    });
})();