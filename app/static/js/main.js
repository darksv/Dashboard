function createChart(container, title, labels, values)
{
    $(container).highcharts({
        chart: {
            type: 'spline'
        },
        title: {
            text: title,
            x: -20
        },
        xAxis: {
            categories: labels
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
        series: [{
            data: values
        }],
        legend: {
            enabled: false
        }
    });
}

function randomValues(min, max, count)
{
    var r = [];
    for (var i = 0; i < count; i++)
    {
        r.push(min + Math.random() * (max - min));
    }
    return r;
}

$(function () {
    createChart('#chart_daily', 'Dzienny', hours, hours_values);
    createChart('#chart_yearly', 'Roczny', months, randomValues(-50, 50, 12));
    createChart('#chart_monthly', 'Miesięczny', days, randomValues(-20, 10, 30));
});