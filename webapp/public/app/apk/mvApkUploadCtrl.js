angular.module('app').controller('mvApkUploadCtrl', function($scope, mvUser, mvNotifier, $location,
                                                             mvIdentity, Upload, $timeout,$resource) {
  $scope.identity = mvIdentity;
  $scope.apkUpload = function(file) {
    file.upload = Upload.upload({
      url: '/api/apk/upload',
      data: {file: file},
    });

    file.upload.then(function (response) {
        //
        if(response.status === 200){
            //console.log(response);
            if(response.data.code === 510){
                mvNotifier.notify("Only APK files Can be uploaded.");
            }
            if(response.data.code === 200){
                mvNotifier.notify(response.data.err_desc);
                $location.path('/apps');
            }
        }
      $timeout(function () {
        file.result = response.data;
      });
    }, function (response) {
      if (response.status > 0){
          $scope.errorMsg = response.status + ': ' + response.data;
          //console.log(response.status);
          if(response.status == 403){
              mvNotifier.notify("Please Log In to Upload APK files for Analysis.");
          }
          console.log(response.data.code);

      }
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