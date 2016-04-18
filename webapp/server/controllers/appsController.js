var Apk = require('mongoose').model('Apk');
var shell = require('shelljs');


exports.getAllApps = function(req, res) {
    Apk.find({}).exec(function(err, collection) {
        res.send(collection);
    })
};

exports.getAppsByUserName = function(req, res) {
    var curentUserName = req.user.username;
    Apk.find({username:curentUserName}).exec(function(err, collection) {
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
    trigerFileProcessing();
    res.json({error_code:200,err_desc:"Trigger Started Successfully."});
}

function trigerFileProcessing(){
    shell.echo('hello world');
    shell.echo(process.cwd());
    shell.cd(process.cwd());
    console.log(shell.ls());

    //shell.ls('./');
}