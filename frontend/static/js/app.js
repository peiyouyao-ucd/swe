/* ==========================================
   GLOBAL VARIABLES
   ========================================== */
let map;
let markers = [];
let predictionChart;
let currentMode = 'bikes'; 
let selectedStationNumber = null;
let allStationsData = [];
let currentHighlightedMarker = null;
let currentForecastData = [];
let directionsService = null;
let routeRenderers = [];
let routeCustomMarkers = [];


/* ==========================================
   1. MAP INITIALIZATION
   ========================================== */
function initMap() {
    const mapElement = document.getElementById("map");
    if (!mapElement) return;

    const dublin = { lat: 53.349805, lng: -6.26031 };
    
    map = new google.maps.Map(mapElement, {
        zoom: 13,
        center: dublin,
        mapId: 'DEMO_MAP_ID',
        disableDefaultUI: false,
    });

    fetchStations();
    fetchWeather();
    initAutocomplete();
}

/* ==========================================
   ROUTE PLANNER: AUTOCOMPLETE LOGIC
   ========================================== */
function initAutocomplete() {
    const originInput = document.getElementById('route-origin');
    const destInput = document.getElementById('route-destination');

    if (!originInput || !destInput) return;

    // 💡 Pro Tip: Restrict search results to Ireland ('ie')
    // This prevents users from accidentally selecting "Trinity College" in the USA
    const options = {
        componentRestrictions: { country: "ie" }, 
        fields: ["geometry", "name", "formatted_address"], 
    };

    // Attach Autocomplete to the input fields
    const originAutocomplete = new google.maps.places.Autocomplete(originInput, options);
    const destAutocomplete = new google.maps.places.Autocomplete(destInput, options);

    // Bias the search results towards the current map viewport
    if (map) {
        originAutocomplete.bindTo('bounds', map);
        destAutocomplete.bindTo('bounds', map);
    }
}

/* ==========================================
   2.TABS & HASH JUMPING LOGIC (Unified)
   ========================================== */

/**
 * Handles tab switching for any page with tabs (like How-to).
 */
function switchTab(event, contentId) {
    // 1. Find all tab pages and items in the current container
    const pages = document.querySelectorAll('.how-to-page');
    const tabs = document.querySelectorAll('.tab-item');

    // 2. Clear active classes
    pages.forEach(p => p.classList.remove('active'));
    tabs.forEach(t => t.classList.remove('active'));

    // 3. Activate the target page and the clicked tab
    const targetPage = document.getElementById(contentId);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
}

/**
 * Handles deep-linking when a user arrives with a #hash in the URL.
 */
function handleHashJump() {
    const hash = window.location.hash.substring(1);
    if (!hash) return;

    // Give the page a tiny moment to render before jumping
    setTimeout(() => {
        const targetPage = document.getElementById(hash);
        const targetTab = document.querySelector(`.tab-item[onclick*="${hash}"]`);

        if (targetPage && targetTab) {
            // Re-use our switchTab logic to update UI
            const pages = document.querySelectorAll('.how-to-page');
            const tabs = document.querySelectorAll('.tab-item');
            
            pages.forEach(p => p.classList.remove('active'));
            tabs.forEach(t => t.classList.remove('active'));

            targetPage.classList.add('active');
            targetTab.classList.add('active');

            // Smoothly scroll to the content
            targetPage.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 300);
}

// Ensure these run when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initPasswordToggle(); // Keep your existing password logic
    handleHashJump();     // Enable deep linking
});

/* ==========================================
   3. CYCLING FORECAST (WEATHER API)
   ========================================== */
async function fetchWeather() {
    const tempDisplay = document.getElementById('display-temp');
    if (!tempDisplay) return;

    try {
        const response = await fetch('/api/weather');
        const data = await response.json();
        if (data.error) return;


        tempDisplay.innerText = `${Math.round(data.temp)}°C`;
        document.getElementById('temp-min').innerText = Math.round(data.temp_min);
        document.getElementById('temp-max').innerText = Math.round(data.temp_max);
        document.getElementById('feels-like').innerText = `Feels like ${Math.round(data.feels_like)}°C`;
        document.getElementById('weather-condition').innerText = data.weather_description;
        document.getElementById('wind-val').innerText = `${data.wind_speed} km/h`;
        document.getElementById('hum-val').innerText = `${data.humidity}%`;
        document.getElementById('vis-val').innerText = `${(data.visibility / 1000).toFixed(0)} km`;
        document.getElementById('precip-val').innerText = `${data.precipitation || 0} mm`;

    
        const score = calculateCyclingScore(data);
        updateScoreUI(score);

       
        updateKeyFactors(data);
        updateWeatherTheme(data.weather_id, data.weather_main);

    } catch (error) {
        console.error("Weather fetch failed:", error);
    }
}


function updateScoreUI(score) {
    const scoreFill = document.getElementById('score-fill');
    const badge = document.getElementById('status-badge');
    if (!scoreFill || !badge) return;

    scoreFill.style.width = `${score}%`;
    scoreFill.innerText = `${score}/100`;

    let statusText = "";
    let statusClass = "";

    if (score >= 90) { statusText = "Excellent"; statusClass = "excellent"; }
    else if (score >= 70) { statusText = "Good"; statusClass = "good"; }
    else if (score >= 40) { statusText = "Fair"; statusClass = "fair"; }
    else { statusText = "Poor"; statusClass = "poor"; }

    badge.innerText = statusText;
    badge.className = `badge ${statusClass}`;
}

function updateWeatherTheme(id, main) {
    const body = document.body;
    const icon = document.getElementById('weather-icon-main');
    
 
    body.classList.remove('theme-sunny', 'theme-cloudy', 'theme-rainy', 'theme-stormy');

    let themeClass = '';
    let iconClass = '';

  
    if (id === 800) { 
        themeClass = 'theme-sunny';
        iconClass = 'fa-solid fa-sun';
    } else if (id >= 801 && id <= 804) {
        themeClass = 'theme-cloudy';
        iconClass = 'fa-solid fa-cloud';
    } else if (id >= 500 && id <= 531) { 
        themeClass = 'theme-rainy';
        iconClass = 'fa-solid fa-cloud-showers-heavy';
    } else if (id >= 200 && id <= 232) { 
        themeClass = 'theme-stormy';
        iconClass = 'fa-solid fa-cloud-bolt';
    } else {
        themeClass = 'theme-default';
        iconClass = 'fa-solid fa-cloud-sun';
    }


    body.classList.add(themeClass);
    icon.className = `${iconClass} weather-icon-large`;
}


function updateKeyFactors(data) {
    const tempFactor = document.getElementById('factor-temp');
    const windFactor = document.getElementById('factor-wind');
    const weatherFactor = document.getElementById('factor-weather');


    if (data.temp >= 5 && data.temp <= 25) {
        tempFactor.className = "factor-item positive";
        tempFactor.querySelector('p').innerText = "Acceptable cycling temperature";
    } else {
        tempFactor.className = "factor-item negative";
        tempFactor.querySelector('p').innerText = "Temperature might be uncomfortable";
    }

    if (data.wind_speed <= 20) {
        windFactor.className = "factor-item positive";
        windFactor.querySelector('p').innerText = "Low wind, easy to cycle";
    } else {
        windFactor.className = "factor-item negative";
        windFactor.querySelector('p').innerText = "High winds will slow you down";
    }


    if (data.precipitation > 0 || (data.weather_main && data.weather_main.includes('Rain'))) {
        weatherFactor.className = "factor-item negative";
        weatherFactor.querySelector('p').innerText = "Rainy conditions, watch out!";
    } else {
        weatherFactor.className = "factor-item positive";
        weatherFactor.querySelector('p').innerText = "Dry conditions, great for cycling";
    }
}

function calculateCyclingScore(data) {
    let score = 100;

  
    if (data.temp < 5 || data.temp > 25) {
        score -= 20; 
    }
    
 
    if (data.wind_speed > 20) {
        score -= 30;
    }

  
    if (data.precipitation > 0 || (data.weather_main && data.weather_main.includes('Rain'))) {
        score -= 50; 
    }

    return Math.max(0, score);
}

/* ==========================================
   4. STATION SERVICE (MAP & SIDEBAR)
   ========================================== */
async function fetchStations() {
    if (!map) return;

    try {
        const response = await fetch('/api/stations');
        const rawData = await response.json();
        
        // Normalize the data format
        allStationsData = Array.isArray(rawData) ? (rawData[0]?.stations || rawData) : (rawData.stations || rawData);

        // Initial render
        renderMarkers();
    } catch (error) {
        console.error("Stations fetch failed:", error);
    }
}

function getMarkerIcon(value) {
    let color = '#dc3545'; 
    if (value > 10) color = '#00a86b';
    else if (value > 0) color = '#ffc107';

    return {
        path: google.maps.SymbolPath.CIRCLE, 
        fillColor: color,
        fillOpacity: 0.9,
        scale: 12, 
        strokeColor: 'white',
        strokeWeight: 2,
        labelOrigin: new google.maps.Point(0, 0) 
    };
}

function renderMarkers() {
    markers.forEach(m => m.setMap(null));
    markers = [];

    allStationsData.forEach(station => {
        const bikes = station.available_bikes !== undefined ? station.available_bikes : 0;
        const stands = station.available_bike_stands !== undefined ? station.available_bike_stands : 0;

        const displayValue = (currentMode === 'bikes') ? bikes : stands;

       
        const isHighlighted = (station.number === selectedStationNumber);

        const markerIcon = getMarkerIcon(displayValue);
        
        
        if (isHighlighted) {
            markerIcon.scale = 20; 
        }

        const marker = new google.maps.Marker({
            position: { lat: parseFloat(station.lat), lng: parseFloat(station.lng) },
            map: map,
            icon: markerIcon,
            label: {
                text: (displayValue || 0).toString(),
                color: 'white',
                fontSize: isHighlighted ? '14px' : '12px', 
                fontWeight: 'bold'
            }
        });

        marker.addListener("click", function() {
            showStationDetails(station);
            highlightStationOnMap(station, this);
        });

       
        if (isHighlighted) {
            currentHighlightedMarker = marker;
        }

        markers.push(marker);
    });
}


function closeDetailsPanel() {
    const panel = document.getElementById('details-panel');
    
    
    panel.classList.remove('active');

   
    if (currentHighlightedMarker) {
        let icon = currentHighlightedMarker.getIcon();
        if (icon) {
            icon.scale = 12;
            currentHighlightedMarker.setIcon(icon);
        }
        currentHighlightedMarker = null;
        selectedStationNumber = null;
    }
}

function highlightStationOnMap(station, marker) {
    if (!map) {
        console.error("Map instance not found!");
        return;
    }


    selectedStationNumber = station.number;
    if (currentHighlightedMarker && currentHighlightedMarker !== marker) {
        let oldIcon = currentHighlightedMarker.getIcon();
        if (oldIcon) {
            oldIcon.scale = 12;
            currentHighlightedMarker.setIcon(oldIcon);
        }
    }
    currentHighlightedMarker = marker;

  
    const lat = parseFloat(station.lat);
    const lng = parseFloat(station.lng || station.lon);
    const targetPos = { lat: lat, lng: lng };


    map.panTo(targetPos);

    
    setTimeout(() => {
        map.setZoom(17); 
    }, 300);

    
    let newIcon = marker.getIcon();
    if (newIcon) {
        newIcon.scale = 20;
        marker.setIcon(newIcon);
    }
}


function switchMapMode(mode) {
    currentMode = mode;
    
   
    document.getElementById('btn-show-bikes').classList.toggle('active', mode === 'bikes');
    document.getElementById('btn-show-spaces').classList.toggle('active', mode === 'spaces');

    renderMarkers(); 
}

/* ==========================================
   STATION DETAILS & VIEW SWITCHING
   ========================================== */


async function showStationDetails(station) {
    const panel = document.getElementById('details-panel');
    panel.classList.add('active');

    

    // 1. Populate initial data from the Marker for instant UI feedback
    document.getElementById('selected-station-name').innerText = station.name;
    document.getElementById('bikes-count').innerText = station.available_bikes;
    document.getElementById('stands-count').innerText = station.available_bike_stands || station.bike_stands;
    
    const mlValue = document.getElementById('predicted-value');
    if (mlValue) {
        mlValue.innerText = "Calculating..."; // Show loading state initially
    }
    
    switchDetailsView('info');
    
    const instruction = document.querySelector('.instruction');
    if (instruction) instruction.style.display = 'none';

    // 2. Fetch the comprehensive JSON data package from the backend
    try {
        const response = await fetch(`/api/stations/${station.number}`);
        const data = await response.json(); 
        
        console.log("Perfect data received from API:", data);

        // Key Fix A: Capture 24h forecast data and initialize the slider
        if (data.forecast_24h && data.forecast_24h.length > 0) {
            currentForecastData = data.forecast_24h;
            
            // Reset slider to 0 (Current Time) when opening a new station
            const slider = document.getElementById('time-slider');
            if (slider) slider.value = 0;
            
            // Display the current (0 hours ahead) prediction
            updateForecastDisplay(0); 
        } else if (mlValue && data.prediction !== undefined) {
            // Fallback if 24h array is missing
            mlValue.innerText = data.prediction;
        }

        // Key Fix B: Feed ONLY the 'history' array to the chart
        if (data.history && Array.isArray(data.history)) {
            updateChart(data.history);
        }
        
    } catch (e) {
        console.error("Failed to fetch station details:", e);
    }
}

/**
 * Updates the ML prediction number and time label based on the slider value.
 * @param {number} hoursAhead - The value from the range slider (0 to 23).
 */
function updateForecastDisplay(hoursAhead) {
    const mlValue = document.getElementById('predicted-value');
    const timeLabel = document.getElementById('forecast-time-label');

    if (!currentForecastData || currentForecastData.length === 0) return;

    // Find the specific forecast data for the selected hour
    const forecast = currentForecastData.find(f => f.hours_ahead == hoursAhead);

    if (forecast) {
        if (mlValue) {
            mlValue.innerText = forecast.prediction !== -1 ? forecast.prediction : "N/A";
        }
        
        if (timeLabel) {
            if (hoursAhead == 0) {
                timeLabel.innerText = `Current`;
            } else {
                timeLabel.innerText = `+${hoursAhead}h (${forecast.time_label})`;
            }
        }
    }
}

/**
 * 2. Station Info vs ML Forecast
 */
function switchDetailsView(viewName) {

    const infoView = document.getElementById('view-info');
    const mlView = document.getElementById('view-ml');
    
    if (infoView && mlView) {
        infoView.classList.toggle('active', viewName === 'info');
        mlView.classList.toggle('active', viewName === 'ml');
    }


    document.querySelectorAll('.d-tab').forEach(btn => {
        const isActive = btn.getAttribute('onclick').includes(viewName);
        btn.classList.toggle('active', isActive);
    });
}


function updateChart(history) {
    if (!Array.isArray(history)) {
        console.warn("Chart Error: 'history' is not an array. Received:", history);
        return;
    }

    const canvas = document.getElementById('predictionChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    if (window.predictionChart instanceof Chart) {
        window.predictionChart.destroy();
    }

    history.sort((a, b) => new Date(a.last_update) - new Date(b.last_update));

    const hourlyLabels = [];
    const hourlyData = [];
    const now = new Date();

    for (let i = 23; i >= 0; i--) {
        const targetTime = new Date(now);
        targetTime.setHours(now.getHours() - i, 0, 0, 0);

   
        const label = targetTime.getHours().toString().padStart(2, '0'); 
        hourlyLabels.push(label);

        if (history.length > 0) {
            const closest = history.reduce((prev, curr) => {
                const currTime = new Date(curr.last_update);
                const prevTime = new Date(prev.last_update);
                return Math.abs(currTime - targetTime) < Math.abs(prevTime - targetTime) ? curr : prev;
            });

            const diff = Math.abs(new Date(closest.last_update) - targetTime);
            if (diff < 40 * 60 * 1000) { 
                hourlyData.push(closest.available_bikes);
            } else {
                hourlyData.push(null); 
            }
        } else {
            hourlyData.push(null);
        }
    }

    window.predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hourlyLabels,
            datasets: [{
                label: 'Available Bikes',
                data: hourlyData,
                borderColor: '#00a86b',
                backgroundColor: 'rgba(0, 168, 107, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 1.5,
                pointRadius: 2,
                spanGaps: true 
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: (items) => items[0].label + ":00"
                    }
                }
            },
            scales: { 
                y: { 
                    beginAtZero: true,
                    ticks: { stepSize: 1 } 
                },
                x: { 
                    grid: { display: false },
                    ticks: { 
                        maxRotation: 0, 
                        autoSkip: true,    
                        maxTicksLimit: 12 
                    } 
                }
            }
        }
    });
}



function jumpToTab(contentId) {
    const targetTab = document.querySelector(`.tab-item[onclick*="${contentId}"]`);
    if (targetTab) {
        targetTab.click(); 
        const howToSection = document.getElementById('how-to-section');
        if (howToSection) {
            const offset = 80;
            const elementPosition = howToSection.getBoundingClientRect().top + window.pageYOffset;
            window.scrollTo({ top: elementPosition - offset, behavior: 'smooth' });
        }
    }
}

// --- Password Toggle Logic ---
function initPasswordToggle() {
    const toggleBtn = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

 
    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', function() {
    
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

         
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
            
    
            this.style.color = type === 'text' ? '#059669' : '#9ca3af';
        });
    }
}


async function subscribeToPlan(planName) {
    const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_name: planName })
    });

    const result = await response.json();

    if (result.success) {
        alert(`Successfully subscribed to ${planName}!`);
        window.location.reload(); 
    } else {
        alert("Subscription failed: " + result.message);
    }
}

/* ==========================================
    1. PLAN SELECTION 
   ========================================== */
function selectPlan(planName, btnElement) {
    const userName = window.CURRENT_USER_NAME;
    if (!userName || userName === "" || userName === "None") {
        alert("Please login first to subscribe!");
        window.location.href = "/login";
        return;
    }

    const card = btnElement.closest('.plan-card');
    if (card) {
        card.style.position = 'relative';
        const loader = document.createElement('div');
        loader.className = 'processing-overlay';
        loader.style = "position:absolute; top:0; left:0; width:100%; height:100%; background:rgba(255,255,255,0.9); display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:10; border-radius:15px;";
        loader.innerHTML = `
            <i class="fa-solid fa-spinner fa-spin" style="font-size: 2rem; color: #00a86b; margin-bottom: 10px;"></i>
            <p style="font-weight:bold; color:#333;">Securing your ${planName}...</p>
        `;
        card.appendChild(loader);
    }

    setTimeout(async () => {
        try {
            const response = await fetch('/api/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ plan_name: planName })
            });

            const result = await response.json();
            if (result.success) {
                window.location.href = "/profile"; 
            } else {
                alert("Subscription failed: " + result.message);
                const loader = card.querySelector('.processing-overlay');
                if (loader) loader.remove();
            }
        } catch (error) {
            alert("Connection error!");
        }
    }, 1500);
}

/* ==========================================
    2. RENEW LOGIC
   ========================================== */
async function renewPlan(btnElement) {
    btnElement.innerText = "Processing...";
    btnElement.disabled = true;

    try {
        const response = await fetch('/api/renew', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            alert("Awesome! Your subscription has been extended.");
            location.reload(); 
        } else {
            alert("Oops! " + result.message);
            btnElement.disabled = false;
            btnElement.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Renew Subscription';
        }
    } catch (error) {
        alert("Connection failed.");
        btnElement.disabled = false;
    }
}

/* ==========================================
    INITIALIZATION 
   ========================================== */
document.addEventListener('DOMContentLoaded', () => {
  
    if (typeof initPasswordToggle === "function") initPasswordToggle();

    
    if (window.location.pathname.includes('profile')) {
        const startDateElem = document.getElementById('start-date-display');
        const endDateElem = document.getElementById('end-date-display');
        const daysLeftElem = document.getElementById('days-left-badge');

       
        if (startDateElem && startDateElem.innerText.trim() !== "--" && startDateElem.innerText.trim() !== "") {
            const currentEnd = new Date(endDateElem.innerText);
            const today = new Date();
            const diffTime = currentEnd - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (daysLeftElem && !isNaN(diffDays)) {
                daysLeftElem.innerText = `(${diffDays > 0 ? diffDays : 0} days remaining)`;
            }
        }
    }


    const slider = document.getElementById('time-slider');
    if (slider) {
        slider.addEventListener('input', (e) => updateForecastDisplay(e.target.value));
    }

    const openRouteBtn = document.getElementById('toggle-route-btn');
    const closeRouteBtn = document.getElementById('close-route-btn');
    const routePanel = document.getElementById('route-planner-panel');
    const calcRouteBtn = document.getElementById('calc-route-btn');

    if (calcRouteBtn) calcRouteBtn.addEventListener('click', calculateAndDisplayRoute);
    if (openRouteBtn && closeRouteBtn && routePanel) {
        openRouteBtn.addEventListener('click', () => routePanel.classList.add('active'));
        closeRouteBtn.addEventListener('click', () => routePanel.classList.remove('active'));
    }
});

setInterval(fetchWeather, 600000);


/* ==========================================
   ROUTE PLANNER: CORE LOGIC
   ========================================== */
/**
 * Helper: Calculate distance between two coordinates using Haversine formula
 */

function getDirections(request) {
    return new Promise((resolve, reject) => {
        directionsService.route(request, (response, status) => {
            if (status === 'OK') resolve(response);
            else reject(status);
        });
    });
}

function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c; // Distance in km
}

/**
 * Helper: Find the nearest station based on availability criteria
 * @param {number} lat - Target latitude
 * @param {number} lng - Target longitude
 * @param {string} needType - 'bikes' (needs available bikes) or 'stands' (needs empty stands)
 */
function findNearestStation(lat, lng, needType) {
    let bestStation = null;
    let minDistance = Infinity;

    // 'allStationsData' is your global array containing all 115 stations
    allStationsData.forEach(station => {
        const hasBikes = station.available_bikes > 0;
        const hasStands = (station.available_bike_stands > 0 || station.stands_count > 0);

        // Skip stations that don't meet our criteria
        if (needType === 'bikes' && !hasBikes) return;
        if (needType === 'stands' && !hasStands) return;

        const dist = getDistance(lat, lng, parseFloat(station.lat), parseFloat(station.lng));
        if (dist < minDistance) {
            minDistance = dist;
            bestStation = station;
        }
    });

    return bestStation;
}

/**
 * Main Function: Calculate and render the multi-stop route
 */
/**
 * Main Function: Calculate and render the multi-stop route with times and dashed lines
 */
async function calculateAndDisplayRoute() {
    const originStr = document.getElementById('route-origin').value;
    const destStr = document.getElementById('route-destination').value;
    const resultsContainer = document.getElementById('route-results');

    if (!originStr || !destStr) {
        alert("Please enter both origin and destination.");
        return;
    }

    if (!directionsService) directionsService = new google.maps.DirectionsService();


    routeRenderers.forEach(r => r.setMap(null));
    routeRenderers = [];

    resultsContainer.innerHTML = '<p style="text-align:center;">Calculating best route...</p>';
    const geocoder = new google.maps.Geocoder();

    try {
        
        const originResult = await geocoder.geocode({ address: originStr + ", Dublin, Ireland" });
        const originLoc = originResult.results[0].geometry.location;

        const destResult = await geocoder.geocode({ address: destStr + ", Dublin, Ireland" });
        const destLoc = destResult.results[0].geometry.location;

        
        const startStation = findNearestStation(originLoc.lat(), originLoc.lng(), 'bikes');
        const endStation = findNearestStation(destLoc.lat(), destLoc.lng(), 'stands');

        if (!startStation || !endStation) {
            resultsContainer.innerHTML = '<p style="color:red;">Could not find valid stations nearby.</p>';
            return;
        }

        const startStationLoc = { lat: parseFloat(startStation.lat), lng: parseFloat(startStation.lng) };
        const endStationLoc = { lat: parseFloat(endStation.lat), lng: parseFloat(endStation.lng) };

       
        const walk1Req = getDirections({ origin: originLoc, destination: startStationLoc, travelMode: 'WALKING' });
        const bikeReq = getDirections({ origin: startStationLoc, destination: endStationLoc, travelMode: 'BICYCLING' });
        const walk2Req = getDirections({ origin: endStationLoc, destination: destLoc, travelMode: 'WALKING' });

 
        const [walk1Res, bikeRes, walk2Res] = await Promise.all([walk1Req, bikeReq, walk2Req]);

       
      
        routeCustomMarkers.forEach(m => m.setMap(null));
        routeCustomMarkers = [];

       
        function createRouteMarker(position, labelText, color, stationData = null) {
            const marker = new google.maps.Marker({
                position: position,
                map: map,
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    fillColor: color, fillOpacity: 1,
                    strokeWeight: 2, strokeColor: 'white',
                    scale: 14 
                },
                label: { text: labelText, color: 'white', fontWeight: 'bold' },
                zIndex: 1002,
                cursor: stationData ? 'pointer' : 'default'
            });

            if (stationData) {
                marker.addListener('click', () => {
      
                    showStationDetails(stationData);
                });
            }

            routeCustomMarkers.push(marker);
        }


        createRouteMarker(originLoc, 'A', '#ea4335'); 
        createRouteMarker(startStationLoc, 'B', '#00a86b', startStation); 
        createRouteMarker(endStationLoc, 'C', '#00a86b', endStation); 
        createRouteMarker(destLoc, 'D', '#ea4335');

  
        const renderWalk1 = new google.maps.DirectionsRenderer({
            map: map, suppressMarkers: true, 
            polylineOptions: { strokeColor: '#2196F3', strokeOpacity: 0, icons: [{ icon: { path: 'M 0,-1 0,1', strokeOpacity: 1, scale: 5 }, offset: '0', repeat: '20px' }] }
        });
        renderWalk1.setDirections(walk1Res);
        routeRenderers.push(renderWalk1);

       
        const renderBike = new google.maps.DirectionsRenderer({
            map: map, suppressMarkers: true, 
            polylineOptions: { strokeColor: '#008b57', strokeWeight: 8, strokeOpacity: 0.9 }
        });
        renderBike.setDirections(bikeRes);
        routeRenderers.push(renderBike);

        const renderWalk2 = new google.maps.DirectionsRenderer({
            map: map, suppressMarkers: true,
            polylineOptions: { strokeColor: '#2196F3', strokeOpacity: 0, icons: [{ icon: { path: 'M 0,-1 0,1', strokeOpacity: 1, scale: 5 }, offset: '0', repeat: '20px' }] }
        });
        renderWalk2.setDirections(walk2Res);
        routeRenderers.push(renderWalk2);

     
        const walk1Time = walk1Res.routes[0].legs[0].duration.text;
        const bikeTime = bikeRes.routes[0].legs[0].duration.text;
        const walk2Time = walk2Res.routes[0].legs[0].duration.text;

        resultsContainer.innerHTML = `
            <div style="background-color: #f8f9fa; padding: 18px; border-radius: 8px; border: 1px solid #e0e0e0;">
                <h4 style="margin: 0 0 15px 0; color: #00a86b; font-size: 16px;">Route Found ! </h4>
                
                <div style="display: flex; flex-direction: column; gap: 16px;">
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 14px;">
                        <div style="display: flex; align-items: center;">
                            <span style="background:#ea4335; color:white; border-radius:50%; width:24px; height:24px; display:inline-flex; justify-content:center; align-items:center; font-size:12px; margin-right:10px; font-weight:bold; flex-shrink:0;">A</span> 
                            <div>
                                <i class="fa-solid fa-person-walking" style="width: 18px; color: #888; text-align: center; margin-right: 4px;"></i>
                                Walk to <strong>${startStation.name}</strong> <span style="color:#00a86b; font-weight:bold; font-size:12px; margin-left:4px;">(B)</span>
                            </div>
                        </div>
                        <span style="color:#555; font-weight:bold; white-space: nowrap; margin-left: 10px;">${walk1Time}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 14px;">
                        <div style="display: flex; align-items: center;">
                            <span style="background:#00a86b; color:white; border-radius:50%; width:24px; height:24px; display:inline-flex; justify-content:center; align-items:center; font-size:12px; margin-right:10px; font-weight:bold; flex-shrink:0;">B</span> 
                            <div>
                                <i class="fa-solid fa-bicycle" style="width: 18px; color: #00a86b; text-align: center; margin-right: 4px;"></i>
                                Cycle to <strong>${endStation.name}</strong> <span style="color:#ea4335; font-weight:bold; font-size:12px; margin-left:4px;">(C)</span>
                            </div>
                        </div>
                        <span style="color:#555; font-weight:bold; white-space: nowrap; margin-left: 10px;">${bikeTime}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 14px;">
                        <div style="display: flex; align-items: center;">
                            <span style="background:#00a86b; color:white; border-radius:50%; width:24px; height:24px; display:inline-flex; justify-content:center; align-items:center; font-size:12px; margin-right:10px; font-weight:bold; flex-shrink:0;">C</span> 
                            <div>
                                <i class="fa-solid fa-person-walking" style="width: 18px; color: #888; text-align: center; margin-right: 4px;"></i>
                                Walk to destination
                            </div>
                        </div>
                        <span style="color:#555; font-weight:bold; white-space: nowrap; margin-left: 10px;">${walk2Time}</span>
                    </div>

                    <div style="display: flex; align-items: center; font-size: 14px; margin-top: -4px;">
                        <span style="background:#ea4335; color:white; border-radius:50%; width:24px; height:24px; display:inline-flex; justify-content:center; align-items:center; font-size:12px; margin-right:10px; font-weight:bold; flex-shrink:0;">D</span> 
                        <div>
                            <i class="fa-solid fa-flag-checkered" style="width: 18px; color: #ea4335; text-align: center; margin-right: 4px;"></i>
                            <strong>Arrive at destination</strong>
                        </div>
                    </div>

                </div>
            </div>
        `;

    } catch (error) {
        console.error("Routing error:", error);
        resultsContainer.innerHTML = '<p style="color:red;">Routing failed. Please try different locations.</p>';
    }
}