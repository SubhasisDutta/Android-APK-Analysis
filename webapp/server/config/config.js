var path = require('path');
var rootPath = path.normalize(__dirname + '/../../');

module.exports = {
  development: {
    db: 'mongodb://localhost/apkanalysis',
    rootPath: rootPath,
    port: process.env.PORT || 3030,
    uploadAPKLocation: 'C:\\Workspace\\Github\\AndroidAPKAnalysis\\webapp\\upload'
  },
  production: {
    rootPath: rootPath,
    db: 'mongodb://jeames:multivision@ds053178.mongolab.com:53178/apkanalysis', //TODO: find the correct string to connect to AWS staging server
    port: process.env.PORT || 80,
    uploadAPKLocation: '/home/bitnami/apps/AndroidAPKAnalysis/webapp/upload'
  }
}