angular.module('app').controller('mvUserAppListCtrl', function($scope,mvIdentity,$resource,mvNotifier,$location) {
  $scope.userApps =[];
  //$scope.courses = mvCachedCourses.query();
  //console.log(mvIdentity);
  if(mvIdentity.currentUser !== undefined) {
      $scope.identity = mvIdentity;
      var userApps =  $resource("/api/userapps");
      $scope.userApps = userApps.query();
  }
  //console.log($scope.userApps) ;

  $scope.sortOptions = [ {value: "-uploaded_on",text: "Sort by Upload Date"},
      {value:"title",text: "Sort by Title"}];
  $scope.sortOrder = $scope.sortOptions[0].value;


  $scope.triggerProcess = function(id){
     //console.log(id);
      var startAnalysis = $resource("/api/startAnalysis");
      var response = startAnalysis.save({file_id:id},function(){
          //console.log(response);
          mvNotifier.notify("The Analysis of the APK file is in Progress. Please wait for some time for the results.");
          $location.url('/');
      });

  };
});
angular.module('app').controller('mvSAReportDetailCtrl', function($scope,$routeParams,$resource) {
    var report = $resource("/api/sareport/:_id");
    $scope.report = report.get({_id: $routeParams.id});
});
angular.module('app').controller('mvSIGReportDetailCtrl', function($scope,$routeParams,$resource) {
    var report = $resource("/api/sigreport/:_id");
    $scope.report = report.get({_id: $routeParams.id});
});