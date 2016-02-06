function pythonjson2jsobject(webservice_url){
	//load jquery
	// sample url = http://127.0.0.1:8000/tweets/ws/startAndEnd?start=1453305942&end=1453305949
	var jq = document.createElement('script');
	jq.src = "https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js";
	document.getElementsByTagName('head')[0].appendChild(jq);

	var res;
	$.ajax({
		url: webservice_url, 
		type: 'GET', 
		success: res = function(data){
			//replace url quotes and black slashes
			console.log(JSON.parse(data.replace(/&quot;/g, '\\"').replace(/\\"/g, '"')));
		}
	});
}