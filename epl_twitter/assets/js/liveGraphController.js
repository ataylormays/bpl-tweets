(function(){
	var app = angular.module('liveGraph', []);

	app.controller('liveGraphCtrl', function($scope, $http) {
	    $scope.graphs = [
	    	{name:'counts', data:[1,4,5]},
	    	{name:'sentiment', data:[4,7,8]}
	    ];

	    var dataParser = function(data){
	    	alert(data);
	    };

	    $scope.getData = function(team1, team2){
	    	var fileName = '/static/streamer-'+team1+'-'+team2+'-counts_data.txt';
	    	$http.get(fileName).then(function successCallBack(data){
	    		return dataParser(data);
	    	}, function errorCallBack(error){
	    		alert(error);
	    	});
	    }

	});
})();