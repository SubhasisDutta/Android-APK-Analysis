var express = require('express');
var stylus = require('stylus');
var logger = require('morgan');
var bodyParser=require('body-parser');
var mongoose = require('mongoose');

var env = process.env.NODE_ENV = process.env.NODE_ENV || 'development';

var app = express();

function compile(str,path){
	return stylus(str).set('filename',path);
}

app.set('views',__dirname + '/server/views'); // path to hold the views
app.set('view engine','jade'); //

app.use(logger('dev'));


app.use(bodyParser.urlencoded({extend:true}));
app.use(bodyParser.json());


app.use(stylus.middleware(
{
	src: __dirname + '/public',
	compile: compile
}));

app.use(express.static(__dirname+'/public')); //anything under public routed to this

if(env === 'development'){
	mongoose.connect('mongodb://localhost/multivision');
}else{
	mongoose.connect('mongodb://multivision:multivision@ds045664.mongolab.com:45664/multivision');
}

var db= mongoose.connection;
db.on('error',console.error.bind(console,'connection error...'));
db.once('open',function callback(){
	console.log('multivision db opened');
});

//var documentMessageInsert= {message:"Testing Mongo from MongoLab in Huroku"};


var messageSchema = mongoose.Schema({message:String});  //hold the new schema
var Message = mongoose.model('Message',messageSchema);  //model based on the schema

var mongoMessage;  //hold the data to pull the data from the database
Message.findOne().exec(function(err, messageDoc) {
  mongoMessage = messageDoc.message;
});

app.get('/partials/:partialPath', function(request,response) {
	response.render('partials/'+request.params.partialPath);
});

app.get('/')

app.get('*', function(request,response){
	//response.render('index');
	response.render('index', {
    mongoMessage: mongoMessage
  }); // pass data from mongodb to index
}); //indicate route match all routs

var port = process.env.PORT || 3030;//3030;
app.listen(port);
console.log("Listining to port "+ port+"...");