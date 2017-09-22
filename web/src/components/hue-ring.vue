<template>
    <div class="hue-ring">
        <canvas :width="size" :height="size" @click="click" @mousedown="mouseDown" @touchstart="touchStart"></canvas>
        <div :style="{
            'left': left + 'px',
            'top': top + 'px',
            'position': 'relative',
            'width': (outerRadius - innerRadius) + 'px',
            'height': '2px',
            'border': '1px solid #FFFFFF',
            'box-sizing': 'borderbox',
            'background': knobColor,
            'transform': 'translate(' + (-(outerRadius - innerRadius) / 2) + 'px, -1px) rotateZ(' + hue + 'deg)',
            'cursor': 'pointer'
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
        data() {
            return {
                onMouseUp: null,
                onMouseMove: null,
                onTouchEnd: null,
                onTouchMove: null
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

            this.onMouseMove = e => {
                let rect = this.$el.querySelector('canvas').getBoundingClientRect(),
                    x = e.clientX - (rect.left + rect.width / 2),
                    y = e.clientY - (rect.top + rect.height / 2),
                    hue = pointToAngle(Math.atan2(y, x));
                this.$emit('update:hue', hue);
            };

            this.onMouseUp = () => {
                document.removeEventListener('mousemove', this.onMouseMove);
                document.removeEventListener('mouseup', this.onMouseUp);
            };

            this.onTouchMove = e => {
                let rect = this.$el.querySelector('canvas').getBoundingClientRect(),
                    x = e.changedTouches[0].clientX - (rect.left + rect.width / 2),
                    y = e.changedTouches[0].clientY - (rect.top + rect.height / 2),
                    hue = pointToAngle(Math.atan2(y, x));
                this.$emit('update:hue', hue);
            };

            this.onTouchEnd = () => {
                document.removeEventListener('touchmove', this.onTouchMove);
                document.removeEventListener('touchend', this.onTouchEnd);
            };
        },
        methods: {
            setByPoint(pointX, pointY) {
                let x = pointX - this.size / 2,
                    y = pointY - this.size / 2,
                    hue = pointToAngle(Math.atan2(y, x));
                this.$emit('update:hue', hue);
            },
            click(e) {
                this.setByPoint(e.clientX, e.clientY);
            },
            mouseDown() {
                document.addEventListener('mouseup', this.onMouseUp);
                document.addEventListener('mousemove', this.onMouseMove);
            },
            touchStart() {
                document.addEventListener('touchend', this.onTouchEnd);
                document.addEventListener('touchmove', this.onTouchMove);
            }
        }
    }
</script>
<style lang="scss">
    .hue-ring {
        user-select: none;
        touch-action: none;
        display: inline-block;
    }
</style>