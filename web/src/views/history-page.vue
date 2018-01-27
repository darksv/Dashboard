<template>
    <div class="history-page">
        <div class="chart-toolbar">
            <div class="chart-toolbar-fields" v-if="optionsVisible">
                <input type="date" class="input" v-model="from" v-on:keyup.enter="show" :readonly="isLoading"
                       title="Start">
                —
                <input type="date" class="input" v-model="to" v-on:keyup.enter="show" :readonly="isLoading" title="End">
            </div>
            <span class="fa fa-cog chart-toolbar-button" role="button" title="Show options"
                  v-on:click.prevent="toggleOptions"></span>
            <ul v-if="optionsVisible" class="chart-visible-channels">
                <li v-for="channel in channels" :key="channel.id" v-if="channel.enabled" class="channel">
                    <label class="channel-label" @click="toggleVisibility(channel.id)">
                        <span class="channel-selector" role="checkbox"
                              :style="{
                                    backgroundColor: isVisible(channel.id) ? channel.color : 'transparent',
                                    border: '1px solid ' + channel.color,
                              }"></span>
                        <span>{{ channel.name || channel.uuid }}</span>
                    </label>
                </li>
            </ul>
            <div class="chart-predefined-periods" v-if="optionsVisible">
                <router-link v-for="period in periods" :key="period"
                             :to="createRouteFor(period)"
                             tag="span" class="period">
                    {{period}}
                </router-link>
            </div>
        </div>
        <loader v-if="isLoading"></loader>
        <chart :responsive="true" :sets="sets" :displayLegend="true" v-else-if="anyVisible"></chart>
        <div class="history-page-info" v-else>
            <p class="history-page-info-content">
                Select at least one channel using the <span class="fa fa-cog"></span> button in the top right corner.
            </p>
        </div>
    </div>
</template>

<script lang="ts">
    import Chart from '../components/chart.vue';
    import Loader from '../components/loader.vue';
    import {client as ApiClient} from '../api-client.ts';
    import {convertShorthandIntoDays, addDaysTo, shortenedDate, isValidDate} from '../date-utils.ts';

    export default {
        props: {
            channels: {
                required: true
            }
        },
        data() {
            return {
                ids: [],
                from: shortenedDate(addDaysTo(new Date, -30)),
                to: shortenedDate(new Date),
                optionsVisible: false,
                isLoading: true,
                sets: [],
                cache: {},
                periods: '1d 1w 1m 3m 6m 1y'.split(' '),
            };
        },
        computed: {
            fromForUrl() {
                return this.from.replace(/-/g, '') + '0000';
            },
            toForUrl() {
                return this.to.replace(/-/g, '') + '2359';
            },
            anyVisible() {
                return this.ids.length > 0;
            }
        },
        watch: {
            from() {
                this.periodChanged = true;
            },
            to() {
                this.periodChanged = true;
            },
            ids() {
                this.idsChanged = true;
                this.show(true);
            },
            $route(route) {
                if (route.name !== 'history') {
                    return;
                }

                let query = route.query;
                this.from = shortenedDate(new Date(query.from));
                this.to = shortenedDate(new Date(query.to));
                this.show(false);
            }
        },
        created() {
            let query = this.$route.query;
            this.ids = (query.ids || '')
                .split(',')
                .map(id => parseInt(id))
                .filter(id => !isNaN(id));

            if (isValidDate(query.from) && isValidDate(query.to)) {
                this.from = shortenedDate(new Date(query.from));
                this.to = shortenedDate(new Date(query.to));
            }

            this.periodChanged = true;
            this.idsChanged = true;
            this.show(true);
        },
        methods: {
            update() {
                let options = {
                    params: {
                        from: this.fromForUrl,
                        to: this.toForUrl,
                        average: 60 // in minutes
                    }
                };

                this.isLoading = true;
                const requests = this.ids.map(id => {
                    let endpoint = '/channel/' + id + '/stats';
                    return ApiClient.get(endpoint, options)
                        .then(response => {
                            let channel = this.channels.find(c => c.id === id);
                            let data = response.data;
                            return {
                                labels: data.labels,
                                values: data.values,
                                title: data.title,
                                unit: data.unit,
                                color: channel.color
                            };
                        });
                });
                Promise
                    .all(requests)
                    .then(sets => {
                        this.sets.length = 0;
                        for (let set of sets) {
                            this.sets.push(set);
                        }
                        this.isLoading = false;
                    }, () => this.isLoading = false);
            },
            show(replaceLocation) {
                if (this.periodChanged !== true && this.idsChanged !== true) {
                    return;
                }

                let location = {
                    name: 'history',
                    query: {
                        from: this.from,
                        to: this.to,
                        ids: this.ids.join(',')
                    }
                };

                if (replaceLocation) {
                    this.$router.replace(location);
                } else {
                    this.$router.push(location);
                }

                this.periodChanged = false;
                this.idsChanged = false;
                this.update();
            },
            toggleOptions() {
                this.optionsVisible = !this.optionsVisible;
                if (!this.optionsVisible) {
                    this.show(false);
                }
            },
            isVisible(channelId) {
                return this.ids.indexOf(channelId) !== -1;
            },
            toggleVisibility(channelId) {
                let index = this.ids.indexOf(channelId);
                if (index === -1) {
                    this.ids.push(channelId);
                } else {
                    this.ids.splice(index, 1);
                }
            },
            createRouteFor(period: string): object {
                let numberOfDays = convertShorthandIntoDays(period),
                    periodEnd = new Date(),
                    periodStart = addDaysTo(periodEnd, -numberOfDays);

                return {
                    name: 'history',
                    query: {
                        from: shortenedDate(periodStart),
                        to: shortenedDate(periodEnd),
                        ids: this.ids.join(',')
                    }
                };
            }
        },
        components: {
            Chart,
            Loader
        }
    };
</script>

<style lang="scss">
    .history-page {
        flex: 1;
        display: flex;

        .loader {
            flex: 1;
        }
    }

    .chart-options {
        margin: 0.5em;
    }

    .chart-toolbar {
        position: absolute;
        top: 0;
        right: 0;
        display: block;
        background: #000000;

        .input {
            font-size: 1em;
        }
    }

    .chart-toolbar-fields {
        display: inline-block;
    }

    .chart-toolbar-button {
        display: inline-block;
        cursor: pointer;
        vertical-align: middle;
        margin: 0.3em;
    }

    .chart-visible-channels {
        background: #000000;
        user-select: none;
        margin: 0;
        padding: 0;
        font-size: 0.8em;

        .channel {
            cursor: default;
            list-style: none;
            margin: 0.1em 0;

            .channel-label {
                cursor: inherit;
                display: inline-block;

                & > span:last-child {
                    margin: 1px;
                }
            }

            .channel-selector {
                border: 1px solid;
                width: 18px;
                height: 12px;
                display: inline-block;
                vertical-align: -2px;
            }
        }
    }

    .chart-predefined-periods {
        display: flex;

        & > .period {
            margin: 0.1em;
            flex: 1;
            text-align: center;
            cursor: pointer;
        }
    }

    .history-page-info {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;

        .history-page-info-content {
            font-style: italic;
            color: #bbb;
            user-select: none;
            text-align: center;
            width: 100%
        }
    }
</style>