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
    last = this.size() - 1;
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
    N = v.length;

    vMin = v.min();
    vMax = v.max();
    vSpread = vMax - vMin;
    
    spread = max - min;

    scale = v;
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
    tick,
    xPadding,
    yPadding) {

    if (typeof(xPadding) === 'undefined') {
	xPadding = .05;
    }
    if (typeof(yPadding) === 'undefined') {
	yPadding = .05;
    }

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

    // First get the sides of the rectangle that we will actually draw
    xBegin = width * xPadding;
    xEnd = width - xBegin;

    yBegin = height * yPadding;
    yEnd = height - yBegin;

    yMid = (yBegin + yEnd) / 2;

    lineList = d3.select("#graph")
	.select("svg")
	.selectAll("line")

    lineList.data([
	[xBegin, yBegin, xBegin, yEnd],
	[xEnd, yBegin, xEnd, yEnd],
	[xBegin, yBegin, xEnd, yBegin],
	[xBegin, yEnd, xEnd, yEnd],
	[xBegin, yMid, xEnd, yMid]])
	.enter()
	.append("line")
	.attr("x1", function(d) { return d[0]; })
	.attr("y1", function(d) { return d[1]; })
	.attr("x2", function(d) { return d[2]; })
	.attr("y2", function(d) { return d[3]; })
	.style({ "stroke" : "black", "stroke-width" : strokeWidth});
    
    xTicks = [];
    for (i = 0; i < N; i++) {
	xTicks.push([
	    (i / N) * (xEnd - xBegin) + xBegin,
	    ((i + 1) / N) * (xEnd - xBegin) + xBegin])
    }
    
    yTickUp = yMid + tick;
    yTickDown = yMid - tick;

    lineList = d3.select("#graph")
	.select("svg")
	.selectAll(".tick")

    lineList.data(xTicks)
	.enter()
	.append("line")
	.attr("x1", function(d) { return d[0]; })
	.attr("x2", function(d) { return d[0]; })
	.attr("y1", yTickUp)
	.attr("y2", yTickDown)
	.style({ "stroke" : "cblack", "stroke-width" : strokeWidth})
	.attr("class", "tick");

    y1Max = y1.max();
    y2Max = y2.max();
    yMax = y1Max > y2Max ? y1Max : y2Max;

    y1Scaled = [];
    y2Scaled = [];
    for (i = 0; i < M; i++) {
	y1Scaled.push(yMid - (yMid - yBegin) * (y1[i] / yMax));
	y2Scaled.push(yMid + (yEnd - yMid) * (y2[i] / yMax));
    }

    y1Rects = [];
    y2Rects = [];

    for (i = 0; i < M; i++) {
	y1Rects.push(
	    [xTicks[i][0] + strokeWidth / 2,
	     y1Scaled[i] + strokeWidth / 2,
	     xTicks[i][1] - xTicks[i][0] - strokeWidth / 2,
	     yMid - y1Scaled[i] - strokeWidth / 2]);
	y2Rects.push(
	    [xTicks[i][0] + strokeWidth / 2,
	     yMid - strokeWidth / 2,
	     xTicks[i][1] - xTicks[i][0] - strokeWidth / 2,
	     y2Scaled[i] - yMid - strokeWidth / 2]);
    }

    rectangleList = d3.select("#graph")
    	.select("svg")
    	.selectAll(".barDown")
    	.data(y1Rects)
	.enter()
    	.append("rect")
    	.attr("x", function(d) { return d[0]; })
    	.attr("y", function(d) { return d[1]; })
    	.attr("width", function(d) { return d[2]; })
    	.attr("height", function(d) { return d[3]; })
	.attr("fill", team1PrimaryColor)
	.attr("class", "barDown")

    rectangleList = d3.select("#graph")
    	.select("svg")
    	.selectAll(".barUp")
    	.data(y2Rects)
	.enter()
    	.append("rect")
    	.attr("x", function(d) { return d[0]; })
    	.attr("y", function(d) { return d[1]; })
    	.attr("width", function(d) { return d[2]; })
    	.attr("height", function(d) { return d[3]; })
	.attr("fill", team2PrimaryColor)
	.attr("class", "barUp")

    milliseconds = 750;
    callString = "blinkFinalBars(" +
	milliseconds + ", '" +
	team1PrimaryColor + "', '" +
	team2PrimaryColor + "', '" +
	team1SecondaryColor + "', '" +
	team2SecondaryColor + "');"

    window.setInterval(callString, milliseconds * 2);
}

function loadTweets(hidden, container, file, counter) {
    tweets = $(hidden).text().split(',\n');
    for (i = counter; i < tweets.length; i++) {
	twttr.widgets.createTweet(
	    tweets[i],
	    document.getElementById(container),
	    {
		cards: 'hidden',
		width: 350
	    });
    }
    counter = tweets.length - 1;

    setTimeout(function() {
	$(hidden).load(file, function() {
	    loadTweets(hidden, container, file, counter);
	});
    }, 3000);
}

function loadGraph(hidden, container, file, chunk, timeout) {
    lines = $(hidden).text().split(',\n');
    n = lines.length;
    now = 0;
    team1Total = 0;
    team2Total = 0;
    team1Arr = [];
    team2Arr = [];
    for (i = 0; i < n - 1; i++) {
	line = lines[i];
	split = line.split(',');
	time = split[0];
	team1 = parseInt(split[1]);
	team2 = parseInt(split[2]);

	if (time < chunk + now) {
	    team1Total += team1;
	    team2Total += team2;
	} else {
	    team1Arr.push(team1Total);
	    team2Arr.push(team2Total);
	    team1Total = 0;
	    team2Total = 0;
	    now = now + chunk;
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
	90,
	1,
	"DarkBlue",
	"DarkRed",
	"Blue",
	"Red",
	"White",
	0,
	0.05,
	0.05);

    setTimeout(function() {
	$(hidden).load(file, function() {
	    loadGraph(hidden, container, file, chunk, timeout);
	});
    }, timeout * 1000);
}
