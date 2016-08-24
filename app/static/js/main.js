(function() {
    console.log(Notification.permission);

    if (Notification.permission === 'default') {
        Notification.requestPermission();
    }

    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

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

    function showChannelStats(options) {
        const isRealtime = (options.type == 'realtime');

        var onChartLoad = function () {
            const chart = this;

            $.getJSON('/channel/' + options.channelId + '/stats/' + (isRealtime ? 'recent': options.type), function (data) {
                var items = data.items,
                    labels = [],
                    series = [];

                for (var i = 0; i < items.length; i++) {
                    var label = items[i][0],
                        value = items[i][1];

                    if (isRealtime) {
                        label = (new Date(label)).getTime();
                        series.push([label, value]);
                    } else {
                        labels.push(label);
                        series.push(value);
                    }
                }

                console.log(labels, series);

                chart.addSeries({
                    data: series,
                    marker: {
                        enabled: false,
                        states: {
                            hover: {
                                enabled: false
                            }
                        }
                    }
                });

                if (!isRealtime) {
                    chart.xAxis[0].setCategories(labels);
                }

                chart.redraw();
            });
        };

        var chartOptions = {
            chart: {
                type: 'spline',
                renderTo: options.container,
                events: {
                    load: onChartLoad
                }
            },
            plotOptions: {
                line: {
                    marker: {
                        enabled: false
                    }
                }
            },
            title: {
                text: options.title,
                x: -20
            },
            exporting: {
                enabled: false
            },
            yAxis: {
                title: {
                    text: options.axisTitle + ' [' + options.unit + ']'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                valueSuffix: options.unit
            },
            legend: {
                enabled: false
            }
        };

        if (isRealtime) {
            chartOptions.animation = Highcharts.svg;
            chartOptions.xAxis = {
                type: 'datetime',
                tickPixelInterval: 150
            };
        }

        console.log(chartOptions);

        return new Highcharts.Chart(chartOptions);
    }

    const chartTitles = {
        realtime: 'Wykres w czasie rzeczywistym',
        daily: 'Ostatnie 24 godziny',
        monthly: 'Ostatni miesiąc'
    };

    const axisTitles = {
        0: 'Temperatura',
        1: 'Ciśnienie'
    };

    const axisUnits = {
        0: '℃',
        1: 'hPa'
    };

    $('[data-chart]').each(function() {
        var chartType = $(this).data('chart'),
            channelId = +$(this).data('channel-id'),
            channelType = +$(this).data('channel-type');

        showChannelStats({
            container: this,
            channelId: channelId,
            type: chartType,
            title: chartTitles[chartType],
            axisTitle: axisTitles[channelType],
            unit: axisUnits[channelType]
        });
    });

    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

    ga('create', 'UA-78299062-1', 'auto');
    ga('send', 'pageview');


    var clientId = navigator.userAgent;

    var client = new Paho.MQTT.Client('ws://xxx:9001/ws', clientId);
    client.onConnectionLost = function (responseObject) {
        if (responseObject.errorCode !== 0)
            console.log('connection lost', responseObject.errorMessage);
    };

    client.onMessageArrived = function (message) {
        console.log('got channel update', message.destinationName, message.payloadString);

        if (data.endpoint == 'channel_details' && message.destinationName.indexOf(data.channel_uuid) !== -1) {
            updateChannelLabel(message.payloadString, Date.now());
        } else if (message.destinationName.startsWith('notify')) {
            new Notification('Informacja', {
                body: message.payloadString
            });
        }
    };

    client.connect({
        onSuccess: function() {
            console.log('connected');

            if (data.endpoint === 'channel_datails')
                client.subscribe('+/' + data.channel_uuid);

            if (data.user.name !== null)
                client.subscribe('notify/' + data.user.name);
        }
    });
})();