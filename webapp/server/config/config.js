var path = require('path');
var rootPath = path.normalize(__dirname + '/../../');

module.exports = {
  development: {//'mongodb://subhasis:subhasis@ec2-52-91-127-226.compute-1.amazonaws.com:27017/apkanalysis',
    db: 'mongodb://localhost/apkanalysis',//mongodb://subhasis:subhasis@ec2-52-91-127-226.compute-1.amazonaws.com:27017/apkanalysis
    rootPath: rootPath,
    port: process.env.PORT || 3030,
    uploadAPKLocation: 'C:\\FileRepo\\apkupload',
    apkTool: 'C:\\Github\\AndroidAPKAnalysis\\apktool\\apktool',
    apkDecompileLocation: 'C:\\FileRepo\\apkupload',//'C:\\FileRepo\\apkdecompile',
    SA_script_location: 'C:\\Github\\AndroidAPKAnalysis\\SMVHunter\\static',
    SA_output_location: 'C:\\FileRepo\\saoutput',
    SIG_script_location: 'C:\\Github\\AndroidAPKAnalysis\\smartInputGeneration',
    SIG_output_location: 'C:\\FileRepo\\sigoutput',
    play_category_finder: 'https://play.google.com/store/apps/details?id='
  },
  production: {
    rootPath: rootPath,
    db: 'mongodb://localhost/apkanalysis', //TODO: find the correct string to connect to AWS staging server
    port: process.env.PORT || 3030,
    uploadAPKLocation: '/home/bitnami/file_repo/apkupload',
    apkTool: '/home/bitnami/AndroidAPKAnalysis/SMVHunter/apktool/apktool',
    apkDecompileLocation: '/home/bitnami/file_repo/apkupload',
    SA_script_location: '/home/bitnami/AndroidAPKAnalysis/SMVHunter/static',
    SA_output_location: '/home/bitnami/file_repo/saoutput',
    SIG_script_location: '/home/bitnami/AndroidAPKAnalysis/smartInputGeneration',
    SIG_output_location: '/home/bitnami/file_repo/sigoutput',
    play_category_finder: 'https://play.google.com/store/apps/details?id='
  }
}