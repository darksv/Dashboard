<template>
    <div class="channel-edit-page">
        <h1>Channel editing</h1>
        <form v-on:submit.prevent="submit" class="channel-edit-form">
            <div>
                 <input type="text" class="text-input" v-model="channel.name" placeholder="Name" :readonly="saving">
            </div>
            <div>
                <input type="text" class="text-input" v-model="channel.unit" placeholder="Unit" :readonly="saving">
            </div>
            <div>
                <label>
                    <input type="checkbox" v-model="channel.enabled" :readonly="saving"> Enabled
                </label>
                <label>
                    <input type="checkbox" v-model="channel.logging_enabled" :readonly="saving"> Logging
                </label>
            </div>
            <div class="channel-edit-form-actions">
                <span v-if="saving">Saving...</span>
                <a v-if="!saving" @click="$router.go(-1)" target="_parent">Cancel</a>
                <input type="submit" class="button" value="Save changes" :readonly="saving">
            </div>
            <input type="hidden" name="color" :value="color" />
        </form>

        <hue-slider :hue.sync="hue"></hue-slider>

        <div v-if="triggers">
            <h2>Triggers</h2>
            <div class="channel-edit-triggers">
                <div v-for="trigger in triggers" :key="trigger.id">
                    <div class="info">{{trigger.message}}</div>
                    <div class="extra">
                        <span class="condition">{{trigger.condition}}</span>
                        <span class="interval">500s</span>
                        <span class="notifications">
                            <span class="fa"
                                  :title="(trigger.mail ? 'Disable' : 'Enable') + ' mail notifications'"
                                  :class="{ 'fa-envelope': trigger.mail, 'fa-envelope-o': !trigger.mail }"
                                  @click="trigger.mail = !trigger.mail"></span>
                            <span class="fa"
                                  :title="(trigger.sms ? 'Disable' : 'Enable') + ' SMS notifications'"
                                  :class="{ 'fa-comment': trigger.sms, 'fa-comment-o': !trigger.sms }"
                                  @click="trigger.sms = !trigger.sms"></span>
                            <span class="fa"
                                  :title="(trigger.push ? 'Disable' : 'Enable') + ' push notifications'"
                                  :class="{ 'fa-bell': trigger.push, 'fa-bell-o': !trigger.push }"
                                  @click="trigger.push = !trigger.push"></span>
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import { client as ApiClient } from '../api-client.ts';
    import ScheduleEditor from '../components/schedule-editor.vue';
    import HueSlider from '../components/hue-slider.vue';
    import ColorPalette from '../components/color-palette.vue';
    import tinycolor from 'tinycolor2';

    export default {
        data() {
            return {
                triggers: [],
                saving: false,
                hue: 50
            };
        },
        computed: {
            color() {
                return tinycolor({ h: this.hue, s: 100, v: 100 }).toHexString();
            }
        },
        props: {
            channel: {
                required: true
            }
        },
        watch: {
            color() {
                this.channel.color = this.color;
            }
        },
        created() {
            ApiClient.get('/channel/' + this.channel.id + '/triggers').then(response => {
                this.triggers = response.data.triggers.map(trigger => {
                    trigger.mail = Math.random() < 0.5;
                    trigger.sms = Math.random() < 0.5;
                    trigger.push = Math.random() < 0.5;
                    return trigger;
                });
            });
        },
        methods: {
            submit() {
                if (this.saving) {
                    return;
                }

                this.saving = true;
                ApiClient.post('/channel/' + this.channel.id, this.channel)
                    .then(() => this.saving = false)
                    .catch(() => this.saving = false);
            }
        },
        components: {
            ScheduleEditor,
            ColorPalette,
            HueSlider
        }
    };
</script>

<style lang="scss">
    .channel-edit-page {
        flex: 1;
        max-width: 600px;
    }

    .channel-edit-form {
        width: 100%;
        div {
            padding: 0.1em;
            margin: 0.75em 0;

            label {
                margin: 0.1em 0.2em;
            }
        }
    }

    .channel-edit-form-actions {
        text-align: end;

        a {
            cursor: pointer;
            margin: 0.5em;
        }
    }

    .channel-edit-triggers {
        margin: 0.5em;

        div {
            .info {

            }

            .extra {
                display: flex;

                span {
                     padding: 0.25em;
                }

                .condition {
                    flex: 2;
                }

                .internal {
                    flex: 1;
                }

                .notifications {
                    flex: none;
                    display: inline-block;
                    margin: 5px 0;
                    text-align: center;
                    font-size: 1.25em;
                    user-select: none;
                    span {
                        cursor: pointer;
                    }
                }
            }
        }
    }
</style>