<template>
    <div class="channel-list">
        <h1 class="page-header">Measuring channels</h1>
        <draggable :list="channels" :options="{ disabled: !enableSort }" :class="{ 'sorting-enabled': enableSort, 'sorting-disabled': !enableSort }" class="tile-container">
            <tile v-for="channel in channels" :key="channel.id" v-if="!channel.disabled || showDisabled" :channel="channel" :user="user" v-on:click.native="showRecent(channel)"></tile>
        </draggable>
        <div class="tile-container-options">
            <label v-if="user.is_authenticated"><input type="checkbox" v-model="enableSort"> Enable channel sorting</label>
            <label><input type="checkbox" v-model="showDisabled"> Show disabled channels</label>
        </div>
    </div>
</template>

<script>
    import Draggable from 'vuedraggable';
    import Tile from '../components/tile.vue';
    import ApiClient from '../api-client.js';

    export default {
        props: {
            channels: {
                required: true,
                type: Array
            },
            user: {
                required: true
            }
        },
        data: function() {
            return {
                enableSort: false,
                showDisabled: false
            }
        },
        watch: {
            channels: function (items) {
                if (!this.enableSort) {
                    return;
                }

                var newOrder = items.map(function (x) {
                    return x.id;
                });

                ApiClient.post('/order?order=' + newOrder.join(','));
            }
        },
        components: {
            draggable: Draggable,
            tile: Tile
        },
        methods: {
            showRecent: function(channel) {
                if (!channel) {
                    return;
                }

                this.$router.push({
                    name: 'channel_recent',
                    params: {
                        channelId: channel.id
                    }
                });
            }
        }
    };
</script>

<style lang="scss">
    .page-header {
        text-align: center;
        margin: 0.5em;
    }

    .tile-container {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        flex-flow: row wrap;
        align-content: center;
        justify-content: center;
        user-select: none;
    }

    .tile-container-options {
        text-align: center;
        margin: 1em 0 0 0;

        label {
            padding: 0.1em;
        }
    }
</style>