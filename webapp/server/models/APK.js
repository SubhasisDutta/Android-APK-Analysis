var mongoose = require('mongoose');

var apkSchema = mongoose.Schema({
  title: {type:String, required:'{PATH} is required!'},
  uploaded_on: {type:Date, required:'{PATH} is required!'},
  isSA_done: {type:Boolean, required:'{PATH} is required!'},
  isSIG_done: {type:Boolean, required:'{PATH} is required!'},
  username: {type: String,required: '{PATH} is required!'},
  SA_report : {type : String},
  SIG_report : {type : String},
  apk_category: {type: String},
  tags: [String]
});




var Apk = mongoose.model('Apk', apkSchema);

module.exports = Apk;
