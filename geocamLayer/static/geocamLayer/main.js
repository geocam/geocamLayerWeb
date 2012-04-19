function initialize() {
    window.map = new google.maps.Map(document.getElementById("map_canvas"), {zoom: 6, mapTypeId: google.maps.MapTypeId.ROADMAP});
    google.maps.event.addListener(map,'bounds_changed',getClusters);
    window.clusters = new Array();
    window.bboxes = new Object();
    window.conn = null;
    window.updating = false;
    window.concurent = false;

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
}

function getClusters() {
    if (typeof(map.getBounds()) == 'undefined') {return;}
    else if (updating) {concurent = true; return;}
    else {
	clearClusters();
	updating = true;
	bounds = map.getBounds()
	lat = map.getCenter().lat()
	    lng = map.getCenter().lng()
	    zoom_x = 360/(bounds.getNorthEast().lng()-bounds.getSouthWest().lng())
	    zoom_y = 180/(bounds.getNorthEast().lat()-bounds.getSouthWest().lat())
	    zoom_p = (zoom_x > zoom_y)?zoom_y:zoom_x;
	zoom_n = (zoom_x > zoom_y)?zoom_x:zoom_y;
	zoom   = (zoom_x < 0 || zoom_y < 0)?zoom_n:zoom_p;
	conn = new XMLHttpRequest();
	conn.open("GET","/points/"+zoom+"/"+lng+"/"+lat+"?cluster=1",true);
	conn.send();
	conn.onreadystatechange = setClusters;
	//Clusters();
    }
}

function clearClusters() {
    for (x=0; x<clusters.length; x++) {
	clusters[x].setVisible(false);
    }
}

function setClusters() {
    if (conn.responseText.length <= 0) {updating = false; concurent = false; return;}
    resp_clusters = JSON.parse(conn.responseText);
    updating = false; clearClusters();
    clusters = new Array(); bboxes = new Array();
    for (x=0; x<resp_clusters['features'].length; x++) {
	cluster = resp_clusters['features'][x];
	pos = cluster['geometry']['coordinates'].toString().split(',');
	if (cluster['properties']['subtype'] == 'point') {
	    marker = new google.maps.Marker({position:new google.maps.LatLng(pos[0], pos[1]), map:map});
	    clusters[clusters.length] = marker;
	}
	else {
	    marker = new google.maps.Marker({position:new google.maps.LatLng(pos[0], pos[1]), map:map, clickable:true, icon:new google.maps.MarkerImage(url='/static/arrow.png')});
	    bboxes[new google.maps.LatLng(pos[0], pos[1])] = cluster['properties']['bbox'];
	    google.maps.event.addListener(marker,"click",function(event){clearClusters();bbox=bboxes[event.latLng];bounds = new google.maps.LatLngBounds(new google.maps.LatLng(bbox[0],bbox[1]),new google.maps.LatLng(bbox[2],bbox[3]));console.log(bbox);console.log(bounds);map.fitBounds(bounds);});
	    clusters[clusters.length] = marker;
	}
    }
    if (concurent && !updating) {getClusters(); concurent = false;}
}

/*
function foo () {
    south = blah
    north = blah
    east = blah
    west = blah

    size = max(south-north, east-west)
    zoom = ceiling(log2(360/size))

    tile_size = 360/2**zoom
    west_x = floor((west-(-180))/tile_size)
    south_y = floor((south-(-90))/tile_size)
    east_x = ceiling((east-(-180))/tile_size)
    north_y = ceiling((north-(-90))/tile_size)
    
    for x in range(west_x, east_x):
        for y in range(south_y, north_y):
	    fetch(zoom, x, y)
*/