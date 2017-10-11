<template>
    <div class="hue-ring" @keydown="keyDown" tabindex="0">
        <canvas :width="size" :height="size" @click="click" @mousedown="mouseDown" @touchstart="touchStart"></canvas>
        <div class="knob" :style="{
            'left': left + 'px',
            'top': top + 'px',
            'width': (outerRadius - innerRadius) + 'px',
            'transform': 'translate(' + (-(outerRadius - innerRadius) / 2) + 'px, -1px) rotateZ(' + hue + 'deg)',
            'background': knobColor
        }"></div>
    </div>
</template>
<script>
    import tinycolor from 'tinycolor2';
    import { hsvToRgb } from '../colors.js';
    import { clamp } from '../math-utils.js';

    function radToDeg(x) {
        return (x > 0 ? x : (2 * Math.PI + x)) * 360 / (2 * Math.PI)
    }

    function pointToDeg(x, y) {
        return radToDeg(Math.atan2(y, x));
    }

    function createHueRingImageData(size, innerRadius, outerRadius) {
        let width = size,
            height = size,
            buffer = new Uint8ClampedArray(width * height * 4),
            imageData = new ImageData(buffer, width, height);

        let index = 0;
        for (let i = 0; i < height; ++i) {
            for (let j = 0; j < width; ++j) {
                let x = j - width / 2,
                    y = i - height / 2;

                let radius = Math.sqrt(x * x + y * y),
                    distanceToOuter = Math.abs(radius - outerRadius),
                    distanceToInner = Math.abs(radius - innerRadius),
                    distanceToNearest = Math.min(distanceToOuter, distanceToInner);

                if (radius <= outerRadius && radius >= innerRadius) {
                    let rgb = hsvToRgb(pointToDeg(x, y), 100, 100);
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

        return imageData;
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
            canvas() {
                return this.$el.querySelector('canvas');
            },
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
            let context = this.canvas.getContext('2d'),
                width = this.canvas.width,
                height = this.canvas.height;
            context.clearRect(0, 0, width, height);
            context.putImageData(createHueRingImageData(this.size, this.innerRadius, this.outerRadius), 0, 0);

            this.onMouseMove = e => {
                this.setByClientPoint(e.clientX, e.clientY);
            };

            this.onMouseUp = () => {
                document.removeEventListener('mousemove', this.onMouseMove);
                document.removeEventListener('mouseup', this.onMouseUp);
            };

            this.onTouchMove = e => {
                this.setByClientPoint(e.changedTouches[0].clientX, e.changedTouches[0].clientY);
            };

            this.onTouchEnd = () => {
                document.removeEventListener('touchmove', this.onTouchMove);
                document.removeEventListener('touchend', this.onTouchEnd);
            };
        },
        methods: {
            setByClientPoint(clientX, clientY) {
                 let rect = this.canvas.getBoundingClientRect(),
                    x = clientX - (rect.left + rect.width / 2),
                    y = clientY - (rect.top + rect.height / 2),
                    hue = pointToDeg(x, y);
                this.$emit('update:hue', hue);
            },
            click(e) {
                this.setByClientPoint(e.clientX, e.clientY);
            },
            mouseDown() {
                document.addEventListener('mouseup', this.onMouseUp);
                document.addEventListener('mousemove', this.onMouseMove);
            },
            touchStart() {
                document.addEventListener('touchend', this.onTouchEnd);
                document.addEventListener('touchmove', this.onTouchMove);
            },
            keyDown(e) {
                let dir = 0;
                if (e.keyCode === 38) {
                    dir = 1;
                } else if (e.keyCode === 40) {
                    dir = -1;
                } else {
                    return;
                }

                let delta = 2,
                    newHue = (this.hue + dir * delta + 360) % 360;
                this.$emit('update:hue', newHue);
            }
        }
    }
</script>
<style lang="scss">
    .hue-ring {
        user-select: none;
        touch-action: none;
        display: inline-block;

        &:focus {
            outline: none;
        }

        .knob {
            position: relative;
            height: 2px;
            border: 1px solid #FFFFFF;
            box-sizing: content-box;
            cursor: pointer;
        }
    }
</style>