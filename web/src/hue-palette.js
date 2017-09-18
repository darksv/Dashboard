/*
    Fast implementation of HSV to RGB conversion for lange amount of pixels
    that is used to build saturation/value palette for a given hue.
    It creates ImageData object that can be use to fill canvas using putImageData.
    Based on hsvToRgb function from tinycolor, but optimized for our use case.
*/

"use strict";

function generatePaletteForHue(hue, width, height) {
    hue /= 60;
    let buffer = new Uint8ClampedArray(width * height * 4),
        integerHue = Math.floor(hue);
    [fill0, fill1, fill2, fill3, fill4, fill5][integerHue % 6](buffer, width, height, hue - integerHue);
    return new ImageData(buffer, width, height);
}

export {
    generatePaletteForHue
}

function fill0(buffer, width, height, fractionHue) {
    for (let y = 0; y < height; ++y) {
        let v = 1 - y / height,
            z = y * width;

        for (let x = 0; x < width; ++x) {
            let s = x / width,
                i = (z + x) << 2,
                p = v * (1 - s),
                t = v * (1 - (1 - fractionHue) * s);

            buffer[i] = v * 255;
            buffer[i + 1] = t * 255;
            buffer[i + 2] = p * 255;
            buffer[i + 3] = 255;
        }
    }
}

function fill1(buffer, width, height, fractionHue) {
    for (let y = 0; y < height; ++y) {
        let v = 1 - y / height,
            z = y * width;

        for (let x = 0; x < width; ++x) {
            let s = x / width,
                i = (z + x) << 2,
                p = v * (1 - s),
                q = v * (1 - fractionHue * s);

            buffer[i] = q * 255;
            buffer[i + 1] = v * 255;
            buffer[i + 2] = p * 255;
            buffer[i + 3] = 255;
        }
    }
}

function fill2(buffer, width, height, fractionHue) {
    for (let y = 0; y < height; ++y) {
        let v = 1 - y / height,
            z = y * width;

        for (let x = 0; x < width; ++x) {
            let s = x / width,
                i = (z + x) << 2,
                p = v * (1 - s),
                t = v * (1 - (1 - fractionHue) * s);

            buffer[i] = p * 255;
            buffer[i + 1] = v * 255;
            buffer[i + 2] = t * 255;
            buffer[i + 3] = 255;
        }
    }
}

function fill3(buffer, width, height, fractionHue) {
    for (let y = 0; y < height; ++y) {
        let v = 1 - y / height,
            z = y * width;

        for (let x = 0; x < width; ++x) {
            let s = x / width,
                i = (z + x) << 2,
                p = v * (1 - s),
                q = v * (1 - fractionHue * s);

            buffer[i] = p * 255;
            buffer[i + 1] = q * 255;
            buffer[i + 2] = v * 255;
            buffer[i + 3] = 255;
        }
    }
}

function fill4(buffer, width, height, fractionHue) {
    "use strict";
    for (let y = 0; y < height; ++y) {
        let v = 1 - y / height,
            z = y * width;

        for (let x = 0; x < width; ++x) {
            let s = x / width,
                i = (z + x) << 2,
                p = v * (1 - s),
                t = v * (1 - (1 - fractionHue) * s);

            buffer[i] = t * 255;
            buffer[i + 1] = p * 255;
            buffer[i + 2] = v * 255;
            buffer[i + 3] = 255;
        }
    }
}

function fill5(buffer, width, height, fractionHue) {
    "use strict";
    for (let y = 0; y < height; ++y) {
        let v = 1 - y / height,
            z = y * width;

        for (let x = 0; x < width; ++x) {
            let s = x / width,
                i = (z + x) << 2,
                p = v * (1 - s),
                q = v * (1 - fractionHue * s);

            buffer[i] = v * 255;
            buffer[i + 1] = p * 255;
            buffer[i + 2] = q * 255;
            buffer[i + 3] = 255;
        }
    }
}
