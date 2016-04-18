/**
 * Created by Subhasis on 3/25/2016.
 */
var multer = require('multer');
var shell = require('shelljs');
//var auth = require('../config/auth');
var env = process.env.NODE_ENV = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];

exports.uploadApk = function(req, res) {
    /*Course.findOne({_id:req.params.id}).exec(function(err, course) {
        res.send(course);
    })*/
    var currentUser = req.user;
    if(currentUser === undefined){
        res.json({error_code:500,err_desc:"Please Login. The Current User is not Authorized."});
        return;
    }

    var fileFilterOnlyAPK = function (req, file, cb) {
        console.log(file);
        var originalName = file.originalname;
        var fileExtension = file.originalname.split('.')[file.originalname.split('.').length -1].toLowerCase();
        if(fileExtension === "apk"){
            //ToDO : log the file in database
            var originalName = file.originalname;


            cb(null, true);
        }else{
            cb(new Error('Only APK files Can be uploaded.'));
            cb(null,false);

        }
    }


    var storage = multer.diskStorage({ //multers disk storage settings
        destination: function (req, file, cb) {
            //cb(null, '/home/bitnami/apps/AndroidAPKAnalysis/webapp/upload');
            console.log(config.uploadAPKLocation);
            cb(null, config.uploadAPKLocation);
        },
        filename: function (req, file, cb) {
            var datetimestamp = Date.now();
            var fileName=file.originalname.split('.')[0] + '-' + datetimestamp + '.' + file.originalname.split('.')[file.originalname.split('.').length -1];
            cb(null, fileName);
        }
    });
    var upload = multer({ //multer settings
        fileFilter : fileFilterOnlyAPK,
        storage: storage
    }).single('file');

    upload(req,res,function(err){
        //console.log(req);
        //trigerFileProcessing();
        console.log(err);
        if(err){
            console.log("Getting Executed");
            res.json({code:510,err_desc:err});
            return;
        }
        res.json({code:200,err_desc:"File Uploaded Successfully."});
    });
};
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