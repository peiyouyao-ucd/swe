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

   
    document.getElementById('selected-station-name').innerText = station.name;
    
   
    document.getElementById('bikes-count').innerText = station.available_bikes;
    document.getElementById('stands-count').innerText = station.available_bike_stands || station.bike_stands;
    
 
    const mlValue = document.getElementById('predicted-value');
    if (mlValue) {
        mlValue.innerText = station.predicted_bikes !== undefined ? station.predicted_bikes : "Calculating...";
    }
    
   
    switchDetailsView('info');

    
    const instruction = document.querySelector('.instruction');
    if (instruction) instruction.style.display = 'none';

  
    try {
        const response = await fetch(`/api/stations/${station.number}`);
        let history = await response.json(); 
        
      
        if (history && Array.isArray(history)) {
            history.sort((a, b) => a.last_update - b.last_update);
        }

        console.log("Sorted history:", history); 
        updateChart(history);
        
    } catch (e) {
        console.error("Error fetching station history:", e);
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
    const canvas = document.getElementById('predictionChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    if (window.predictionChart instanceof Chart) {
        window.predictionChart.destroy();
    }

    
    history.sort((a, b) => new Date(a.last_update) - new Date(b.last_update));

    
    const labels = history.map(h => {
        let dateStr = h.last_update;
        if (typeof dateStr === 'string') {
            dateStr = dateStr.replace(/-/g, "/");
        }
        const dateObj = new Date(dateStr);
        if (isNaN(dateObj)) return h.last_update;
        
        return dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    });


    const data = history.map(h => h.available_bikes);

    window.predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Available Bikes',
                data: data,
                borderColor: '#00a86b',
                backgroundColor: 'rgba(0, 168, 107, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 1.5,      
                pointRadius: 2,        
                pointHoverRadius: 5,   
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { 
                y: { 
                    beginAtZero: true,
                    ticks: { stepSize: 1 } 
                },
                x: { 
                    ticks: { 
                        maxRotation: 0, 
                        autoSkip: true,    
                        maxTicksLimit: 8  
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



function selectPlan(planName) {
   
    const userName = "{{ user_name or '' }}"; 

    if (!userName) {
        alert("Please log in to choose the " + planName + " plan!");
        
        window.location.href = "{{ url_for('auth.login') }}";
    } else {
      
        alert("Excellent choice! Processing your " + planName + " plan...");
    }
}


/* ==========================================
   6. INITIALIZATION
   ========================================== */
document.addEventListener('DOMContentLoaded', () => {
    initPasswordToggle();
   
    const hash = window.location.hash.substring(1);
    if (hash) {
      
        setTimeout(() => jumpToTab(hash), 300);
    }

   
    if (window.location.pathname.includes('profile')) {
        console.log("Welcome to your profile, Sarah!");
    }
});


setInterval(fetchWeather, 600000);


