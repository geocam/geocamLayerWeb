function initialize() {
    window.map = new google.maps.Map(document.getElementById("map_canvas"), {zoom:6, mapTypeId:google.maps.MapTypeId.ROADMAP});
    google.maps.event.addListener(map,'bounds_changed',boundsChanged);
    window.points = new Array();
    window.bboxes = new Object();
    window.currentZoom = null;
    window.currentX = new Array();
    window.currentY = new Array();

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

    // load initial data set
    clearPoints();
    boundsChanged();
}

function clearPoints() {
    console.log("clearing points");
    for (p=0;p<points.length;p++)
	points[p].setVisible(false);
    points = new Array();
    bboxes = new Object();
    currentX = new Array();
    currentY = new Array();
}

function boundsChanged() {
    console.log("bounds changed");
    if (typeof(map.getBounds()) == 'undefined') return;
    bounds = map.getBounds();
    south = bounds.getSouthWest().lat();
    west = bounds.getSouthWest().lng();
    north = bounds.getNorthEast().lat();
    east = bounds.getNorthEast().lng();
    size = Math.max(south-north, east-west);

    zoom = Math.ceil(Math.log(360/size)/Math.log(2));
    if (isNaN(zoom)) zoom = 0;
    zoom -= 1;
    if (zoom < 0) zoom = 1;
    if (zoom > 9) zoom = 9;
    tile_size = 360/Math.pow(2,zoom);

    center = map.getCenter();
    x = Math.floor((center.lng()-(-180))/(tile_size/2));
    y = Math.floor((center.lat()-(-90))/(tile_size/2));

    document.title = "Static Tile HTML Test - Current Tile: "+zoom+"/"+x+"/"+y;
    console.log("Current Tile: "+zoom+"/"+x+"/"+y);

    if (currentZoom != zoom ||
	currentX.indexOf(x) == -1 ||
	currentY.indexOf(y) == -1
	) {
	loadTile(zoom,x,y);
	currentX[currentX.length] = x;
	currentY[currentY.length] = y;
    }
}

function loadTile(zoom,x,y) {
    console.log("sending request");
    $.get("/quad/"+zoom+"/"+x+"/"+y, gotData);
}

function gotData(data) {
    console.log("got response");
}