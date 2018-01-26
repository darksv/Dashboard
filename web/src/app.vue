<!--suppress TypeScriptPreferShortImport -->
<template>
    <div class="main">
        <loader v-if="isLoading"></loader>
        <transition v-else name="fade" mode="out-in" class="page-content">
            <router-view class="view" :channels="channels" :user="user" :client="client"></router-view>
        </transition>
    </div>
</template>

<script lang="ts">
    import {Component, Vue} from 'vue-property-decorator';
    import {Channel} from './channel.ts';
    import {ChannelRepository} from './channel-repository.ts';
    import {WebSocketClient} from './socket-client.ts';
    import {PageTitleChanger} from './page-title-changer.ts';
    import Loader from './components/loader.vue';

    function zfill(string: string, width: number): string {
        if (width > string.length) {
            return new Array(width - string.length + 1).join('0') + string;
        }
        return string;
    }

    function toHourMinute(date: Date): string {
        return zfill(date.getHours().toString(), 2) + ':' + zfill(date.getMinutes().toString(), 2);
    }

    function lastItem<T>(items: Array<T>): T | undefined {
        return items.length > 0 ? items[items.length - 1] : undefined;
    }

    @Component({components: {Loader}})
    export default class App extends Vue {
        connected: boolean = false;
        channels: Array<Channel> = [];
        user: object = {};
        client: WebSocketClient = new WebSocketClient(
            'wss://' + window.location.host + '/ws',
            connected => this.onConnectionUpdated(connected)
        );
        isLoading: boolean = true;
        channelRepository: ChannelRepository = new ChannelRepository();
        pageTitleChanger: PageTitleChanger = new PageTitleChanger();

        // noinspection JSUnusedLocalSymbols
        private created() {
            this.client.on('channel_updated', this.onChannelUpdated);
            this.client.on('channel_logged', this.onChannelLogged);
        }

        // noinspection JSUnusedLocalSymbols
        private destroyed() {
            this.client.off('channel_updated', this.onChannelUpdated);
            this.client.off('channel_logged', this.onChannelLogged);
        }

        private onConnectionUpdated(isConnected: boolean) {
            if (isConnected) {
                this.pageTitleChanger.clearPrefix();
                this.updateChannels();
            } else {
                this.pageTitleChanger.setPrefix('[Offline] ');
            }
            this.connected = isConnected;
        }

        private onChannelUpdated(data: { channel_uuid, value, timestamp }) {
            let channel = this.getChannelByUuid(data.channel_uuid);
            if (channel === undefined) {
                return;
            }
            channel.value = data.value;
            channel.value_updated = data.timestamp;
        }

        private onChannelLogged(data: { channel_uuid, value, timestamp }) {
            let channel = this.getChannelByUuid(data.channel_uuid);
            if (channel === undefined) {
                return;
            }
            let label = toHourMinute(new Date(data.timestamp));
            if (label !== lastItem(channel.items)[0]) {
                channel.items.push([label, data.value]);
            }
        }

        private getChannelByUuid(uuid: string): Channel | undefined {
            return this.channels.find(channel => uuid === channel.uuid);
        }

        private updateChannels() {
            this.isLoading = true;
            this.channelRepository
                .getChannels()
                .then(channels => {
                    this.channels = channels;
                    this.isLoading = false;
                }, () => {
                    this.isLoading = false;
                });
        }
    }
</script>

<style lang="scss">
    .main {
        min-height: 100%;
        display: flex;
        justify-content: center;
    }

    .view {
        flex: 1;
    }
</style>