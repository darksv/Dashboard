<template>
    <div class="schedule-editor">
        <div class="schedule-editor-widget">
            <div class="day">
                <div class="label">&nbsp;&nbsp;&nbsp;</div>
                <div v-for="hour in hours" v-bind:key="hour" class="label">{{hour}}</div>
            </div>
            <div v-for="day in days" v-bind:key="day" class="day">
                <div class="label">{{ day.substr(0, 3) }}</div>
                <div v-for="hour in hours" v-bind:key="hour" class="hour"
                     :data-day="getIndexOfDay(day)"
                     :data-hour="hour"
                     :style="{
                         'backgroundColor':
                            getSelector(day, hour).hasPreview
                                ? (getSelector(day, hour).isSelected ? 'rgba(0, 255, 0, 0.5)' : 'rgba(255, 0, 0, 0.5)')
                                : (getSelector(day, hour).isSelected ? 'rgba(0, 255, 0, 1)' : 'inherit')
                     }"></div>
            </div>
        </div>
        <div class="schedule-editor-toolbar">
            <span class="fa" :class="{ 'fa-check-circle-o': include, 'fa-times-circle-o': !include }" title="Include hours" @click="include=!include"></span>
        </div>
    </div>
</template>

<script>
    import { clamp } from '../math-utils.js';

    export default {
        data: function() {
            var days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                hours = Array.from(Array(24).keys());

            return {
                days: days,
                hours: hours,
                isMouseDown: false,
                include: false,
                selection: days.map(function() {
                    return hours.map(function() {
                        return {
                            isSelected: true,
                            hasPreview: false,
                            needsCommit: false
                        };
                    });
                }),
                selectionOrigin: null
            };
        },
        computed: {
            selected: function() {
                return this.selection.map(function(day) {
                    return day.map(function(x, i) {
                        return {hour: i, isSelected: x.isSelected};
                    }).filter(function(x) {
                        return x.isSelected;
                    }).map(function(x) {
                        return x.hour;
                    });
                });
            }
        },
        mounted: function() {
            var self = this;

            this.mouseUp = function(e) {
                e.preventDefault();
                self.isMouseDown = false;
                self.selectionOrigin = null;
                self.commitSelection();
            };

            this.mouseDown = function(e) {
                e.preventDefault();
                self.isMouseDown = true;

                self.selectionOrigin = {
                    day: parseInt(e.target.dataset.day),
                    hour: parseInt(e.target.dataset.hour)
                };
            };

            this.mouseMove = function(e) {
                e.preventDefault();

                if (!self.isMouseDown || e.button !== 0) {
                    return;
                }

                var day, hour;
                if (e.target.className.indexOf('hour') === -1) {
                    // Find bounding rectangle of the all selectors based on first and the last selector rectangles.
                    var selectors = self.$el.querySelectorAll('.hour'),
                        firstSelector = selectors[0],
                        lastSelector = selectors[selectors.length - 1],
                        firstSelectorRect = firstSelector.getBoundingClientRect(),
                        lastSelectorRect = lastSelector.getBoundingClientRect(),
                        selectorsRect = {
                            top: firstSelectorRect.top,
                            left: firstSelectorRect.left,
                            width: lastSelectorRect.left + lastSelectorRect.width - firstSelectorRect.left,
                            height: lastSelectorRect.top + lastSelectorRect.height - firstSelectorRect.top
                        };

                    // Calculate potential selectors that might be selected.
                    // We are assuming that all selectors have equal dimensions.
                    hour = clamp(0, 23, Math.floor((e.clientX - selectorsRect.left) / ((selectorsRect.width / self.hours.length))));
                    day = clamp(0, 6, Math.floor((e.clientY - selectorsRect.top) / ((selectorsRect.height / self.days.length))));

                    console.log(e.target.className, day, hour);

                } else {
                    var data = e.target.dataset;
                    day = parseInt(data.day);
                    hour = parseInt(data.hour);
                }

                var start = self.selectionOrigin,
                    left = Math.min(start.hour, hour),
                    top = Math.min(start.day, day),
                    right = Math.max(start.hour, hour),
                    bottom = Math.max(start.day, day);
                self.clearSelection();
                self.selectRectangle({day: top, hour: left}, bottom - top + 1, right - left + 1, self.include);
            };

            document.addEventListener('mouseup', this.mouseUp);
            document.addEventListener('mousedown', this.mouseDown);
            document.addEventListener('mousemove', this.mouseMove);
        },
        destroy: function() {
            document.removeEventListener('mouseup', this.mouseUp);
            document.removeEventListener('mousedown', this.mouseDown);
            document.removeEventListener('mousemove', this.mouseMove);
        },
        methods: {
            getIndexOfDay: function(day) {
                return this.days.indexOf(day);
            },
            getSelector: function(day, hour) {
                return this.selection[this.getIndexOfDay(day)][parseInt(hour)];
            },
            selectRectangle: function(origin, width, height, select) {
                for (var i = 0; i < width; ++i) {
                    for (var j = 0; j < height; ++j) {
                        var selector = this.selection[origin.day + i][origin.hour + j];
                        selector.hasPreview = true;
                        if (selector.isSelected === select) {
                            selector.needsCommit = false;
                        } else {
                            selector.isSelected = select;
                            selector.needsCommit = true;
                        }
                    }
                }
            },
            clearSelection: function() {
                for (var i = 0; i < this.selection.length; ++i) {
                    for (var j = 0; j < this.selection[i].length; ++j) {
                        var selector = this.selection[i][j];
                        selector.isSelected = selector.needsCommit
                            ? !selector.isSelected
                            : selector.isSelected;
                        selector.hasPreview = false;
                        selector.needsCommit = false;
                    }
                }
            },
            commitSelection: function() {
                for (var i = 0; i < this.selection.length; ++i) {
                    for (var j = 0; j < this.selection[i].length; ++j) {
                        var selector = this.selection[i][j];
                        selector.hasPreview = false;
                        selector.needsCommit = false;
                    }
                }
            }
        }
    };
</script>

<style lang="scss">
    .schedule-editor {
        display: flex;
        user-select: none;
    }

    .schedule-editor-toolbar {
        flex: none;
        display: flex;
        flex-direction: column;
        justify-content: center
    }

    .schedule-editor-widget {
        flex: 1;
        margin: 0.5em;

        .label {
            text-align: center;
            font-family: monospace;
            flex: 1;
        }

        .day > .label:first-child {
            flex: auto;
        }

        .day {
            display: flex;

            $border: 1px solid #666;
            .hour {
                flex: 1;
                text-align: center;
                border-top: $border;
                border-left: $border;

                &:last-child {
                    border-right: $border;
                }
            }

            &.day:last-child .hour {
                border-bottom: $border;
            }
        }
    }
</style>