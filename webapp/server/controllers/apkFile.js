/**
 * Created by Subhasis on 3/25/2016.
 */
var multer = require('multer');
//var auth = require('../config/auth');
var env = process.env.NODE_ENV = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
var Apk = require('../models/APK');

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
        //console.log(file);
        var fileExtension = file.originalname.split('.')[file.originalname.split('.').length -1].toLowerCase();
        if(fileExtension === "apk"){
            cb(null, true);
        }else{
            cb(new Error('Only APK files Can be uploaded.'));
            cb(null,false);
        }
    }


    var storage = multer.diskStorage({ //multers disk storage settings
        destination: function (req, file, cb) {
            //cb(null, '/home/bitnami/apps/AndroidAPKAnalysis/webapp/upload');
            //console.log(config.uploadAPKLocation);
            cb(null, config.uploadAPKLocation);
        },
        filename: function (req, file, cb) {
            //var fileName=file.originalname.split('.')[0] + '-' + datetimestamp + '.' + file.originalname.split('.')[file.originalname.split('.').length -1];
            var originalName = file.originalname;
            Apk.create({title:originalName,uploaded_on: new Date(),isSA_done :false,isSIG_done: false,username: req.user.username},function(err,record){
                if(err){
                    console.log("DB Insert Failed.")
                    cb(new Error('There was an error in Uploading.')); //TODO : See How to print this error
                    cb(null,false);
                }else{
                    var newFileName = record._id+ '.' + file.originalname.split('.')[file.originalname.split('.').length -1];
                    file.newName = newFileName;
                    console.log(record._id);
                    cb(null, newFileName);
                }
            });
        }
    });
    var upload = multer({ //multer settings
        fileFilter : fileFilterOnlyAPK,
        storage: storage
    }).single('file');

    upload(req,res,function(err){
        //console.log(req);
        //trigerFileProcessing();
        //console.log(err);
        if(err){
            console.log(err);
            console.log("Error Getting Executed");
            res.json({code:510,err_desc:err});
            return;
        }
        res.json({code:200,err_desc:"File Uploaded Successfully."});
    });
};