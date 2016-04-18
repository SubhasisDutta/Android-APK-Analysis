var env = process.env.NODE_ENV = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
var Apk = require('mongoose').model('Apk');
var shell = require('shelljs');


exports.getAllApps = function(req, res) {
    Apk.find({}).exec(function(err, collection) {
        res.send(collection);
    })
};

exports.getAppsByUserName = function(req, res) {

    var curentUserName = req.user.username;
    //console.log(curentUserName);
    Apk.find({username:curentUserName}).exec(function(err, collection) {
        //console.log(collection);
        res.send(collection);
    });
}

/*exports.getAppsById = function(req, res) {
    Apk.findOne({_id:req.params.id}).exec(function(err, app) {
        res.send(app);
    });
}*/

/*
exports.createAPKRecord = function(fileName,userName) {
    var userData = req.body;
    userData.username = userData.username.toLowerCase();
    userData.salt = encrypt.createSalt();
    userData.hashed_pwd = encrypt.hashPwd(userData.salt, userData.password);
    User.create(userData, function(err, user) {
        if(err) {
            if(err.toString().indexOf('E11000') > -1) {
                err = new Error('Duplicate Username');
            }
            res.status(400);
            return res.send({reason:err.toString()});
        }
        req.logIn(user, function(err) {
            if(err) {return next(err);}
            res.send(user);
        })
    })
};*/


exports.startTrigger = function(req, res){
    trigerFileProcessing(req.body.file_id);
    res.json({error_code:200,err_desc:"Trigger Started Successfully."});
}

function trigerFileProcessing(file_id){
    console.log(file_id);
    shell.echo('hello world');
    shell.echo(process.cwd());
    shell.cd(process.cwd());
    //console.log(shell.ls());

    //shell.ls('./');
}

function updateSAinDB(id,status,report){
    //update SA in Database
}

function updateSIGinDB(id,status,report){
    //update SIG in Database
}