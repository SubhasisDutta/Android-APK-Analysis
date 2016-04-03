/**
 * Created by Subhasis on 3/25/2016.
 */
var multer = require('multer');
var shell = require('shelljs');

exports.uploadApk = function(req, res) {
    /*Course.findOne({_id:req.params.id}).exec(function(err, course) {
        res.send(course);
    })*/
    var storage = multer.diskStorage({ //multers disk storage settings
        destination: function (req, file, cb) {
            //cb(null, '/home/bitnami/apps/AndroidAPKAnalysis/webapp/upload');
            cb(null, 'C:\\Workspace\\Github\\AndroidAPKAnalysis\\webapp\\upload');
        },
        filename: function (req, file, cb) {
            var datetimestamp = Date.now();
            var fileName=file.originalname.split('.')[0] + '-' + datetimestamp + '.' + file.originalname.split('.')[file.originalname.split('.').length -1];
            cb(null, fileName);
        }
    });
    var upload = multer({ //multer settings
        storage: storage
    }).single('file');

    upload(req,res,function(err){
        //console.log(req);
        //trigerFileProcessing();
        if(err){
            res.json({error_code:500,err_desc:err});
            return;
        }
        res.json({error_code:200,err_desc:"File Uploaded Successfully."});
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