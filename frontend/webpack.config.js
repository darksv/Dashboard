const path = require('path');
const webpack = require('webpack');
const DefinePlugin = webpack.DefinePlugin
const CommonsChunkPlugin = webpack.optimize.CommonsChunkPlugin;
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');

module.exports = {
    entry: {
        'app': './src/index.js',
        'vendor': ['vue', 'vue-router', 'vuedraggable', 'axios', 'chart.js', 'mqtt']
    },
    devtool: "source-map",
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, '../static')
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader',
            }
        ]
    },
    plugins: [
        new CommonsChunkPlugin({
			names: ['vendor'],
			minChunks: Infinity
		}),
        new DefinePlugin({
            'process.env': {
                NODE_ENV: '"production"'
            }
        }),
        new UglifyJSPlugin({
            include: /\.min\.js$/,
            minimize: true
        })
    ]
};