<template>
    <div class="channel-custom-page">
        <div class="chart-toolbar">
            <div class="chart-toolbar-fields" v-if="fieldsShown">
                <input type="date" class="input" v-model="from" v-on:keyup.enter="show" :readonly="isLoading"
                       title="Start">
                -
                <input type="date" class="input" v-model="to" v-on:keyup.enter="show" :readonly="isLoading" title="End">
            </div>
            <span class="fa fa-calendar chart-toolbar-button" role="button" v-on:click.prevent="toggleFields"></span>
        </div>
        <loader v-if="isLoading"></loader>
        <chart :responsive="true" :sets="sets" :displayLegend="true" v-else></chart>
    </div>
</template>

<script>
    import Chart from '../components/chart.vue';
    import Loader from '../components/loader.vue';
    import axios from 'axios';
    import {client as ApiClient} from '../api-client.js';
    import {zip} from "../functional";

    function isValidDate(str) {
        return !isNaN(Date.parse(str));
    }

    Date.prototype.addDays = function (n) {
        return new Date(this.getTime() + n * 24 * 3600 * 1000);
    };

    Date.prototype.toShort = function () {
        return this.toISOString().substr(0, 10);
    };

    export default {
        props: {
            channels: {
                required: true
            }
        },
        data() {
            return {
                ids: [],
                from: (new Date).addDays(-30).toShort(),
                to: (new Date).toShort(),
                fieldsShown: false,
                isLoading: true,
                sets: [],
            };
        },
        computed: {
            fromForUrl() {
                return this.from.replace(/-/g, '') + '0000';
            },
            toForUrl() {
                return this.to.replace(/-/g, '') + '2359';
            }
        },
        watch: {
            from() {
                this.periodChanged = true;
            },
            to() {
                this.periodChanged = true;
            }
        },
        created() {
            let query = this.$route.query;
            this.ids = (query.ids || '').split(',').map(id => parseInt(id));
            if (isValidDate(query.from) && isValidDate(query.to)) {
                this.from = new Date(query.from).toShort();
                this.to = new Date(query.to).toShort();
            }

            this.periodChanged = true;
            this.show(true);
        },
        methods: {
            update() {
                let options = {
                    params: {
                        type: 'custom',
                        from: this.fromForUrl,
                        to: this.toForUrl,
                        average: 1440
                    }
                };

                this.isLoading = true;

                let workers = this.ids.map(channelId => {
                    let url = '/channel/' + channelId + '/stats';
                    return ApiClient.get(url, options);
                });

                axios.all(workers).then(responses => {
                    this.sets.length = 0;
                    responses.forEach(response => {
                        // WARNING: shitty workaround
                        // TODO: fix
                        let channelId = parseInt(response.config.url.split('/')[3]),
                            channel = this.channels.find(c => c.id === channelId);

                        let data = response.data;
                        this.sets.push({
                            labels: data.labels,
                            values: data.values,
                            title: data.title,
                            unit: data.unit,
                            color: channel.color
                        });
                    });

                    this.isLoading = false;
                }).catch(() => this.isLoading = false);
            },
            show(replaceLocation) {
                if (this.periodChanged !== true) {
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
                this.update();
            },
            toggleFields() {
                this.fieldsShown = !this.fieldsShown;

                if (!this.fieldsShown) {
                    this.show();
                }
            }
        },
        components: {
            Chart,
            Loader
        }
    };
</script>

<style lang="scss">
    .channel-custom-page {
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
        height: 32px;

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
        margin: 0 0 0 0.25em;
    }
</style>