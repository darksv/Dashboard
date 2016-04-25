function createChart(container, title)
{
    var options = {
        chart: {
            type: 'spline',
            renderTo: container
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
    $.getJSON('/api/sensors/' + sensorId + '/stats/' + type, function(data) {
        var labels = [];
        var series = [];

        for (var i = 0; i < data.data.length; i++)
        {
            labels.push(data.data[i][0]);
            series.push(data.data[i][1]);
        }

        chart.xAxis[0].setCategories(labels);
        chart.addSeries({data: series});

        chart.redraw();
    });
}

$(function () {
    $('[data-chart]').each(function() {
        var chart = createChart(this, $(this).data('chart'));
        updateChart(chart, $(this).data('chart'), $(this).data('sensor-id'));
    });
});