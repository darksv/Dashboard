<template>
    <div class="chart-container">
        <div class="chart-toolbar">
            <div class="chart-toolbar-fields" v-if="fieldsShown">
                <input type="date" class="input" v-model="from" v-on:keyup.enter="show" :readonly="!fieldsEnabled">
                -
                <input type="date" class="input" v-model="to" v-on:keyup.enter="show" :readonly="!fieldsEnabled">
            </div>
            <span class="fa fa-calendar chart-toolbar-button" role="button" v-on:click.prevent="toggleFields"></span>
        </div>
        <chart :points="points" :title="title" :unit="unit" ></chart>
    </div>
</template>

<script>
    import Chart from '../components/chart.vue';
    import ApiClient from '../api-client.js';

    function isValidDate(str) {
        return !isNaN(Date.parse(str));
    }

    Date.prototype.addDays = function(n) {
        return new Date(this.getTime() + n * 24 * 3600 * 1000);
    };

    export default {
        data: function () {
            return {
                points: [],
                title: '',
                unit: '',
                from: '',
                to: '',
                fieldsEnabled: true,
                fieldsShown: false,
                maxPoints: 60
            };
        },
        props: {
            channel: {
                required: true
            }
        },
        computed: {
            formattedFrom: function () {
                return this.from.replace(/-/g, '') + '0000';
            },
            formattedTo: function () {
                return this.to.replace(/-/g, '') + '2359';
            }
        },
        watch: {
            channel: function() {
                this.update();
            },
            from: function () {
                this.periodChanged = true;
            },
            to: function () {
                this.periodChanged = true;
            }
        },
        created: function () {
            var dateFrom, dateTo;

            if (isValidDate(this.$route.query.from) && isValidDate(this.$route.query.to)) {
                dateFrom = new Date(this.$route.query.from);
                dateTo = new Date(this.$route.query.to);
            } else {
                dateFrom = (new Date).addDays(-30);
                dateTo = (new Date);
            }

            this.periodChanged = true;
            this.from = dateFrom.toISOString().substr(0, 10);
            this.to = dateTo.toISOString().substr(0, 10);
            this.show();
        },
        methods: {
            update: function() {
                var url = '/channel/' + this.channel.id + '/stats?type=custom&from=' + this.formattedFrom + '&to=' + this.formattedTo;
                var self = this;
                self.fieldsEnabled = false;
                ApiClient.get(url).then(function (response) {
                    var data = response.data;
                    self.items = [];
                    for (var i = 0; i < data.labels.length; ++i) {
                        self.items.push([data.labels[i], data.values[i]]);
                    }
                    self.title = data.title;
                    self.unit = data.unit;
                    self.fieldsEnabled = true;
                });
            },
            show: function () {
                if (this.periodChanged !== true) {
                    return;
                }

                this.$router.push({
                    name: 'channel_custom',
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
            toggleFields: function () {
                this.fieldsShown = !this.fieldsShown;

                if (!this.fieldsShown) {
                    this.show();
                }
            }
        },
        components: {
            chart: Chart
        }
    };
</script>

<style lang="scss">
    .chart-options {
        margin: 0.5em;
    }

    .chart-container {
        flex: 2;
        margin: 1em 1em 0 1em;
        height: 100%;
        position: relative;
        user-select: none;
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