<template>
    <div class="login-page">
        <form v-if="state == 'default'" class="login-form" method="POST" @submit.prevent="login">
            <div>
                <input type="text" class="text-input" name="username" placeholder="Username" required="required">
            </div>
            <div>
                <input type="password" class="text-input" name="password" placeholder="Password" required="required">
            </div>
            <div>
                <input type="submit" class="button" value="Login">
            </div>
        </form>
        <loader v-if="state == 'logging'"></loader>
        <p v-if="state == 'failed'" class="error-message">
            Wrong username and/or password.<br>
            Please <a @click="state='default'">try again</a>!
        </p>
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
                state: 'default'
            };
        },
        methods: {
            login() {
                if (this.state !== 'default') {
                    return;
                }
                let self = this;
                self.state = 'logging';
                login(this.username, this.password, () => self.state = 'success', () => self.state = 'failed');
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
        }
    }

    .error-message {
        text-align: center;
        font-size: 1.5em;
    }
</style>