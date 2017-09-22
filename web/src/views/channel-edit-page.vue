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

        <div v-if="watchers">
            <h2>Watchers</h2>
            <div class="channel-edit-watchers">
                <div v-for="watcher in watchers" :key="watcher.id">
                    <div class="info">{{watcher.message}}</div>
                    <div class="extra">
                        <span class="condition">{{watcher.condition}}</span>
                        <span class="interval">500s</span>
                        <span class="notifications">
                            <span class="fa"
                                  :title="(watcher.mail ? 'Disable' : 'Enable') + ' mail notifications'"
                                  :class="{ 'fa-envelope': watcher.mail, 'fa-envelope-o': !watcher.mail }"
                                  @click="watcher.mail = !watcher.mail"></span>
                            <span class="fa"
                                  :title="(watcher.sms ? 'Disable' : 'Enable') + ' SMS notifications'"
                                  :class="{ 'fa-comment': watcher.sms, 'fa-comment-o': !watcher.sms }"
                                  @click="watcher.sms = !watcher.sms"></span>
                            <span class="fa"
                                  :title="(watcher.push ? 'Disable' : 'Enable') + ' push notifications'"
                                  :class="{ 'fa-bell': watcher.push, 'fa-bell-o': !watcher.push }"
                                  @click="watcher.push = !watcher.push"></span>
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import { client as ApiClient } from '../api-client.js';
    import ScheduleEditor from '../components/schedule-editor.vue';
    import HueSlider from '../components/hue-slider.vue';
    import ColorPalette from '../components/color-palette.vue';
    import tinycolor from 'tinycolor2';

    export default {
        data() {
            return {
                watchers: [],
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
            ApiClient.get('/channel/' + this.channel.id + '/watchers').then(response => {
                this.watchers = response.data.watchers.map(watcher => {
                    watcher.mail = Math.random() < 0.5;
                    watcher.sms = Math.random() < 0.5;
                    watcher.push = Math.random() < 0.5;
                    return watcher;
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

    .channel-edit-watchers {
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