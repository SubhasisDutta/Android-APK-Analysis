angular.module('app',['ngResource','ngRoute']); //angular dependency modules

//client side routs inside this file by calling the config function
angular.module('app').config(function($routeProvider, $locationProvider) {
    $locationProvider.html5Mode(true);//location provider to turn on html5 mode for routing
    $routeProvider
        .when('/', { templateUrl: '/partials/main', controller: 'mainCtrl'});
});

angular.module('app').controller('mainCtrl', function($scope) {
    $scope.myVar = "Hello Angular";
});