let map;
let markers = [];
let infoWindow;

function initMap() {
    const dublin = { lat: 53.349805, lng: -6.26031 };
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: dublin,
        mapId: 'YOUR_MAP_ID', // Optional: Use for personalized styles
    });

    infoWindow = new google.maps.InfoWindow();
    fetchStations();
}

async function fetchStations() {
    try {
        const response = await fetch('/api/stations');
        const stations = await response.json();

        // Clear existing markers
        markers.forEach(m => m.setMap(null));
        markers = [];

        stations.forEach(station => {
            const marker = new google.maps.Marker({
                position: { lat: station.position_lat, lng: station.position_lng },
                map: map,
                title: station.name,
                icon: getMarkerIcon(station.available_bikes)
            });

            marker.addListener("click", () => {
                showStationDetails(station);
            });

            markers.push(marker);
        });
    } catch (error) {
        console.error("Error fetching stations:", error);
    }
}

function getMarkerIcon(bikes) {
    let color = 'red';
    if (bikes > 10) color = 'green';
    else if (bikes > 0) color = 'orange';

    return {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: color,
        fillOpacity: 0.8,
        scale: 8,
        strokeColor: 'white',
        strokeWeight: 2
    };
}

async function showStationDetails(station) {
    document.querySelector('#details-panel h2').innerText = station.name;
    document.querySelector('#details-panel p').innerText = `Address: ${station.address}\nBikes: ${station.available_bikes} / ${station.bike_stands}`;

    // Fetch historical data for chart
    try {
        const response = await fetch(`/api/stations/${station.number}`);
        const history = await response.json();
        updateChart(history);
    } catch (e) {
        console.error("Error fetching history:", e);
    }
}

function updateChart(history) {
    const ctx = document.getElementById('predictionChart').getContext('2d');

    if (window.predictionChart && typeof window.predictionChart.destroy === 'function') {
        window.predictionChart.destroy();
    }

    const labels = history.map(h => new Date(h.last_update).toLocaleTimeString()).reverse();
    const data = history.map(h => h.available_bikes).reverse();

    window.predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Available Bikes',
                data: data,
                borderColor: '#007bff',
                tension: 0.1
            }]
        }
    });
}
