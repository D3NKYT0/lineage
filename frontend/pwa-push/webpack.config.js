const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.[contenthash].js',
    clean: true,
    publicPath: '/static/pwa/', // Corrigido para servir do caminho correto
  },
  resolve: {
    extensions: ['.js', '.jsx'],
    fallback: {
      "path": require.resolve("path-browserify"),
      "fs": false,
      "crypto": false,
      "stream": false,
      "buffer": false,
      "util": false,
      "url": false,
      "querystring": false,
      "os": false,
      "assert": false,
      "constants": false,
      "events": false,
      "http": false,
      "https": false,
      "zlib": false,
      "tty": false,
      "vm": false,
      "child_process": false,
      "worker_threads": false,
      "perf_hooks": false,
      "async_hooks": false,
      "inspector": false,
      "trace_events": false,
      "v8": false,
      "domain": false,
      "punycode": false,
      "string_decoder": false,
      "timers": false,
      "tls": false,
      "net": false,
      "dns": false,
      "dgram": false,
      "cluster": false,
      "module": false,
      "process": require.resolve("process/browser"),
    },
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
      {
        test: /\.css$/i,
        use: ['style-loader', 'css-loader'],
      },
      {
        test: /\.(png|jpe?g|gif|svg)$/i,
        type: 'asset/resource',
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
      favicon: false,
    }),
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, 'public'),
    },
    historyApiFallback: true,
    port: 3000,
  },
  externals: {
    'react-icons': 'ReactIcons',
  },
}; 