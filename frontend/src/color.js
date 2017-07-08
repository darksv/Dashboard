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

export default {
    contrast: contrastColor,
    hexToRgba: hexToRgba
};