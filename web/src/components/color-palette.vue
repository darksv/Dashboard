<template>
    <div class="color-palette">
        <canvas width="1000" height="500" @click="click"></canvas>
        <div class="knob" :style="{ left: knobX + 'px', top: knobY + 'px', backgroundColor: knobColor }"></div>
    </div>
</template>

<script>
    import tinycolor from 'tinycolor2';
    import { clamp } from '../math-utils.js';
    import { generatePaletteForHue } from '../hue-palette.js';

    function hsvToRgb(h, s, v) {
        // Based on hsvToRgb function from tinycolor (original does not work for some specified colors
        h = h / 60;
        s = s / 100;
        v = v / 100;

        var i = Math.floor(h),
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

    export default {
        props: {
            hue: {
                required: true,
                type: Number
            },
            saturation: {
                required: false,
                type: Number
            },
            value: {
                required: false,
                type: Number
            }
        },
        data: function() {
            return {
                canvas: null,
                context: null,
                isMouseDown: false,
                mouseUp: null,
                mouseDown: null,
                mouseMove: null
            }
        },
        computed: {
            knobX: function() {
                return this.canvas
                    ? this.saturation / 100 * this.canvas.width - 8
                    : -8;
            },
            knobY: function() {
                return this.canvas
                    ? (1 - this.value / 100) * this.canvas.height - 8
                    : -8
            },
            knobColor: function() {
                var color = hsvToRgb(this.hue, this.saturation, this.value).map(function(x) {
                    return ~~x;
                }).join(', ');
                return 'rgb(' + color + ')';
            }
        },
        watch: {
            hue: function() {
                this.redraw();
            }
        },
        mounted: function() {
            this.canvas = this.$el.querySelector('canvas');
            this.context = this.canvas.getContext('2d');
            this.redraw();

            var self = this;

            this.mouseDown = function(e) {
                if (e.button === 0 && (e.target === self.$el.querySelector('canvas') || e.target === self.$el.querySelector('.knob'))) {
                    self.isMouseDown = true;
                }
            };
            this.mouseUp = function(e) {
                if (e.button === 0) {
                    self.isMouseDown = false;
                }
            };
            this.mouseMove = function(e) {
                if (e.button === 0 && self.isMouseDown) {
                    var boundingRect = self.$el.getBoundingClientRect();
                    self.update(e.x - boundingRect.left, e.y - boundingRect.top);
                }
            };

            document.addEventListener('mousedown', this.mouseDown);
            document.addEventListener('mouseup', this.mouseUp);
            document.addEventListener('mousemove', this.mouseMove);
        },
        beforeDestroy: function() {
            document.removeEventListener('mousedown', this.mouseDown);
            document.removeEventListener('mouseup', this.mouseUp);
            document.removeEventListener('mousemove', this.mouseMove);
        },
        methods: {
            click: function(e) {
                this.update(e.offsetX, e.offsetY);
            },
            update: function(offsetX, offsetY) {
                this.$emit('update:saturation', clamp(0, 100, offsetX / this.canvas.width * 100));
                this.$emit('update:value', clamp(0, 100, (1 - offsetY / this.canvas.height) * 100));
            },
            redraw: function() {
                var width = this.canvas.width,
                    height  = this.canvas.height,
                    context = this.context;
                context.clearRect(0, 0, width, height);
                context.putImageData(generatePaletteForHue(this.hue, width, height), 0, 0);
            }
        }
    };
</script>

<style lang="scss">
    .color-palette {
        margin: 1em;
        position: relative;

        canvas {
            position: absolute;
        }

        .knob {
            position: absolute;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border: 1px solid #FFFFFF;
            top: -8px;
            left: -8px;
        }
    }
</style>