function initialize() {
    window.map = new google.maps.Map(document.getElementById("map_canvas"), {zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});
    //google.maps.event.addListener(map,'bounds_changed',getClusters);
    window.points = new Array();
    //window.bboxes = new Object();
    window.conn = null;
    //window.updating = false;
    //window.concurent = false;

    // Try W3C Geolocation (Preferred)
    if(navigator.geolocation) {
	browserSupportFlag = true;
	navigator.geolocation.getCurrentPosition(function(position) {
	    initialLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
	    map.setCenter(initialLocation);
	}, function() {
	    handleNoGeolocation(browserSupportFlag);
	});
	// Try Google Gears Geolocation
    } else if (google.gears) {
	browserSupportFlag = true;
	var geo = google.gears.factory.create('beta.geolocation');
	geo.getCurrentPosition(function(position) {
	    initialLocation = new google.maps.LatLng(position.latitude,position.longitude);
	    map.setCenter(initialLocation);
	}, function() {
	    handleNoGeoLocation(browserSupportFlag);
	});
	// Browser doesn't support Geolocation
    } else {
	browserSupportFlag = false;
	handleNoGeolocation(browserSupportFlag);
    }
    
    function handleNoGeolocation(errorFlag) {
	if (errorFlag == true) {
	    alert("Geolocation service failed.");
	    initialLocation = newyork;
	} else {
	    alert("Your browser doesn't support geolocation. We've placed you in Siberia.");
	    initialLocation = siberia;
	}
	map.setCenter(initialLocation);
    }

    // load a tile to test stuff out
    loadTile(0,0,0);
}

function loadTile(zoom,x,y) {
    conn = new XMLHttpRequest();
    conn.open("GET", "/static/tiles/"+zoom+"/"+x+"/"+y+".json", true);
    conn.onreadystatechange = processTile;
    conn.send(null);
}

function clearPoints() {
    for (x=0;x<points.length;x++) {
	points[x].setVisible(false);
    }
}

function processTile() {
    if (conn.responseText.length <= 0) {return;}
    if (conn.readyState == 4) {
	if (conn.status == 200) {
	    console.log("points recieved");
	} else {
	    console.log("Error: "+conn.statusText);
	    return;
	}
    } else {
	return;
    }
    parsed = JSON.parse(conn.responseText);
    clearPoints();
    console.log(parsed);
    for (xcell in parsed) {
	for (ycell in parsed[xcell]) {
	    for (point in parsed[xcell][ycell]) {
		pos = point['coordinates'];
		console.log(parsed[xcell][ycell][point]);
		marker = new google.maps.Market({position:new google.maps.LatLng(pos)});
		points[points.length] = marker;
	    }
	}
    }
}