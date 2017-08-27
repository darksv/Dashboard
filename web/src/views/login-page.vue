<template>
    <div class="login-page">
        <h1 class="page-header">User authentication</h1>
        <p v-if="failed" class="error-message">
            Invalid username and/or password.
        </p>
        <form class="login-form" method="POST" @submit.prevent="login">
            <div>
                <input type="text" class="text-input" name="username" placeholder="Username" :readonly="logging">
            </div>
            <div>
                <input type="password" class="text-input" name="password" placeholder="Password" :readonly="logging">
            </div>
            <div>
                <input type="submit" class="button" value="Login" :readonly="logging">
            </div>
        </form>
    </div>
</template>
<script>
    import loader from './../components/loader.vue';
    import { client, login } from './../api-client';

    export default {
        template: '#login-page',
        data: function () {
            return {
                username: '',
                password: '',
                logging: false,
                failed: false
            };
        },
        methods: {
            login: function () {
                if (this.logging) {
                    return;
                }
                var self = this;
                self.logging = true;
                login(this.username, this.password, function() {
                    self.logging = false;
                    self.failed = false;
                }, function() {
                    self.logging = false;
                    self.failed = true;
                })
            },
            clear: function() {
                this.username = '';
                this.password = '';
            }
        },
        components: {
            loader: loader
        }
    }
</script>
<style lang="scss">
    .login-page {
        width: 30%;
        margin: auto auto;
    }

    .login-form {
        div {
            padding: 0.1em;
            margin: 0.75em 0;
        }
    }

    .error-message {
        color: #FF0000;
        text-align: center;
        font-size: 0.85em;
    }
</style>