/*
  Used to assert conditinos.
  Probably there is a more canonical way to do this.
*/
function assert(condition, message) {
    if (!condition) {
	throw new Error(message);
    }
}

function toHM(time) {
    function fix(x) {
	if (x < 10) { return "0" + x.toString(); }
	else { return x.toString(); }
    }
    //var S = fix(time % 60);
    time = Math.floor(time / 60);
    var M = fix(time % 60);
    time = Math.floor(time / 60);
    var H = fix(time % 24);
    return (H + ":" + M);
}

function fromHMS(timeString) {
    var split = timeString.split(":");
    return (
	parseInt(split[0]) * 3600 +
	    parseInt(split[1]) * 60 +
	    parseInt(split[2]));
}

function convertTimestampToLocalTime(timestamp) {
  var d = new Date(timestamp * 1000),	// Convert the passed timestamp to milliseconds
		yyyy = d.getFullYear(),
		mm = ('0' + (d.getMonth() + 1)).slice(-2),	// Months are zero based. Add leading 0.
		dd = ('0' + d.getDate()).slice(-2),			// Add leading 0.
		hh = d.getHours(),
		h = hh,
		min = ('0' + d.getMinutes()).slice(-2),		// Add leading 0.
		s = ('0' + d.getSeconds()).slice(-2),		// Add leading 0.
		ampm = 'AM',
		time;
			
	if (hh > 12) {
		h = hh - 12;
		ampm = 'PM';
	} else if (hh === 12) {
		h = 12;
		ampm = 'PM';
	} else if (hh == 0) {
		h = 12;
	}
	
	// ie: 2013-02-18, 8:35 AM	
	time = yyyy + '-' + mm + '-' + dd + ', ' + h + ':' + min + ':' + s + ' ' + ampm;
		
	return time;
}

// Prototypes to get the minimum and maximum members of arrays
Array.prototype.max = function() {
    return Math.max.apply(null, this);
}

Array.prototype.min = function() {
    return Math.min.apply(null, this);
}

// Prototypes to get the first and last members of selections
d3.selection.prototype.first = function() {
    return d3.select(this[0][0]);
}
d3.selection.prototype.last = function() {
    var last = this.size() - 1;
    return d3.select(this[0][last]);
}

/*
  rescale

  v: an array of numbers
  max: a number
  min: a number

  This function rescales the elements of the vector `v` so that
  they each lie between `min` and `max`.

  For example, rescale([1, 5, 6], 2, 3) === [2, 2.833, 3].
*/
function rescale(v, min, max) {
    var N = v.length;

    var vMin = v.min();
    var vMax = v.max();
    var vSpread = vMax - vMin;

    var spread = max - min;

    var scale = v;
    for (i = 0; i < N; i++) {
	scale[i] = ((v[i] - vMin) / vSpread) * spread + min;
    }
    return scale;
}

/*
  blinkFinalBars

  milliseconds: a number
  team1PrimaryColor: a color
  team2PrimaryColor: a color
  team1SecondaryColor: a color
  team1SecondaryColor: a color

  This function causes the final svg elements of the .barDown and
  .barUp classes to blink.

  The final element of the .barDown class will blink between
  `team1PrimaryColor` and `team1SecondaryColor`, completing half the
  period every `milliseconds` milliseconds.

  The final element of the .barUp class will blink similarly between
  the `team2PrimaryColor` and 'team2SecondaryColor.'

*/
function blinkFinalBars(
    milliseconds,
    team1PrimaryColor,
    team2PrimaryColor,
    team1SecondaryColor,
    team2SecondaryColor) {

    d3.selectAll(".barDown").last()
	.transition()
	.duration(milliseconds)
	.styleTween("fill", function() {
	    return d3.interpolate(
		team1PrimaryColor,
		team1SecondaryColor); })
	.transition()
	.duration(milliseconds)
	.styleTween("fill", function() {
	    return d3.interpolate(
		team1SecondaryColor,
		team1PrimaryColor); });

    d3.selectAll(".barUp").last()
	.transition()
	.duration(milliseconds)
	.styleTween("fill", function() {
	    return d3.interpolate(
		team2PrimaryColor,
		team2SecondaryColor); })
	.transition()
	.duration(milliseconds)
	.styleTween("fill", function() {
	    return d3.interpolate(
		team2SecondaryColor,
		team2PrimaryColor); });
}

/*
  makeDoubleBarGraph

  height: a number
  width: a number
  y1: a number
  y2: a number
  N: a number,  number of bars at end of game
  strokeWidth: a number
  team1PrimaryColor: a color
  team2PrimaryColor: a color
  team1SecondaryColor: a color
  team1SecondaryColor: a color
  backgroundColor: backgroundColor
  tick: a number
  xPadding: a number
  yPadding: a number

  This function draws the central graph of our site.
  A more formal description is forthcoming.
*/
function makeDoubleBarGraph(
    height,
    width,
    y1,
    y2,
    N,
    strokeWidth,
    team1PrimaryColor,
    team2PrimaryColor,
    team1SecondaryColor,
    team2SecondaryColor,
    backgroundColor,
    dottedLineColor,
    tick,
    xPadding,
    yPadding,
    xInnerPadding,
    yInnerPadding,
    yMidWidth,
    startTimeString,
    endTimeString,
    nTimeTickMarks,
    initializing) {

    assert(
	y1.length == y2.length,
	"Vectors must have same length.");
    M = y1.length;

    assert(
	M <= N,
	"Vectors must have length less than N.");


    var canvas = d3.select("#liveGraph")
	.selectAll("svg")
	.data([[height, width]])
	.enter()
	.append("svg")
	.attr("height", function(d) { return d[0]; })
	.attr("width", function(d) { return d[1]; })
	.style({ "background-color" : backgroundColor,
		 "margin" : "auto",
		 "display" : "block",
		 "width" : width,
		 "position" : "relative"});

    // First get the sides of the rectangle
    var xBegin = width * xPadding;
    var xEnd = width - xBegin;
    var xMid = (xEnd + xBegin) / 2;

    var xInnerBegin = xBegin + (width - 2 * xBegin) * xInnerPadding;
    var xInnerEnd = width - xInnerBegin;

    var yBegin = height * yPadding;
    var yEnd = height - yBegin;

    var yInnerBegin = yBegin + (width - 2 * yBegin) * yInnerPadding;
    var yInnerEnd = height - yInnerBegin;

    var yMid = (yBegin + yEnd) / 2;
    var yMidUp = yMid + yMidWidth;
    var yMidDown = yMid - yMidWidth;
    d3.select("#liveGraph")
	.select("svg")
	.selectAll("line")
	.remove()

    var lineList = d3.select("#liveGraph")
	.select("svg")
	.selectAll("line")

    lineList.data([
	[xBegin, yBegin, xBegin, yEnd],
	[xEnd, yBegin, xEnd, yEnd],
	[xBegin, yBegin, xEnd, yBegin],
	[xBegin, yEnd, xEnd, yEnd],
	[xBegin + 20, yMidUp, xEnd - 20, yMidUp],
	[xBegin + 20, yMidDown, xEnd - 20, yMidDown]])
	.enter()
	.append("line")
	.attr("x1", function(d) { return d[0]; })
	.attr("y1", function(d) { return d[1]; })
	.attr("x2", function(d) { return d[2]; })
	.attr("y2", function(d) { return d[3]; })
	.style({ "stroke" : "black", "stroke-width" : strokeWidth});

    var xTicks = [];
    for (i = 0; i <= N; i++) {
	xTicks.push([
	    (i / N) * (xInnerEnd - xInnerBegin) + xInnerBegin,
	    ((i + 1) / N) *
		(xInnerEnd - xInnerBegin) + xInnerBegin])
    }

    function addTicks(tickBottom, tickTop) {
	d3.select("#liveGraph")
	    .select("svg")
	    .selectAll("tick")
	    .remove()

	lineList = d3.select("#liveGraph")
	    .select("svg")
	    .selectAll("tick")
	    .data(xTicks)
	    .enter()
	    .append("line")
	    .attr("x1", function(d) { return d[0]; })
	    .attr("x2", function(d) { return d[0]; })
	    .attr("y1", tickBottom)
	    .attr("y2", tickTop)
	    .style({
		"stroke" : "black",
		"stroke-width" : 1})
	    .attr("class", "tick");
    }

    addTicks(yMidUp, yMidUp + tick);
    addTicks(yMidDown, yMidDown - tick);
    var y1Max = y1.max();
    var y2Max = y2.max();
    var originalYMax = y1Max > y2Max ? y1Max : y2Max;
    yMax = Math.max(Math.pow(10, Math.ceil(Math.log10(originalYMax + 1))), 100);

    var jump = yMax / 10;
    while (yMax - jump > originalYMax) { 
	yMax -= jump;
    } 

    var nowYMag = yMax;

    yMax = yMax * 1.25;

    var yMag = [];
    while (nowYMag > 1) {
	yMag.push(nowYMag);
	nowYMag -= jump;
    }

    var y1Scaled = [];
    var y2Scaled = [];
    for (i = 0; i < M; i++) {
	y1Scaled.push(
	    yMidDown - (yMidDown - yInnerBegin) *
		(y1[i] / yMax));
	y2Scaled.push(
	    yMidUp + (yInnerEnd - yMidUp) *
		(y2[i] / yMax));
    }

    var y1MagScaled = [];
    var y2MagScaled = [];
    for (i = 0; i < yMag.length; i++) {
	y1MagScaled.push(
	    [yMidDown - (yMidDown - yInnerBegin) *
	     (yMag[i] / yMax),
	     yMag[i]]);
	y2MagScaled.push(
	    [yMidUp + (yInnerEnd - yMidUp) *
	     (yMag[i] / yMax),
	     yMag[i]]);
    }

    function makeDottedLineList(y, dottedLineClass) {
	d3.select("#liveGraph")
	    .select("svg")
	    .selectAll("." + dottedLineClass)
	    .remove()

	d3.select("#liveGraph")
	    .select("svg")
	    .selectAll(dottedLineClass)
	    .data(y)
	    .enter()
	    .append("line")
	    .attr("x1", xBegin + 20)
	    .attr("x2", xEnd - 20)
	    .attr("y1", function(d) { return d[0]; })
	    .attr("y2", function(d) { return d[0]; })
	    .style({
		"stroke" : dottedLineColor,
		"stroke-width" : strokeWidth,
		"stroke-dasharray" : "5, 5" })
	    .attr("class", dottedLineClass);
    }

    function addYLabels(y, color, labelClass) {
	d3.select("#liveGraph")
	    .select("svg")
	    .selectAll(labelClass)
	    .remove()

	d3.select("#liveGraph")
	    .select("svg")
	    .selectAll("." + labelClass)
	    .data(y)
	    .enter()
	    .append("text")
	    .text(function(d) { return d[1]; })
	    .attr("x", xBegin + 1)
	    .attr("y", function(d) { return d[0]; })
	    .attr("font-family", "sans-serif")
	    .attr("font-size", "10px")
	    .attr("fill", color)
	    .attr("alignment-baseline", "central")
	    .attr("text-anchor", "left")
	    .attr("class", labelClass);
    }

    makeDottedLineList(y1MagScaled, "yAxisUp");
    makeDottedLineList(y2MagScaled, "yAxisDown");


    addYLabels(y1MagScaled, team1PrimaryColor, "yLabelUp");
    addYLabels(y2MagScaled, team2PrimaryColor, "yLabelDown");

    var y1Rects = [];
    var y2Rects = [];

    for (i = 0; i < M; i++) {
	y1Rects.push(
	    [xTicks[i][0] + strokeWidth / 2,
	     y1Scaled[i] - strokeWidth,
	     xTicks[i][1] - xTicks[i][0] - strokeWidth / 2,
	     yMidDown - y1Scaled[i],
	     y1[i]]);
	y2Rects.push(
	    [xTicks[i][0] + strokeWidth / 2,
	     yMidUp + strokeWidth,
	     xTicks[i][1] - xTicks[i][0] - strokeWidth / 2,
	     y2Scaled[i] - yMidUp,
	     y2[i]]);
    }

    function makeRectangleList(rectangles, barClass, color){
	d3.select("#liveGraph")
	    .select("svg")
	    .selectAll("." + barClass)
	    .remove()

	d3.select("#liveGraph")
	    .select("svg")
	    .selectAll("." + barClass)
	    .data(rectangles)
	    .enter()
	    .append("rect")
	    .attr("x", function(d) { return d[0]; })
	    .attr("y", function(d) { return d[1]; })
	    .attr("width", function(d) { return d[2]; })
	    .attr("height", function(d) { return d[3]; })
	    .attr("fill", color)
	    .attr("class", barClass)
	    .attr("title", function(d) { return d[4]; });
    }
    
    makeRectangleList(
	y1Rects,
	"barDown",
	team1PrimaryColor);
    makeRectangleList(
	y2Rects,
	"barUp",
	team2PrimaryColor);

    milliseconds = 1500;
    var callString = "blinkFinalBars(" +
	milliseconds + ", '" +
	team1PrimaryColor + "', '" +
	team2PrimaryColor + "', '" +
	team1SecondaryColor + "', '" +
	team2SecondaryColor + "');";

    var startTime = fromHMS(startTimeString);
    var endTime = fromHMS(endTimeString);
    var timeInterval = (endTime - startTime) / (nTimeTickMarks - 1);
    var tickInterval = (xInnerEnd - xInnerBegin) / (nTimeTickMarks - 1);
    var times = [];
    for (i = 0; i < nTimeTickMarks; i++) {
	times.push([
	    toHM(Math.floor(startTime + timeInterval * i)),
	    i * tickInterval + xInnerBegin]);
    }


    d3.select("#liveGraph")
	.select("svg")
	.selectAll(".time")
	.remove()

    var text = d3.select("#liveGraph")
	.select("svg")
	.selectAll(".times")
	.data(times)
	.enter()
	.append("text")
	.text(function (d) { return d[0]; })
	.attr("x", function(d) { return d[1]; })
	.attr("y", function(d) { return yMid; })
	.attr("font-family", "sans-serif")
	.attr("font-size", "10px")
	.attr("fill", "black")
	.attr("alignment-baseline", "central")
	.attr("text-anchor", "middle")
	.attr("class", "time");

    d3.select("#liveGraph")
	.select("svg")
	.selectAll(".axisLabel")
	.remove();

    var transformString = "rotate(270," + (xBegin - 20) + "," + yMid + ")";
    d3.select("#liveGraph")
	.select("svg")
	.selectAll(".axisLabel")
	.data(["number of tweets"])
	.enter()
	.append("text")
	.text(function(d) { return d; })
	.attr("x", xBegin - 20)
	.attr("y", yMid)
	.attr("transform", transformString)
	.attr("font-family", "sans-serif")
	.attr("font-size", "14px")
	.attr("fill", "black")
	.attr("alignment-baseline", "central")
	.attr("text-anchor", "middle")
	.attr("class", "axisLabel");

    d3.select("#liveGraph")
	.select("svg")
	.selectAll(".graphTitle")
	.remove();

    d3.select("#liveGraph")
	.select("svg")
	.selectAll(".graphTitle")
	.data(["Tweets By Team And Minute"])
	.enter()
	.append("text")
	.text(function(d) { return d; })
	.attr("x", xMid)
	.attr("y", yInnerBegin - 20)
	.attr("font-family", "sans-serif")
	.attr("font-size", "14px")
	.attr("fill", "black")
	.attr("alignment-baseline", "central")
	.attr("text-anchor", "middle")
	.attr("class", "graphTitle");


    if (initializing) { window.setInterval(callString, milliseconds * 2); }
}


/*
	drawHashtagChart
	hashtags: a list of top_hashtags objects returned from getArchive
	This function draws a horizontal bar chart of popular hashtags.
*/
function drawHashtagChart(hashtags){
	var hashtagsData = []
	for (var i = 0; i < hashtags.length; i++) {
		hashtagsData.push(hashtags[i].count);
	};

	var scaleHashtagData = d3.scale.linear()
							.domain([0, d3.max(hashtagsData)])
							.range([0, 420])

	d3.select("#topHashtagsChart")
		.selectAll("div")
			.data(hashtagsData)
		.enter().append("div")
			.style("width", function(d) { return scaleHashtagData(d) + "px"})
			.text(function(d) {return d; });	
}

function getCounts(url) {
    console.log(url);
    var jq = document.createElement('script');
    jq.src = "https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js";

	var result = $.ajax({
	url: url,
	type: 'GET',
	async: false});

	return result.responseJSON;
}

function getArchive(url) {
    console.log(url);
    
	var result = $.ajax({
	url: url,
	type: 'GET',
	async: false});

	return result.responseJSON;
}

function getPopularTweet(url, body) {
    $.ajax({
	type: "POST",
	url: url,
	data: JSON.stringify(body),
	success: function(data, status){
	    loadTweets(data.top_tweet, url, body);
	}
    });
}

/*
  loadTweets
  hidden: a string giving the id of a hidden div
  container: a string giving the id of a div for display
  file: a string giving the file to read data from
  counter: the number of lines that have been read from the file
  previously
  timeout: a number specifying the amount of time until the function
  should call itself recursively
  This function loads the file containing data for the central graph
  and then passes that data to makeDoubleBarGraph(...).
*/
function loadTweets(tweet_id, url, body) {
    if (tweet_id) {
	var divName = 'tweet' + String(tweet_id);
	var divString = '<div id="' + divName + '"></div>';
	var oldScrollTop = $('#tweets').scrollTop();
	$('#tweets').prepend(divString);
	twttr.widgets.createTweet(
	    tweet_id,
	    document.getElementById(divName),
	    {
		cards: 'hidden'
	    }).then(function(element) {
		if (oldScrollTop > 0) {
		    var adjustment = $("#" + divName)[0].getBoundingClientRect().height + 10;
		    $('#tweets').scrollTop(oldScrollTop + adjustment);
		}
	    });
	if(body.exclusions){
	    body.exclusions.push(tweet_id);
	} else {
	    body.exclusions = [tweet_id];
	}
	setTimeout(function() {
	    getPopularTweet(url, body);
	}, 30000);
    }
}

function loadArchivedTweets(tweet_ids) {
	for (var i = 0; i < tweet_ids.length; i++) {
		tweet_id = tweet_ids[i];
		var divName = 'tweet' + String(tweet_id);
		var divString = '<div id="' + divName + '"></div>';
		console.log(divString);
		var oldScrollTop = $('#tweets').scrollTop();
		$('#tweets').prepend(divString);
		twttr.widgets.createTweet(
			tweet_id,
			document.getElementById(divName),
			{
				cards: 'hidden'
		    }).then(function(element) {
				if (oldScrollTop > 0) {
					var adjustment = $("#" + divName)[0].getBoundingClientRect().height + 10;
					$('#tweets').scrollTop(oldScrollTop + adjustment);
				}
			});
	}
}



/*
  loadGraph

  countsData: the object returned by getCounts
  container: a string giving the id of a div for display
  barDuration: a number giving the number of seconds each bar
  in the graph should correspond to.
  timeout: a number specifying the amount of time until the function
  should call itself recursively

*/
function loadGraph(
    countsData,
    container,
    match_ts,
    liveTweetsUrl,
    barDuration,
    timeout,
    initializing) {
    
    var team1Arr = countsData ? countsData.home.counts : [];
    var team2Arr = countsData ? countsData.away.counts : [];

    startTimeString = convertTimestampToLocalTime(match_ts).slice(-11, -3);
    endTimeString = convertTimestampToLocalTime(match_ts + 2 * 60 * 60).slice(-11, -3);

    startTimeString = startTimeString[0] == "0" ? console.log(startTimeString.slice(1)) : startTimeString;
    endTimeString = endTimeString[0] == "0" ? endTimeString.slice(1) : endTimeString;

    makeDoubleBarGraph(
	500,
	600,
	team1Arr,
	team2Arr,
	120,
	1,
	"DarkBlue",
	"DarkRed",
	"Blue",
	"Red",
	"#F7F9FA",
	//"#E8EAEB",
	"#d9d9d9",
	3,
	0.10,
	0.10,
	0.05,
	0.00,
	10,
	startTimeString,
	endTimeString,
	9,
	initializing);

    function replaceUrlParam(url, paramName, paramValue) {
		var pattern = new RegExp('\\b('+paramName+'=).*?(&|$)')
		if(url.search(pattern)>=0){
		    return url.replace(pattern,'$1' + paramValue + '$2');
		}
		return url + (url.indexOf('?')>0 ? '&' : '?') + paramName + '=' + paramValue 
	    }

    function addIncrementalCountData(oldCountsData, newCountsData){
		if(oldCountsData){
		    for (var i = 0; i < newCountsData.home.counts.length; i++) {
			oldCountsData.home.counts.push(newCountsData.home.counts[i]);
		    };
		    for (var i = 0; i < newCountsData.away.counts.length; i++) {
			oldCountsData.away.counts.push(newCountsData.away.counts[i]);
		    };
		    return oldCountsData;
		}
		return newCountsData;
	}

	if (timeout) {
		setTimeout(function() {
			var now = Math.floor(new Date().getTime() / 1000);
			//get data from last minute
			start = now - 59;
			liveTweetsUrl = replaceUrlParam(liveTweetsUrl, 'start', Math.floor(start).toString())
			newCountsData = getCounts(liveTweetsUrl);
			countsData = addIncrementalCountData(countsData, newCountsData);
			loadGraph(
			    countsData,
			    container,
			    liveTweetsUrl,
			    barDuration,
			    timeout,
			    initializing);
		    }, timeout * 1000);
	}
}
