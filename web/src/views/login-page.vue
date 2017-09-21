<template>
    <div class="login-page">
        <loader v-if="state === 'logging'"></loader>
        <p v-else-if="state === 'failed'" class="error-message">
            Wrong username and/or password.<br>
            Please <a @click="state='default'">try again</a>!
        </p>
        <form v-else class="login-form" method="POST" @submit.prevent="submit">
            <div>
                <input type="text" class="text-input" placeholder="Username" required="required" v-model="username">
            </div>
            <div>
                <input type="password" class="text-input" placeholder="Password" required="required" v-model="password">
            </div>
            <div>
                <label>
                    <input type="checkbox" v-model="remember">
                    Remember me
                </label>
                <input type="submit" class="button" value="Login">
            </div>
        </form>
    </div>
</template>
<script>
    import Loader from '../components/loader.vue';
    import { client, login } from './../api-client';

    export default {
        data() {
            return {
                username: '',
                password: '',
                remember: false,
                state: 'default'
            };
        },
        methods: {
            submit() {
                if (this.state !== 'default') {
                    return;
                }

                this.state = 'logging';
                login(this.username, this.password, () => this.state = 'success', () => this.state = 'failed');
            },
            clear() {
                this.username = '';
                this.password = '';
            }
        },
        components: {
            Loader
        }
    }
</script>
<style lang="scss">
    .login-page {
        display: flex;
        justify-content: center;
        align-items: center;
        flex: 1;
    }

    .login-form {
        max-width: 600px;

        div {
            padding: 0.1em;
            margin: 0.75em 0;

            &:last-child {
                display: flex;
                flex-direction: row;
                align-items: center;

                :nth-child(1) {
                    flex: auto;
                }

                :nth-child(2) {
                    flex: 1;
                }
            }
        }
    }

    .error-message {
        text-align: center;
        font-size: 1.5em;
    }
</style>