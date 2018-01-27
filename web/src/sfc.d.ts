declare module '*.vue' {
    import Vue from 'vue'
    export default Vue
}

declare module 'vue/types/vue' {
    import {Route, Router} from 'vue-router';

    interface Vue {
        $route: Route,
        $router: Router,
        $el: HTMLElement,
    }
}