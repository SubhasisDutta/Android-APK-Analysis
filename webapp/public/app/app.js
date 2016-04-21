angular.module('app', ['ngResource', 'ngRoute','ngFileUpload']);

angular.module('app').config(function($routeProvider, $locationProvider) {
  var routeRoleChecks = {
    admin: {auth: function(mvAuth) {
      return mvAuth.authorizeCurrentUserForRoute('admin')
    }},
    user: {auth: function(mvAuth) {
      return mvAuth.authorizeAuthenticatedUserForRoute()
    }}
  }

  $locationProvider.html5Mode(true);
  $routeProvider
      .when('/', { templateUrl: '/partials/main/main', controller: 'mvMainCtrl'})
      .when('/admin/users', { templateUrl: '/partials/admin/user-list',
        controller: 'mvUserListCtrl', resolve: routeRoleChecks.admin
      })
      .when('/signup', { templateUrl: '/partials/account/signup',
        controller: 'mvSignupCtrl'
      })
      .when('/apk/upload', { templateUrl: '/partials/apk/upload',
          controller: 'mvApkUploadCtrl'
      })
      .when('/profile', { templateUrl: '/partials/account/profile',
        controller: 'mvProfileCtrl', resolve: routeRoleChecks.user
      })
      .when('/apps', { templateUrl: '/partials/apk/user-app-list',
        controller: 'mvUserAppListCtrl'
      })
      .when('/apps/SAreport/:id', { templateUrl: '/partials/apk/sareport-details',
        controller: 'mvSAReportDetailCtrl'
      })
      .when('/apps/SIGreport/:id', { templateUrl: '/partials/apk/sigreport-details',
          controller: 'mvSIGReportDetailCtrl'
      })

});

angular.module('app').run(function($rootScope, $location) {
  $rootScope.$on('$routeChangeError', function(evt, current, previous, rejection) {
    if(rejection === 'not authorized') {
      $location.path('/');
    }
  })
})
