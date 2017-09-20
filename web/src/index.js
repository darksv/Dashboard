import Vue from 'vue';
import VueRouter from 'vue-router';
import App from './app.vue';
import ChannelsPage from './views/channels-page.vue';
import LoginPage from './views/login-page.vue';
import ExperimentsPage from './views/experiments-page.vue';
import ChannelPage from './views/channel-page.vue';
import ChannelEditPage from './views/channel-edit-page.vue';
import ChannelRecentPage from './views/channel-recent-page.vue';
import ChannelCustomPage from './views/channel-custom-page.vue';

Vue.use(VueRouter);

const router = new VueRouter({
    routes: [
        {
            path: '/',
            component: ChannelsPage,
            name: 'home'
        },
        {
            path: '/login',
            component: LoginPage,
            name: 'login'
        },
        {
            path: '/experiments',
            component: ExperimentsPage,
            name: 'experiments'
        },
        {
            path: '/channel/:channelId',
            component: ChannelPage,
            props: true,
            children: [
                {
                    path: 'edit',
                    component: ChannelEditPage,
                    name: 'channel_edit'
                },
                {
                    path: 'recent',
                    component: ChannelRecentPage,
                    name: 'channel_recent'
                },
                {
                    path: 'custom',
                    component: ChannelCustomPage,
                    name: 'channel_custom'
                }
            ]
        }
    ]
});

router.beforeEach((to, from, next) => {
    if (to.name === null) {
        next(false);
    } else {
        next();
    }
});

new Vue({
    el: '#app',
    router,
    render: h => h(App)
});
