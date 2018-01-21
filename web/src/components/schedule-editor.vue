<template>
    <div class="schedule-editor">
        <div class="schedule-editor-widget">
            <div class="day">
                <div class="label">&nbsp;&nbsp;&nbsp;</div>
                <div v-for="hour in hourLabels" v-bind:key="hour" class="label label-hour">{{hour}}</div>
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
                <div class="dummy-hour"></div>
            </div>
        </div>
        <div class="schedule-editor-toolbar">
            <span class="fa" :class="{ 'fa-check-circle-o': include, 'fa-times-circle-o': !include }"
                  title="Include hours" @click="include=!include"></span>
        </div>
    </div>
</template>

<script>
    import {clamp} from '../math-utils.js';

    function hasParentWithClass(element, className) {
        while (element = element.parentNode) {
            if (element.classList !== undefined && element.classList.contains(className)) {
                return true;
            }
        }
        return false;
    }

    export default {
        props: {
            hourFormat: {
                required: false,
                default: '24h',
                validator(value) {
                    return ['12h', '24h'].indexOf(value) >= 0;
                }
            },
            selection: {
                required: false,
                default: {}
            }
        },
        data() {
            let days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                hours = Array.from(Array(24).keys());

            return {
                days: days,
                hours: hours,
                isPressed: false,
                include: false,
                selectors: days.map(
                    () => hours.map(
                        () => ({
                            isSelected: true,
                            hasPreview: false,
                            needsCommit: false
                        })
                    )
                ),
                selectionOrigin: null
            };
        },
        computed: {
            selected() {
                return this.selectors
                    .map(
                        day => day
                            .map((x, i) => ({hour: i, isSelected: x.isSelected}))
                            .filter(x => x.isSelected)
                            .map(x => x.hour)
                    );
            },
            hourLabels() {
                let hours = this.hours.map(x => x);
                hours.push(24);
                return hours.map(hour => this.formatHour(hour));
            }
        },
        watch: {
            selection() {
                for (let day in this.days) {
                    for (let hour in this.hours) {
                        this.selectors[day][hour].isSelected = this.selection[day].indexOf(hour) !== -1;
                    }
                }
            }
        },
        mounted() {
            let self = this;

            this.mouseUp = function (e) {
                e.preventDefault();
                self.isPressed = false;
                self.selectionOrigin = null;
                self.commitSelection();

                document.removeEventListener('mouseup', self.mouseUp);
                document.removeEventListener('mousemove', self.mouseMove);
            };

            this.mouseDown = function (e) {
                if (e.target !== null && self.isElementPartOfOtherInstance(e.target)) {
                    return;
                }

                e.preventDefault();
                self.isPressed = true;
                self.selectionOrigin = {
                    day: parseInt(e.target.dataset.day),
                    hour: parseInt(e.target.dataset.hour)
                };
                self.updateSelection(e.target, e.clientX, e.clientY);

                document.addEventListener('mouseup', self.mouseUp);
                document.addEventListener('mousemove', self.mouseMove);
            };

            this.mouseMove = function (e) {
                if (self.isPressed && e.button === 0) {
                    e.preventDefault();
                    self.updateSelection(e.target, e.clientX, e.clientY);
                }
            };

            this.touchStart = function (e) {
                if (e.target !== null && self.isElementPartOfOtherInstance(e.target)) {
                    return;
                }

                self.isPressed = true;
                self.selectionOrigin = {
                    day: parseInt(e.target.dataset.day),
                    hour: parseInt(e.target.dataset.hour)
                };
                self.updateSelection(e.target, e.changedTouches[0].clientX, e.changedTouches[0].clientY);

                document.addEventListener('touchmove', self.touchMove);
                document.addEventListener('touchend', self.touchEnd);
            };

            this.touchMove = function (e) {
                if (self.isPressed) {
                    let clientX = e.changedTouches[0].clientX,
                        clientY = e.changedTouches[0].clientY,
                        target = document.elementFromPoint(clientX, clientY);

                    self.updateSelection(target, clientX, clientY);
                }
            };

            this.touchEnd = function () {
                self.isPressed = false;
                self.selectionOrigin = null;
                self.commitSelection();

                document.removeEventListener('touchmove', self.touchMove);
                document.removeEventListener('touchend', self.touchEnd);
            };

            document.addEventListener('mousedown', this.mouseDown);
            document.addEventListener('touchstart', this.touchStart);
        },
        destroy() {
            document.removeEventListener('mousedown', this.mouseDown);
            document.removeEventListener('touchstart', this.touchStart);
        },
        methods: {
            getIndexOfDay(day) {
                return this.days.indexOf(day);
            },
            getSelector(day, hour) {
                return this.selectors[this.getIndexOfDay(day)][parseInt(hour)];
            },
            formatHour(hour) {
                if (this.hourFormat === '24h') {
                    return hour;
                }
                hour = hour % 24;
                if (hour === 0) {
                    return '12am';
                } else if (hour < 12) {
                    return hour + 'am';
                } else if (hour === 12) {
                    return '12pm';
                } else {
                    return (hour - 12) + 'pm';
                }
            },
            selectRectangle(origin, width, height, select) {
                for (let i = 0; i < width; ++i) {
                    for (let j = 0; j < height; ++j) {
                        let selector = this.selectors[origin.day + i][origin.hour + j];
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
            clearSelection() {
                for (let i = 0; i < this.selectors.length; ++i) {
                    for (let j = 0; j < this.selectors[i].length; ++j) {
                        let selector = this.selectors[i][j];
                        selector.isSelected = selector.needsCommit
                            ? !selector.isSelected
                            : selector.isSelected;
                        selector.hasPreview = false;
                        selector.needsCommit = false;
                    }
                }
            },
            commitSelection() {
                for (let i = 0; i < this.selectors.length; ++i) {
                    for (let j = 0; j < this.selectors[i].length; ++j) {
                        const selector = this.selectors[i][j];
                        selector.hasPreview = false;
                        selector.needsCommit = false;
                    }
                }

                this.$emit('update:selection', this.selectors.map(day => {
                    const values = [];
                    for (let i = 0; i < day.length; ++i) {
                        if (day[i].isSelected) {
                            values.push(i);
                        }
                    }
                    return values;
                }));
            },
            updateSelection(target, clientX, clientY) {
                let day, hour;
                if (target === null || target === document || this.isElementPartOfOtherInstance(target) || target.className.indexOf('hour') === -1) {
                    // Find bounding rectangle of the all selectors based on first and the last selector rectangles.
                    const selectors = this.$el.querySelectorAll('.hour'),
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
                    hour = clamp(0, 23, Math.floor((clientX - selectorsRect.left) / ((selectorsRect.width / this.hours.length))));
                    day = clamp(0, 6, Math.floor((clientY - selectorsRect.top) / ((selectorsRect.height / this.days.length))));
                } else {
                    const data = target.dataset;
                    day = parseInt(data.day);
                    hour = parseInt(data.hour);
                }

                const start = this.selectionOrigin,
                    left = Math.min(start.hour, hour),
                    top = Math.min(start.day, day),
                    right = Math.max(start.hour, hour),
                    bottom = Math.max(start.day, day);
                this.clearSelection();
                this.selectRectangle({day: top, hour: left}, bottom - top + 1, right - left + 1, this.include);
            },
            isElementPartOfOtherInstance(element) {
                return hasParentWithClass(element, 'schedule-editor') && !this.$el.contains(element);
            }
        }
    };
</script>

<style lang="scss">
    .schedule-editor {
        display: flex;
        user-select: none;
        touch-action: none;
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

            &.label-hour {
                transform: translateX(-50%);
            }
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

            }

            &.day:last-child .hour {
                border-bottom: $border;
            }

            .dummy-hour {
                flex: 1;
                border-left: $border;
            }
        }
    }
</style>