export interface Channel {
    color: string;
    deviceId: number;
    enabled: boolean;
    id: number;
    logging_enabled: boolean;
    name: string;
    type: number;
    unit: string;
    uuid: string;
    value: number;
    value_updated: Date;
    items: Array<[string, number]>;
}