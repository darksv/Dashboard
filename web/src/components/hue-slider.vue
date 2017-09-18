<template>
    <div class="hue-slider" @click="click">
        <div class="knob" :style="{ left: knobLeft + 'px', backgroundColor: knobColor }"></div>
    </div>
</template>

<script>
    import tinycolor from 'tinycolor2';
    import { clamp } from '../math-utils.js';

    export default {
        props: {
            hue: {
                required: false,
                type: Number,
                default: 0
            }
        },
        data: function() {
            return {
                isMouseDown: false,
                width: 0,
                mouseUp: null,
                mouseDown: null,
                mouseMove: null
            };
        },
        computed: {
            knobLeft: function() {
                return this.hue / 360 * this.width - 8;
            },
            knobColor: function() {
                return tinycolor({h: this.hue, s: 100, v: 100}).toRgbString();
            }
        },
        methods: {
            click: function(e) {
                if (e.target === this.$el) {
                    this.updateHue(e.offsetX);
                }
            },
            updateHue: function(offset) {
                var hue = parseInt(clamp(0, 360, offset / this.width * 360));
                this.$emit('update:hue', hue);
            }
        },
        mounted: function() {
            var self = this;
            this.width = this.$el.clientWidth;
            this.mouseDown = function(e) {
                if (e.button === 0 && (e.target === self.$el || e.target === self.$el.querySelector('.knob'))) {
                    e.preventDefault();
                    self.isMouseDown = true;
                }
            };
            this.mouseUp = function(e) {
                if (e.button === 0) {
                    e.preventDefault();
                    self.isMouseDown = false;
                }
            };
            this.mouseMove = function(e) {
                if (e.button === 0 && self.isMouseDown) {
                    e.preventDefault();
                    self.updateHue(e.x - self.$el.getBoundingClientRect().left);
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
        }
    };
</script>

<style lang="scss">
    .hue-slider {
        width: 100px;
        height: 10px;
        background: linear-gradient(to right,
            hsl(0, 100%, 50%),
            hsl(60, 100%, 50%),
            hsl(120, 100%, 50%),
            hsl(180, 100%, 50%),
            hsl(240, 100%, 50%),
            hsl(300, 100%, 50%),
            hsl(360, 100%, 50%)
        );
        margin: 1em;
        user-select: none;
    }

    .hue-slider .knob {
        width: 16px;
        height: 16px;
        top: -4px;
        left: 0px;
        border-radius: 50%;
        border: 1px solid #FFFFFF;
        position: relative;
        cursor: pointer;
    }
</style>