var auth = require('./auth'),
  users = require('../controllers/users'),
  apkFile = require('../controllers/apkFile'),//courses = require('../controllers/courses'),
  appsController = require('../controllers/appsController'),
  mongoose = require('mongoose');
  //User = mongoose.model('User');


module.exports = function(app) {

  app.get('/api/users', auth.requiresRole('admin'), users.getUsers);
  app.post('/api/users', users.createUser);
  app.put('/api/users', users.updateUser);

  //app.get('/api/courses', courses.getCourses);
  //app.get('/api/courses/:id', courses.getCourseById);

  app.post('/api/apk/upload',auth.requiresApiLogin, apkFile.uploadApk);

  app.get('/api/userapps',auth.requiresApiLogin, appsController.getAppsByUserName);
  app.get('/api/apps', auth.requiresRole('admin'), appsController.getAllApps);
  app.post('/api/startAnalysis',auth.requiresApiLogin,appsController.startTrigger);

  app.get('/api/sareport/:_id',auth.requiresApiLogin,appsController.getSAReport);
  app.get('/api/sigreport/:_id',auth.requiresApiLogin,appsController.getSIGReport);
  app.get('/api/sareportFile/:_id',auth.requiresApiLogin,appsController.getSAReportFile);
  app.get('/api/satree/:_id/:_seedId',auth.requiresApiLogin,appsController.getSAReportTree);

  app.get('/partials/*', function(req, res) {
    res.render('../../public/app/' + req.params[0]);
  });

  app.post('/login', auth.authenticate);
  // route to test if the user is logged in or not
  app.get('/getCurrentUser', auth.getLoginUser);

  app.post('/logout', function(req, res) {
    req.logout();
    res.end();
  });

  app.all('/api/*', function(req, res) {
    res.send(404);
  });

  app.get('*', function(req, res) {
    res.render('index', {
      bootstrappedUser: req.user
    });
  });
}