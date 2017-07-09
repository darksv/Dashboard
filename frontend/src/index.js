import Vue from 'vue';
import VueRouter from 'vue-router';
import App from './app.vue';

Vue.use(VueRouter);

function view(name) {
    return require('./views/' + name + '-page.vue').default;
}

const router = new VueRouter({
    routes: [
        { path: '/', component: view('channels'), name: 'home' },
        { path: '/login', component: view('login'), name: 'login' },
        {
            path: '/channel/:channelId',
            component: view('channel'),
            props: true,
            children: [
                {
                    path: 'edit',
                    component: view('channel-edit'),
                    name: 'channel_edit'
                },
                {
                    path: 'recent',
                    component: view('channel-recent'),
                    name: 'channel_recent'
                },
                {
                    path: 'custom',
                    component: view('channel-custom'),
                    name: 'channel_custom'
                }
            ]
        }
    ]
});

new Vue({
    router: router,
    render: function(h) {
        return h(App);
    }
}).$mount('#app');
