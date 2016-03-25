/**
 * Created by Subhasis on 3/25/2016.
 */
var multer = require('multer');

exports.uploadApk = function(req, res) {
    /*Course.findOne({_id:req.params.id}).exec(function(err, course) {
        res.send(course);
    })*/
    var storage = multer.diskStorage({ //multers disk storage settings
        destination: function (req, file, cb) {
            cb(null, 'C:\\Workspace\\Github\\AndroidAPKAnalysis\\webapp\\upload');
        },
        filename: function (req, file, cb) {
            console.log("fdfd");
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
        if(err){
            res.json({error_code:1,err_desc:err});
            return;
        }
        res.json({error_code:0,err_desc:"File Uploaded Successfully."});
    });



}