<template>
    <div class="channel-edit-page">
        <h1>Channel editing</h1>
        <form v-on:submit.prevent="save" class="channel-edit-form">
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
        </form>
    </div>
</template>

<script>
    import ApiClient from '../api-client.js';

    export default {
        data: function () {
            return {
                saving: false
            };
        },
        props: {
            channel: {
                required: true
            }
        },
        watch: {
            channel: function () {
                this.update();
            }
        },
        created: function () {
            this.update();
        },
        methods: {
            update: function() {

            },
            save: function () {
                if (this.saving) {
                    return;
                }

                var self = this;
                self.saving = true;
                ApiClient.post('/channel/' + this.channel.id, this.channel).then(function () {
                    self.saving = false;
                }).catch(function () {
                    self.saving = false;
                });
            }
        }
    };
</script>

<style lang="scss">
    .channel-edit-page {
        margin: 0 auto;
    }

    @media (min-width: 600px) {
        .channel-edit-page {
            width: 600px;
        }
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
</style>