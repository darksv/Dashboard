<template>
    <div>
        <form v-on:submit.prevent="save">
            <input type="text" v-model="channel.name" placeholder="Nazwa"><br>
            <input type="text" v-model="channel.unit" placeholder="Jednostka"><br>
            <input type="checkbox" v-model="channel.disabled" placeholder="Wyłączony"><br>
            <input type="color" v-model="channel.color" placeholder="Kolor"><br>
            <input type="submit" value="Zapisz">
        </form>
    </div>
</template>

<script>
    import ApiClient from '../api-client.js';

    export default {
        data: function () {
            return {
                channel: {}
            };
        },
        props: {
            channel: {
                required: true
            }
        },
        watch: {
            channelId: function () {
                this.update();
            }
        },
        created: function () {
            this.update();
        },
        methods: {
            update: function() {
                var self = this;
                ApiClient.get('/channel/' + this.channelId).then(function (response) {
                    self.channel = response.data;
                });
            },
            save: function () {
                ApiClient.post('/channel/' + this.channelId, this.channel);
            }
        }
    };
</script>