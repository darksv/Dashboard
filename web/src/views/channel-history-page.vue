<template>
    <div class="channel-custom-page">
        <div class="chart-toolbar">
            <div class="chart-toolbar-fields" v-if="fieldsShown">
                <input type="date" class="input" v-model="from" v-on:keyup.enter="show" :readonly="isLoading" title="Start">
                -
                <input type="date" class="input" v-model="to" v-on:keyup.enter="show" :readonly="isLoading" title="End">
            </div>
            <span class="fa fa-calendar chart-toolbar-button" role="button" v-on:click.prevent="toggleFields"></span>
        </div>
        <loader v-if="isLoading"></loader>
        <chart :responsive="true" :points="points" :title="title" :unit="unit" v-else></chart>
    </div>
</template>

<script>
    import Chart from '../components/chart.vue';
    import Loader from '../components/loader.vue';
    import { client as ApiClient } from '../api-client.js';
    import {zip} from "../functional";

    function isValidDate(str) {
        return !isNaN(Date.parse(str));
    }

    Date.prototype.addDays = function(n) {
        return new Date(this.getTime() + n * 24 * 3600 * 1000);
    };

    Date.prototype.toShort = function () {
        return this.toISOString().substr(0, 10);
    };

    export default {
        data() {
            return {
                points: [],
                title: '',
                unit: '',
                from: (new Date).addDays(-30).toShort(),
                to: (new Date).toShort(),
                fieldsShown: false,
                isLoading: true,
                maxPoints: 60
            };
        },
        props: {
            channel: {
                required: true
            }
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
            channel() {
                this.update();
            },
            from() {
                this.periodChanged = true;
            },
            to() {
                this.periodChanged = true;
            }
        },
        created() {
            let query = this.$route.query;
            if (isValidDate(query.from) && isValidDate(query.to)) {
                this.from = new Date(query.from).toShort();
                this.to = new Date(query.to).toShort();
            }

            this.periodChanged = true;
            this.show();
        },
        methods: {
            update() {
                let url = '/channel/' + this.channel.id + '/stats',
                    options = {
                        params: {
                            type: 'custom',
                            from: this.fromForUrl,
                            to: this.toForUrl,
                            average: 1440
                        }
                    };

                this.isLoading = true;
                ApiClient.get(url, options).then(response => {
                    let data = response.data;
                    this.points = zip(data.labels, data.values);
                    this.title = data.title;
                    this.unit = data.unit;
                    this.isLoading = false;
                }).catch(() => this.isLoading = false);
            },
            show() {
                if (this.periodChanged !== true) {
                    return;
                }

                this.$router.push({
                    name: 'channel_history',
                    query: {
                        from: this.from,
                        to: this.to
                    }
                });
                this.periodChanged = false;

                if (this.channel) {
                    this.update();
                }
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