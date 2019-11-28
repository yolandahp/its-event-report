var map;
var service;
var prevInfoWindow = false;

var table;

function initMap() {
    var directionsService = new google.maps.DirectionsService;

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 18,
        center: {lat: -7.282681, lng: 112.794811}
    });

    table = $('#rekap').DataTable({
        "scrollX": true
    });

    rekapData = table.rows().data();

    for(var i = 0; i < rekapData.length; i++) {
        route = [];
        route["tweet"] = rekapData[i][2];
        route["place"] = rekapData[i][4];
        route["address"] = rekapData[i][5];
        route["latitude"] = parseFloat(rekapData[i][6]);
        route["longitude"] = parseFloat(rekapData[i][7]);

        displayOnePosition(route);
    }    
}

function displayOnePosition(route){
    route.tweet = route.tweet.replace(/(\r\n|\n|\r)/gm,"<br>");
    var contentString = '<div id="content">'+
                            '<div id="siteNotice">'+
                            '</div>'+
                            '<div class="firstHeading">' + 
                                '<h5>'+ route.place +'</h5>'+
                                '<p><b>'+ route.address + '</b></p>' +
                            '</div>' + 
                            '<div id="bodyContent">'+
                                '<p>' + route.tweet + '</p>'+
                            '</div>'+
                        '</div>';

    var infoWindowMarker = new google.maps.InfoWindow({
        content: contentString
    });

    var infoMarker = new google.maps.Marker({
        position: {lat: route.latitude, lng: route.longitude},
        map: map,
        title: route.place
    });

    infoMarker.addListener('click', function() {
        if(prevInfoWindow) {
            prevInfoWindow.close();
        }
    
        prevInfoWindow = infoWindowMarker;

        infoWindowMarker.open(map, infoMarker);
        infoWindowMarker.setZIndex(1000);
    });

    var infoWindow = new google.maps.InfoWindow();
    infoWindow.setContent(route.tweet);
    infoWindow.setPosition({lat: route.latitude, lng: route.longitude});
    infoWindow.open(map, infoMarker);
}
