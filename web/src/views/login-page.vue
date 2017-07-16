<script>
    export default {
        template: '#login-page',
        data: function () {
            return {
                username: '',
                password: ''
            };
        },
        methods: {
            login: function () {
                this.$router.push('/');
            }
        }
    }
</script>