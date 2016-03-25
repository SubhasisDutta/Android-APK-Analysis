angular.module('app').controller('mvApkUploadCtrl', function($scope, mvUser, mvNotifier, $location,
                                                             mvAuth, Upload, $timeout,$resource) {

  $scope.apkUpload = function(file) {
    file.upload = Upload.upload({
      url: '/api/apk/upload',
      data: {file: file},
    });

    file.upload.then(function (response) {
        mvNotifier.notify(response.data.err_desc);
      $timeout(function () {
        file.result = response.data;
      });
    }, function (response) {
      if (response.status > 0)
        $scope.errorMsg = response.status + ': ' + response.data;
    }, function (evt) {
      // Math.min is to fix IE which reports 200% sometimes
      file.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
    });


    /*var newUserData = {
      username: $scope.email,
      password: $scope.password,
      firstName: $scope.fname,
      lastName: $scope.lname
    };*/
    /*mvAuth.createUser(newUserData).then(function() {
      mvNotifier.notify('User account created!');
      $location.path('/');
    }, function(reason) {
      mvNotifier.error(reason);
    })*/
  }
  $scope.triggerProcessing = function(){
      var trigger = $resource("/api/apk/trigger");
      $scope.trigger = trigger.get(function(response){
          mvNotifier.notify(response.err_desc);
      });
  };
});