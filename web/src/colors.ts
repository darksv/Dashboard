function hsvToRgb(h: number, s: number, v: number): Array<number> {
    // Based on hsvToRgb function from tinycolor (original does not work for some specified colors
    h = h / 60;
    s = s / 100;
    v = v / 100;

    const i = Math.floor(h),
        f = h - i,
        p = v * (1 - s),
        q = v * (1 - f * s),
        t = v * (1 - (1 - f) * s),
        mod = i % 6,
        r = [v, q, p, p, t, v][mod],
        g = [t, v, v, q, p, p][mod],
        b = [p, p, t, v, v, q][mod];

    return [r * 255, g * 255, b * 255];
}

export {
    hsvToRgb
}