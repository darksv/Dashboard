function createChart(container, title)
{
    var options = {
        chart: {
            type: 'spline',
            renderTo: container
        },
        plotOptions: {
            line: {
                marker: {
                    enabled: false
                }
            }
        },
        title: {
            text: title,
            x: -20
        },
        xAxis: {
            categories: []
        },
        yAxis: {
            title: {
                text: 'Temperatura (°C)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            valueSuffix: '°C',
            enabled: false
        },
        legend: {
            enabled: false
        }
    };

    return new Highcharts.Chart(options);
}

function createRealtimeChart(container, channelId)
{
    var options = {
        chart: {
            type: 'spline',
            animation: Highcharts.svg,
            events: {
                load: function () {
                    var series = this.series[0];

                    setInterval(function(){
                        $.getJSON('/api/channels/' + channelId, function(response) {
                            var data = response.data,
                                x = (new Date(data.value_updated)).getTime(),
                                y = data.value,
                                lastTimestamp = series.data[series.data.length - 1].x;

                            if (lastTimestamp != x)
                                series.addPoint([x, y], true, true);
                        });
                    }, 5000);
                }
            },
            renderTo: container
        },
        title: {
            text: 'Wykres w czasie rzeczywistym'
        },
        xAxis: {
            type: 'datetime',
            tickPixelInterval: 150
        },
        yAxis: {
            title: {
                text: 'Temperatura (°C)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            enabled: false
        },
        legend: {
            enabled: false
        },
        exporting: {
            enabled: false
        },
        series: [{}]
    };

    $.getJSON('/api/channels/' + channelId + '/stats/recent', function(response) {
        var data = response.data
            points = [];

        for (var i = 0; i < data.length; ++i)
        {
            var entry = data[i];
            points.push([(new Date(entry[0])).getTime(), entry[1]]);
        }

        options.series[0].data = points;
        new Highcharts.Chart(options);
    });
}

function updateChart(chart, type, sensorId)
{
    $.getJSON('/api/channels/' + sensorId + '/stats/' + type, function(data) {
        var labels = [];
        var series = [];

        for (var i = 0; i < data.data.length; i++)
        {
            labels.push(data.data[i][0]);
            series.push(data.data[i][1]);
        }

        chart.xAxis[0].setCategories(labels);
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

        chart.redraw();
    });
}

$(function () {
    const chartTitles = {
        realtime: 'Na żywo',
        daily: 'Ostatnie 24 godziny',
        monthly: 'Ostatni miesiąc'
    };

    $('[data-chart]').each(function() {
        var chartType = $(this).data('chart');
        var sensorId = $(this).data('sensor-id')
        var chart = null;

        if (chartType == 'realtime')
        {
            chart = createRealtimeChart(this, sensorId);
        }
        else
        {
            chart = createChart(this, chartTitles[chartType]);
            updateChart(chart, chartType, sensorId);
        }
    });
});