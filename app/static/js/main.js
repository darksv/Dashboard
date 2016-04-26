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
        daily: 'Ostatnie 24 godziny',
        monthly: 'Ostatni miesiąc'
    };

    $('[data-chart]').each(function() {
        var chartType = $(this).data('chart');
        var chart = createChart(this, chartTitles[chartType]);
        updateChart(chart, chartType, $(this).data('sensor-id'));
    });
});