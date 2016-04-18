var passport = require('passport');

exports.authenticate = function(req, res, next) {
  req.body.username = req.body.username.toLowerCase();
  var auth = passport.authenticate('local', function(err, user) {
    if(err) {return next(err);}
    if(!user) { res.send({success:false})}
    req.logIn(user, function(err) { //creates a session for the user
      if(err) {return next(err);}
      res.send({success:true, user: user});
    })
  })
  auth(req, res, next);
};

exports.requiresApiLogin = function(req, res, next) {
  if(!req.isAuthenticated()) {
    res.status(403);
    res.end();
  } else {
    next();
  }
};

exports.requiresRole = function(role) {
  return function(req, res, next) {
    if(!req.isAuthenticated() || req.user.roles.indexOf(role) === -1) {
      res.status(403);
      res.end();
    } else {
      next();
    }
  }
}

exports.getLoginUser = function(req,res){
  if(!req.isAuthenticated()) {
    res.send(req.user);
  }else{
    res.send('0');
  }
};

exports.getCurrentUserInfo = function(req){
    if(!req.isAuthenticated()) {
        return req.user;
    }else{
        return '0';
    }
};