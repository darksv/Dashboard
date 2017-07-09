<template>
    <div class="loader">
        <div class="bounce1" :style="{ backgroundColor: color }"></div>
        <div class="bounce2" :style="{ backgroundColor: color }"></div>
        <div class="bounce3" :style="{ backgroundColor: color }"></div>
    </div>
</template>

<script>
    export default {
        props: {
            color: {
                required: false,
                default: '#FFFFFF'
            }
        }
    };
</script>

<style lang="scss">
    .loader {
        display: flex;
        align-items: center;
        justify-content: center;

        & div {
            width: 18px;
            height: 18px;

            border-radius: 100%;
            display: inline-block;
            -webkit-animation: sk-bouncedelay 1.4s infinite ease-in-out both;
            animation: sk-bouncedelay 1.4s infinite ease-in-out both;
        }

        .bounce1 {
            -webkit-animation-delay: -0.32s;
            animation-delay: -0.32s;
        }

        .bounce2 {
            -webkit-animation-delay: -0.16s;
            animation-delay: -0.16s;
        }
    }

    @-webkit-keyframes sk-bouncedelay {
        0%, 80%, 100% {
            -webkit-transform: scale(0);
        }
        40% {
            -webkit-transform: scale(1.0);
        }
    }

    @keyframes sk-bouncedelay {
        0%, 80%, 100% {
            -webkit-transform: scale(0);
            transform: scale(0);
        }
        40% {
            -webkit-transform: scale(1.0);
            transform: scale(1.0);
        }
    }
</style>