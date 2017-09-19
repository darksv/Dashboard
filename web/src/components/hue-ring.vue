<template>
    <div :style="{ 'background': knobColor }">
        <canvas :width="size" :height="size" @click="set"></canvas>
        <div :style="{
            'left': left + 'px',
            'top': top + 'px',
            'position': 'relative',
            'width': (outerRadius - innerRadius) + 'px',
            'height': '2px',
            'border': '1px solid #FFFFFF',
            'box-sizing': 'borderbox',
            'background': knobColor,
            'transform': 'translate(' + (-(outerRadius - innerRadius) / 2) + 'px, -1px) rotateZ(' + hue + 'deg)'
        }"></div>
    </div>
</template>
<script>
    import { hsvToRgb } from '../colors.js';
    import tinycolor from 'tinycolor2';

    function pointToAngle(x) {
        return (x > 0 ? x : (2 * Math.PI + x)) * 360 / (2 * Math.PI)
    }

    export default {
        props: {
            hue: {
                required: true,
                type: Number
            },
            size: {
                required: true,
                type: Number
            },
            radiusRatio: {
                required: false,
                type: Number,
                default: 0.75
            }
        },
        computed: {
            knobColor() {
                return tinycolor({h: this.hue, s: 100, v: 100}).toHexString();
            },
            outerRadius() {
                return this.size / 2;
            },
            innerRadius() {
                return this.outerRadius * this.radiusRatio;
            },
            left() {
                return this.size / 2 + ((this.outerRadius + this.innerRadius) / 2) * Math.cos(this.hue / 360 * 2 * Math.PI);
            },
            top() {
                return -this.size / 2 + ((this.outerRadius + this.innerRadius) / 2) * Math.sin(this.hue / 360 * 2 * Math.PI) - 3;
            }
        },
        mounted() {
            let canvas = this.$el.querySelector('canvas'),
                context = canvas.getContext('2d'),
                width = canvas.width,
                height = canvas.height,
                buffer = new Uint8ClampedArray(width * height * 4),
                imageData = new ImageData(buffer, width, height);

            let index = 0;
            for (let i = 0; i < height; ++i) {
                for (let j = 0; j < width; ++j) {
                    let x = j - width / 2,
                        y = i - height / 2;

                    let radius = Math.sqrt(x * x + y * y),
                        distanceToOuter = Math.abs(radius - this.outerRadius),
                        distanceToInner = Math.abs(radius - this.innerRadius),
                        distanceToNearest = Math.min(distanceToOuter, distanceToInner);

                    if (radius <= this.outerRadius && radius >= this.innerRadius) {
                        let rgb = hsvToRgb(pointToAngle(Math.atan2(y, x)), 100, 100);
                        buffer[index++] = rgb[0];
                        buffer[index++] = rgb[1];
                        buffer[index++] = rgb[2];
                        buffer[index++] = distanceToNearest * 255;
                    } else {
                        buffer[index++] = 0;
                        buffer[index++] = 0;
                        buffer[index++] = 0;
                        buffer[index++] = 0;
                    }
                }
            }

            context.clearRect(0, 0, width, height);
            context.putImageData(imageData, 0, 0);
        },
        methods: {
            set(e) {
                let x = e.offsetX - this.size / 2,
                    y = e.offsetY - this.size / 2,
                    hue = pointToAngle(Math.atan2(y, x));
                this.$emit('update:hue', hue);
            }
        }
    }
</script>