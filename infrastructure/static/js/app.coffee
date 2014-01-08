@infrastructure = angular.module('infrastructure',[])


infrastructure.factory 'statsService', ($http) ->
  return {
    statsPromise: $http.get('projects/stats.json')
  }

@infrastructure.controller 'DistrictStatsCtrl', ($scope,statsService) ->
  options = {width: $('#district-info').width(), height: 200, margin: {top: 10, bottom: 20, left: 10, right: 10}}
  $scope.districtChart = new DistrictBarChart("#projects-per-district",options)
  statsService.statsPromise.then (response) ->
    stats = response.data["districts"]
    $scope.stats = (value for key,value of stats)
    $scope.stats = $scope.stats.map (stat,index) -> 
      stat.District = index+1
      stat
    $scope.districtChart.chart($scope.stats,"project_count")
    #$scope.districtChart.chart($scope.stats,"project_costs")
  $scope.$watch 'chart', ->
    $scope.districtChart.chart($scope.stats,"project_#{$scope.chart}") if $scope.chart
