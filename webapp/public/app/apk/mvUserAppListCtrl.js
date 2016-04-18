angular.module('app').controller('mvUserAppListCtrl', function($scope,mvIdentity) {
  $scope.identity = mvIdentity;
  //$scope.courses = mvCachedCourses.query();

  $scope.sortOptions = [{value:"title",text: "Sort by Title"},
    {value: "published",text: "Sort by Publish Date"}];
  $scope.sortOrder = $scope.sortOptions[0].value;
});