/*
	Used to assert conditinos.
	Probably there is a more canonical way to do this.
*/
function assert(condition, message) {
	if (!condition) {
		alert(message);
		throw new Error(message);
	}
}

function toHMS(time) {
	function fix(x) {
		if (x < 10) { return "0" + x.toString(); }
		else { return x.toString(); }
	}
	var S = fix(time % 60);
	time = Math.floor(time / 60);
	var M = fix(time % 60);
	time = Math.floor(time / 60);
	var H = fix(time % 24);
	return (H + ":" + M + ":" + S);
}

function fromHMS(timeString) {
	var split = timeString.split(":");
	return (
		parseInt(split[0]) * 3600 +
			parseInt(split[1]) * 60 +
			parseInt(split[2]));
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

	The final element of the .barUp class will blink similary between
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
	N: a number
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

	console.log("makeDoubleBarGraph(...)");
	assert(
		y1.length == y2.length,
		"Vectors must have same length.");
	M = y1.length;

	assert(
		M <= N,
		"Vectors must have length less than N.");


	d3.select("#graph")
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

	var xInnerBegin = xBegin + (width - 2 * xBegin) * xInnerPadding;
	var xInnerEnd = width - xInnerBegin;

	var yBegin = height * yPadding;
	var yEnd = height - yBegin;

	var yInnerBegin = yBegin + (width - 2 * yBegin) * yInnerPadding;
	var yInnerEnd = height - yInnerBegin;

	var yMid = (yBegin + yEnd) / 2;
	var yMidUp = yMid + yMidWidth;
	var yMidDown = yMid - yMidWidth;

	var lineList = d3.select("#graph")
		.select("svg")
		.selectAll("line")

	lineList.data([
		[xBegin, yBegin, xBegin, yEnd],
		[xEnd, yBegin, xEnd, yEnd],
		[xBegin, yBegin, xEnd, yBegin],
		[xBegin, yEnd, xEnd, yEnd],
		[xBegin, yMidUp, xEnd, yMidUp],
		[xBegin, yMidDown, xEnd, yMidDown]])
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
		lineList = d3.select("#graph")
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
	var yMax = y1Max > y2Max ? y1Max : y2Max;
	yMax = Math.max(Math.pow(2, Math.ceil(Math.log2(yMax + 1))), 128);

	var jump = Math.pow(2, Math.floor(Math.log2(yMax) / 4));
	var nowYMag = yMax;

	yMax = yMax * 1.25;

	var yMag = [];
	while (nowYMag > 1) {
		yMag.push(nowYMag);
		nowYMag /= jump;
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

	function makeDottedLineList(y) {
		d3.select("#graph")
			.select("svg")
			.selectAll(".dottedLine")
			.data(y)
			.enter()
			.append("line")
			.attr("x1", xBegin + 1)
			.attr("x2", xEnd - 1)
			.attr("y1", function(d) { return d[0]; })
			.attr("y2", function(d) { return d[0]; })
			.style({
				"stroke" : dottedLineColor,
				"stroke-width" : strokeWidth,
				"stroke-dasharray" : "5, 5" })
			.attr("class", "tick");
	}

	makeDottedLineList(y1MagScaled);
	makeDottedLineList(y2MagScaled);

	var y1Rects = [];
	var y2Rects = [];
	for (i = 0; i < M; i++) {
		y1Rects.push(
			[xTicks[i][0] + strokeWidth / 2,
			 y1Scaled[i] + strokeWidth / 2,
			 xTicks[i][1] - xTicks[i][0] - strokeWidth / 2,
			 yMidDown - y1Scaled[i] - strokeWidth / 2,
			 y1[i]]);
		y2Rects.push(
			[xTicks[i][0] + strokeWidth / 2,
			 yMidUp - strokeWidth / 2,
			 xTicks[i][1] - xTicks[i][0] - strokeWidth / 2,
			 y2Scaled[i] - yMidUp - strokeWidth / 2,
			 y2[i]]);
	}

	function makeRectangleList(rectangles, barClass, color){
		d3.select("#graph")
			.select("svg")
			.selectAll("." + barClass)
			.remove()

		d3.select("#graph")
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
			toHMS(Math.floor(startTime + timeInterval * i)),
			i * tickInterval + xInnerBegin]);
	}

	var text = d3.select("#graph")
		.select("svg")
		.selectAll("text")
		.data(times)
		.enter()
		.append("text")
		.text(function (d) { return d[0]; })
		.attr("x", function(d) { return d[1]; })
		.attr("y", function(d) { return yMid; })
		.attr("font-family", "sans-serif")
		.attr("font-size", "10px")
		.attr("fill", "red")
		.attr("alignment-baseline", "central")
		.attr("text-anchor", "middle");

	if (initializing) { window.setInterval(callString, milliseconds * 2); }
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
function loadTweets(hidden, container, file, counter) {
	var tweets = $('#' + hidden).text().split('\n');
	for (i = counter; i < tweets.length; i++) {
		twttr.widgets.createTweet(
			tweets[i],
			document.getElementById(container),
			{
				cards: 'hidden',
				width: 350
			});
	}
	var counter = tweets.length - 1;

	setTimeout(function() {
		$('#' + hidden).load(file, function() {
			loadTweets(hidden, container, file, counter);
		});
	}, 3000);
}


/*
	loadGraph

	hidden: a string giving the id of a hidden div
	container: a string giving the id of a div for display
	file: a string giving the file to read data from
	barDuration: a number giving the number of seconds each bar
		in the graph should correspond to.
	timeout: a number specifying the amount of time until the function
		should call itself recursively

*/
function loadGraph(
	hidden,
	container,
	file,
	barDuration,
	timeout,
	initializing) {
	var lines = $('#' + hidden).text().split('\n');
	var n = lines.length;
	var now = 0;
	var team1Total = 0;
	var team2Total = 0;
	var team1Arr = [];
	var team2Arr = [];
	for (i = 0; i < n - 1; i++) {
		var line = lines[i];
		var split = line.split(',');
		var time = split[0];
		var team1 = parseInt(split[1]);
		var team2 = parseInt(split[2]);
		if (time < barDuration + now) {
			team1Total += team1;
			team2Total += team2;
		} else {
			team1Arr.push(team1Total);
			team2Arr.push(team2Total);
			team1Total = 0;
			team2Total = 0;
			now = now + barDuration;
			i--;
		}
	}
	team1Arr.push(team1Total);
	team2Arr.push(team2Total);

	makeDoubleBarGraph(
		400,
		600,
		team1Arr,
		team2Arr,
		30,
		1,
		"DarkBlue",
		"DarkRed",
		"Blue",
		"Red",
		"#F7F9FA",
		"#E8EAEB",
		3,
		0.05,
		0.05,
		0.05,
		0.00,
		10,
		"11:00:00",
		"13:00:00",
		9,
		initializing);

	setTimeout(function() {
		$('#' + hidden).load(file, function() {
			loadGraph(
				hidden,
				container,
				file,
				barDuration,
				timeout,
				false);
		});
	}, timeout * 1000);
}
