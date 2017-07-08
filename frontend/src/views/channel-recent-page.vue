<template>
    <div class="chart-container">
        <chart :labels="labels" :values="values" :title="title" :color="color" :unit="unit" :maxPoints="60" ></chart>
    </div>
</template>

<script>
    import Chart from '../components/chart.vue';
    import ApiClient from '../api-client.js';

    Array.prototype.last = function() {
        return this[this.length - 1];
    };

    export default {
        props: {
            channelId: {
                required: true
            }
        },
        data: function () {
            return {
                items: [],
                title: '',
                color: '',
                unit: ''
            };
        },
        computed: {
            labels: function () {
                return this.items.map(function(item) {
                    return item[0];
                });
            },
            values: function () {
                return this.items.map(function(item) {
                    return item[1];
                });
            }
        },
        watch: {
            channelId: function() {
                this.update();
            }
        },
        created: function () {
            this.update();
        },
        methods: {
            update: function() {
                var self = this;
                ApiClient.get('/channel/' + this.channelId + '/stats?type=recent').then(function (response) {
                    var data = response.data;
                    self.items = [];
                    for (var i = 0; i < data.labels.length; ++i) {
                        self.add(data.labels[i], data.values[i], true);
                    }
                    self.color = data.color;
                    self.title = data.title;
                    self.unit = data.unit;
                });
            },
            add: function(label, value, ignoreDuplicatedLabel) {
                if (this.items.length > 0 && this.items.last()[0] === label && ignoreDuplicatedLabel === true){
                    return;
                }

                this.items.push([label, value]);
            }
        },
        components: {
            Chart: Chart
        }
    }
</script>