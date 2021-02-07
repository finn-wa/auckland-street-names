function initMap() {
  const map = L.map('map', {
    center: { lat: -36.85, lon: 174.76 },
    zoom: 12,
  });

  L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  const markers = L.markerClusterGroup({
    chunkedLoading: true,
    disableClusteringAtZoom: 17,
    spiderfyOnMaxZoom: false,
  });

  markers.addLayers(streetData.map((s) => streetToMarker(s)));
  map.addLayer(markers);
}

function streetToMarker(street) {
  const marker = L.marker(L.latLng(street[0], street[1]));
  marker.bindTooltip(`<div class="tooltip info"><strong>${street[2]}</strong><br>${street[3]}</div>`);
  return marker;
}

initMap();
