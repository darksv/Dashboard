<template>
    <div class="channel-list">
        <h1 class="page-header">Measuring channels</h1>
        <draggable :list="channels" :options="{ disabled: !canSort }" class="tile-container">
            <tile v-for="channel in channels" :key="channel.id" v-if="channel.enabled || showDisabled" :channel="channel" :user="user" v-on:click.native="showHistory(channel)"></tile>
        </draggable>
    </div>
</template>

<script>
    import Draggable from 'vuedraggable';
    import Tile from '../components/tile.vue';
    import { client as ApiClient} from '../api-client.ts';

    export default {
        props: {
            channels: {
                required: true,
                type: Array
            },
            user: {
                required: true,
                type: Object
            }
        },
        data() {
            return {
                canSort: true,
                showDisabled: false
            }
        },
        watch: {
            channels(items) {
                if (!this.canSort) {
                    return;
                }
                ApiClient.post('/order', {
                    ids: items.map(x => x.id)
                });
            }
        },
        methods: {
            showHistory(channel) {
                if (!channel) {
                    return;
                }

                this.$router.push({
                    name: 'history',
                    query: {
                        ids: channel.id.toString()
                    }
                });
            }
        },
        components: {
            Draggable,
            Tile
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
</style>