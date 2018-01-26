import {Channel} from './channel';
import {client as ApiClient} from './api-client.ts';
import {zip} from './functional.ts';

export class ChannelRepository {
    public async getChannels(): Promise<Array<Channel>> {
        return ApiClient
            .get('channels')
            .then(response => response.data.channels)
            .then(channels => channels.map((channel: Channel) => this.loadStats(channel)))
            .then(channels => Promise.all(channels));
    }

    private loadStats(channel: Channel): Promise<Channel> {
        if (!this.hasStats(channel)) {
            channel.items = [];
            return Promise.resolve(channel);
        }
        return this
            .getChannelStats(channel.id)
            .then(items => {
                channel.items = items;
                return channel
            });
    }

    private hasStats(channel: Channel): boolean {
        return channel.enabled && channel.logging_enabled;
    }

    private async getChannelStats(channelId: number): Promise<Array<[string, number]>> {
        const endpoint = '/channel/' + channelId + '/stats';
        const options = {
            params: {
                average: 1
            }
        };
        return ApiClient
            .get(endpoint, options)
            .then(response => {
                const data = response.data;
                return <Array<[string, number]>> zip(data.labels, data.values);
            });
    }
}

