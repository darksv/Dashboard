Highcharts.setOptions({
    global: {
        useUTC: false
    }
});

function showChannelStats(options)
{
    const isRealtime = (options.type == 'realtime');

    var startUpdates = function(chart) {
        var series = chart.series[0];

        setInterval(function(){
            $.getJSON('/api/channels/' + options.channelId, function(response) {
                var data = response.data,
                    x = (new Date(data.value_updated)).getTime(),
                    y = data.value,
                    lastTimestamp = series.data[series.data.length - 1].x;

                var channelValueLabel = $('#channel_value');
                var delta = y - channelValueLabel.text();

                var changeIndicator = channelValueLabel.prev().removeClass('glyphicon-arrow-up glyphicon-arrow-down');
                if (delta < 0)
                    changeIndicator.addClass('glyphicon-arrow-down');
                else if (delta > 0)
                    changeIndicator.addClass('glyphicon-arrow-up');

                channelValueLabel.text(y);
                channelValueLabel.attr('title', data.value_updated);

                if (lastTimestamp != x)
                    series.addPoint([x, y], true, true);
            });
        }, 5000);
    };

    var onChartLoad = function () {
        const chart = this;

        $.getJSON('/api/channels/' + options.channelId + '/stats/' + (isRealtime ? 'recent': options.type), function (data) {
            var labels = [],
                series = [];

            for (var i = 0; i < data.data.length; i++) {
                var label = data.data[i][0],
                    value = data.data[i][1];

                if (isRealtime) {
                    label = (new Date(label)).getTime();
                    series.push([label, value]);
                } else {
                    labels.push(label);
                    series.push(value);
                }
            }

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

            if (isRealtime) {
                startUpdates(chart);
            } else {
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

    if (isRealtime)
    {
        chartOptions.animation = Highcharts.svg;
        chartOptions.xAxis = {
            type: 'datetime',
            tickPixelInterval: 150
        };
    }

    console.log(chartOptions);

    return new Highcharts.Chart(chartOptions);
}

$(function () {
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
});