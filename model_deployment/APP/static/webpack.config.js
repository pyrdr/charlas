var HTMLWebpackPlugin = require('html-webpack-plugin');
var HTMLWebpackPluginConfig = new HTMLWebpackPlugin({
    template: __dirname +  '/index.html',
    filename: 'index.html',
    inject: 'body'
});

module.exports = {
    entry: __dirname + '/index.js',
    module: {
	loaders: [
       {
	 test: /\.js$/,
	 exclude: /node_modules/,
	 loader: 'babel-loader'
       }
    ,
    {
        test: /\.css/,
        loaders: ['style-loader', 'css-loader'],
      },


  ]
  },
  output: {
	filename: 'transformed.js',
	path: __dirname + '/build'
  },
  plugins: [HTMLWebpackPluginConfig]
};
