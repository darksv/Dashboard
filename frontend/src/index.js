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
        { path: '/channel/:channelId/edit', component: view('channel-edit'), name: 'channel_edit', props: true},
        { path: '/channel/:channelId/recent', component: view('channel-recent'), name: 'channel_recent', props: true },
        { path: '/channel/:channelId/custom', component: view('channel-custom'), name: 'channel_custom', props: true }
    ]
});

var app = new Vue({
    router: router,
    render: function(h) {
        return h(App);
    },
    el: '#app'
});
