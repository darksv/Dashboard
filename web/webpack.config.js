const path = require('path');
const webpack = require('webpack');
const DefinePlugin = webpack.DefinePlugin;
const CommonsChunkPlugin = webpack.optimize.CommonsChunkPlugin;
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
    entry: {
        'vendor': ['vue', 'vue-router', 'vuedraggable', 'axios', 'chart.js', 'mqtt', 'tinycolor2'],
        'app': ['./src/index.js', './src/styles.scss']
    },
    devtool: 'source-map',
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: '[name].js'
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader',
                options: {
                    extractCSS: true
                }
            },
            {
                test: /\.scss$/,
                loader: ExtractTextPlugin.extract({
                    fallback: 'style-loader',
                    use: 'css-loader!sass-loader'
                })
            },
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
        }),
        new ExtractTextPlugin('styles.css')
    ]
};