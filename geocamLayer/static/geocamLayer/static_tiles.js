function initialize() {
    window.map = new google.maps.Map(document.getElementById("map_canvas"), {zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});
    google.maps.event.addListener(map,'bounds_changed',boundsChanged);
    //google.maps.event.addListener(map,'bounds_changed',clearPoints);
    window.points = new Array();
    window.bboxes = new Object();
    window.conn = null;
    window.currentZoom = null;
    window.currentX = new Array();
    window.currentY = new Array();
    window.updating = false;
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

    boundsChanged();

    // load a tile to test stuff out
    //loadTile(0,0,0);
    //loadTile(0,0,1);

    //loadTile(0,1,0);
    //loadTile(0,1,1);
    //clearPoints();
}

function boundsChanged(start) {
    if (typeof(map.getBounds()) == 'undefined') {return;}
    bounds = map.getBounds();
    south = bounds.getSouthWest().lat();
    west = bounds.getSouthWest().lng();
    north = bounds.getNorthEast().lat();
    east = bounds.getNorthEast().lng();
    size = Math.max(south-north, east-west);

    zoom = Math.ceil(Math.log(360/size)/Math.log(2));
    if (isNaN(zoom)) zoom = 0;
    zoom -= 1;
    if (zoom < 0) zoom = 1
    if (zoom > 9) zoom = 9;
    tile_size = 360/Math.pow(2,zoom);

    center = map.getCenter();
    x = Math.floor((center.lng()-(-180))/(tile_size/2));
    y = Math.floor((center.lat()-(-90))/(tile_size/2));

    document.title="Static Tile HTML Test - Current Tile: "+zoom+"/"+x+"/"+y
    console.log("Current Tile: "+zoom+"/"+x+"/"+y);

    if (currentZoom != zoom) {
	clearPoints();
	currentZoom = zoom;
    }

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
    conn = new XMLHttpRequest();
    console.log("getting /static/tiles/"+zoom+"/"+x+"/"+y+".json", true);
    conn.open("GET", "/static/tiles/"+zoom+"/"+x+"/"+y+".json", true);
    conn.onreadystatechange = processTile;
    conn.send(null);
}

function clearPoints() {
    console.log("clearing points");
    for (p=0;p<points.length;p++) {
	points[p].setVisible(false);
    }
    points = new Array();
    bboxes = new Object();
    currentX = new Array();
    currentY = new Array();
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
    for (x in parsed['features']) {
	cluster = parsed['features'][x];
	pos = cluster['geometry']['coordinates'].toString().split(',');
	if (cluster['properties']['subtype'] == 'point') {
	    marker = new google.maps.Marker({position:new google.maps.LatLng(pos[1], pos[0]), map:map});
	    points[points.length] = marker;
	} else {
	    marker = new google.maps.Marker({position:new google.maps.LatLng(pos[1], pos[0]), map:map, clickable:true, icon:new google.maps.MarkerImage(url='/static/arrow.png')});
	    bboxes[new google.maps.LatLng(pos[1], pos[0])] = cluster['properties']['bbox'];
	    google.maps.event.addListener(marker,"click",function(event){
		bbox = bboxes[event.latLng];
		console.log(bbox);
		bounds = new google.maps.LatLngBounds(new google.maps.LatLng(bbox[0],bbox[1]),
						      new google.maps.LatLng(bbox[2],bbox[3]));
		console.log(bounds);
		map.fitBounds(bounds);
		}
		);
	    points[points.length] = marker;
	}
    }
}