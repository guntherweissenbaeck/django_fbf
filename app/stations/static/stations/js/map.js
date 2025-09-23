/**
 * @file map.js
 * @brief Render the Wildvogelhilfe map using Leaflet and FBF backend data.
 */

const MAP_CONFIG = window.stationMapConfig || {};

/**
 * @brief Controller class wrapping Leaflet integration and UI helpers.
 */
class WildvogelhilfeMap {
    constructor() {
        this.map = null;
        this.markers = [];
        this.stations = [];
        this.filteredMarkers = [];
        this.index = { plz: new Map(), city: new Map() };
        this.lastQuery = '';
        this.init();
    }

    async init() {
        this.initMap();
        await this.loadStations();
        this.buildIndex();
        this.initSearchUI();
        this.addMarkersToMap();
        this.updateStats();
        this.initDownloadButton();
        this.initReportButton();
        this.initLeafletLocateControl();
    }

    initMap() {
        // Karte auf Deutschland zentrieren
        this.map = L.map('map').setView([51.1657, 10.4515], 6);

        // OpenStreetMap Tiles hinzufügen
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18
        }).addTo(this.map);

        // Benutzerdefinierte Icons
        this.createCustomIcons();
    }

    createCustomIcons() {
        // CSS-Variablen aus dem DOM lesen
        const getStatusColor = (statusVar) => {
            return getComputedStyle(document.documentElement)
                .getPropertyValue(statusVar).trim();
        };
        
        const activeColor = getStatusColor('--status-active');
        const inactiveColor = getStatusColor('--status-inactive');
        const nabuColor = getStatusColor('--status-nabu');
        
        // Icon für aktive Wildvogelhilfen
        this.defaultIcon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="
                background-color: ${activeColor};
                width: 20px;
                height: 20px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            "></div>`,
            iconSize: [26, 26],
            iconAnchor: [13, 13]
        });

        // Icon für inaktive Wildvogelhilfen
        this.inactiveIcon = L.divIcon({
            className: 'custom-marker-inactive',
            html: `<div style="
                background-color: ${inactiveColor};
                width: 20px;
                height: 20px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            "></div>`,
            iconSize: [26, 26],
            iconAnchor: [13, 13]
        });

        // Icon für NABU Wildvogelhilfen
        this.nabuIcon = L.divIcon({
            className: 'custom-marker-nabu',
            html: `<div style="
                background-color: ${nabuColor};
                width: 20px;
                height: 20px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            "></div>`,
            iconSize: [26, 26],
            iconAnchor: [13, 13]
        });
    }

    async loadStations() {
        const endpoint = MAP_CONFIG.dataUrl;
        try {
            const response = await fetch(endpoint, {
                credentials: 'same-origin',
                cache: 'no-cache',
                headers: { 'Accept': 'application/json' }
            });

            if (response.status === 304) {
                console.log('ℹ️ Unveränderte Stationsdaten (304) – bestehende Marker werden weiterverwendet.');
                return; // vorhandene this.stations beibehalten
            }

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            if (!Array.isArray(data)) {
                throw new Error('Ungültiges Antwortformat (kein Array)');
            }
            this.stations = data;
            console.log(`✅ ${this.stations.length} Stationen geladen`);
        } catch (error) {
            console.error('❌ Fehler beim Laden der Stationen:', error);
            this.showError('Stationsdaten konnten nicht geladen werden. Bitte später erneut versuchen.');
        }
    }

    // Removed demo data fallback to avoid confusing partial dataset scenarios

    addMarkersToMap() {
    // Entferne vorhandene Marker (bei Re-Render nach Filter)
    this.markers.forEach(m => this.map.removeLayer(m));
    this.markers = [];
    
    let markerCount = 0;
    let skippedCount = 0;
    
        this.stations.forEach(station => {
            // Koordinaten validieren
            const lat = parseFloat(station.latitude);
            const lng = parseFloat(station.longitude);
            
            // Debug: Ungültige Koordinaten protokollieren
            if (isNaN(lat) || isNaN(lng) || lat === 0 || lng === 0) {
                console.warn('Station ohne gültige Koordinaten:', station.name, 'lat:', station.latitude, 'lng:', station.longitude);
                skippedCount++;
                return;
            }
            
            // Icon basierend auf Spezialisierung wählen
            const icon = this.getIconForStation(station);
            
            try {
                // Marker erstellen
                const marker = L.marker([lat, lng], {
                    icon: icon
                }).addTo(this.map);
                
                // Referenz für Highlighting / Suche
                marker._station = station;

                // Popup-Inhalt erstellen
                const popupContent = this.createPopupContent(station);
                marker.bindPopup(popupContent);

                // Marker zur Liste hinzufügen
                this.markers.push(marker);
                markerCount++;
            } catch (error) {
                console.error('Fehler beim Erstellen des Markers für:', station.name, error);
                skippedCount++;
            }
        });

        console.log(`Marker erstellt: ${markerCount}, Übersprungen: ${skippedCount}, Total Stationen: ${this.stations.length}`);

        // Karte so zoomen, dass alle Marker sichtbar sind
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }

    getIconForStation(station) {
        // Status-basierte Icon-Auswahl (hat Priorität)
        const status = station.status ? station.status.toLowerCase() : 'aktiv';
        
        switch (status) {
            case 'inaktiv':
                return this.inactiveIcon;
            case 'nabu':
                return this.nabuIcon;
            case 'aktiv':
            default:
                // Für aktive Stationen: Prüfen ob es sich um eine Greifvogel-Spezialisierung handelt
                if (station.specialization && 
                    station.specialization.toLowerCase().includes('greifvogel')) {
                    return this.greifvogelIcon;
                }
                return this.defaultIcon;
        }
    }

    createPopupContent(station) {
        let content = `<div class="popup-content">`;
        content += `<h4>${station.name}</h4>`;
        
        // Status-Anzeige nur für inaktive Stationen
        if (station.status && station.status.toLowerCase() === 'inaktiv') {
            const inactiveColor = getComputedStyle(document.documentElement)
                .getPropertyValue('--status-inactive').trim();
            content += `<div class="status" style="background: ${inactiveColor}; color: white; padding: 2px 6px; border-radius: 12px; font-size: 0.8rem; display: inline-block; margin-bottom: 0.5rem;">⚠️ inaktiv</div>`;
        }
        
        if (station.specialization) {
            content += `<div class="specialization">${station.specialization}</div>`;
        }
        
        content += `<div class="address">${station.address}</div>`;
        
        content += `<div class="contact">`;
        if (station.phone) {
            content += `<strong>Tel:</strong> <a href="tel:${station.phone.replace(/\s/g, '')}">${station.phone}</a><br>`;
        }
        if (station.email) {
            content += `<strong>E-Mail:</strong> <a href="mailto:${station.email}">${station.email}</a><br>`;
        }
        if (station.website) {
            content += `<strong>Website:</strong> <a href="${station.website}" target="_blank" rel="noopener noreferrer">${station.website}</a>`;
        }
        content += `</div>`;
        if (station.note) {
            content += `<div class="note" style="margin-top:6px;font-size:0.85rem;color:var(--gray-700);line-height:1.2;">${station.note}</div>`;
        }
        
        content += `</div>`;
        return content;
    }

    updateStats() {
        const statsElement = document.getElementById('station-count');
        if (statsElement) {
            const totalStations = this.stations.length;
            
            let statsText = `${totalStations} Wildvogelhilfen gefunden`;
            
            statsElement.textContent = statsText;
        }
    }

    initDownloadButton() {
        const downloadBtn = document.getElementById('download-btn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                this.downloadJsonData();
            });
        }
    }

    downloadJsonData() {
        try {
            // JSON-Daten vorbereiten
            const jsonData = JSON.stringify(this.stations, null, 2);
            
            // Blob erstellen
            const blob = new Blob([jsonData], { type: 'application/json' });
            
            // Download-URL erstellen
            const url = window.URL.createObjectURL(blob);
            
            // Temporären Download-Link erstellen
            const downloadLink = document.createElement('a');
            downloadLink.href = url;
            downloadLink.download = `wildvogelhilfen-${new Date().toISOString().split('T')[0]}.json`;
            downloadLink.style.display = 'none';
            
            // Link zum DOM hinzufügen, klicken und wieder entfernen
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
            
            // URL wieder freigeben
            window.URL.revokeObjectURL(url);
            
            // Feedback für den Benutzer
            const originalText = document.getElementById('download-btn').textContent;
            document.getElementById('download-btn').textContent = '✅ Download gestartet!';
            document.getElementById('download-btn').style.background = 'linear-gradient(135deg, #28a745, #20c997)';
            
            setTimeout(() => {
                document.getElementById('download-btn').textContent = originalText;
                document.getElementById('download-btn').style.background = '';
            }, 2000);
            
        } catch (error) {
            console.error('Fehler beim Download:', error);
            
            // Fallback: Daten in neuem Tab anzeigen
            const jsonData = JSON.stringify(this.stations, null, 2);
            const newWindow = window.open();
            newWindow.document.write('<pre>' + jsonData + '</pre>');
            newWindow.document.title = 'Wildvogelhilfen JSON-Daten';
            
            // Feedback für den Benutzer
            const originalText = document.getElementById('download-btn').textContent;
            document.getElementById('download-btn').textContent = '📋 In neuem Tab geöffnet';
            
            setTimeout(() => {
                document.getElementById('download-btn').textContent = originalText;
            }, 3000);
        }
    }

    initReportButton() {
        const reportBtn = document.getElementById('report-btn');
        if (reportBtn) {
            reportBtn.addEventListener('click', () => {
                this.openReportForm();
            });
        }
    }

    openReportForm() {
        if (MAP_CONFIG.reportUrl) {
            window.open(MAP_CONFIG.reportUrl, '_blank', 'noopener');
            return;
        }

        alert('Aktuell steht kein Formular für neue Stationen zur Verfügung. Bitte kontaktieren Sie das FBF-Team per E-Mail.');
    }

    // --- Leaflet Locate Control ---
    initLeafletLocateControl() {
        // Leaflet's eingebaute Locate-Funktion verwenden
        const locateControl = L.control.locate({
            position: 'topright',
            strings: {
                title: "Zeige meinen Standort",
                popup: "Du bist innerhalb von {distance} {unit} von diesem Punkt",
                outsideMapBoundsMsg: "Du befindest dich außerhalb des sichtbaren Kartenbereichs"
            },
            locateOptions: {
                maxZoom: 12,
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 Minuten Cache
            },
            flyTo: true,
            keepCurrentZoomLevel: false,
            clickBehavior: {
                inView: 'stop',
                outOfView: 'setView'
            },
            showPopup: false, // Wir erstellen eigene Popups
            circleStyle: {
                color: '#ff4444',
                fillColor: '#ff4444',
                fillOpacity: 0.1,
                weight: 2
            },
            markerStyle: {
                color: '#ff4444',
                fillColor: '#ff4444'
            },
            metric: true,
            onLocationError: (err) => {
                console.error('Standortfehler:', err);
                alert('Standortbestimmung fehlgeschlagen: ' + err.message);
            },
            onLocationOutsideMapBounds: (context) => {
                console.warn('Standort außerhalb der Kartengrenzen');
                alert(context.options.strings.outsideMapBoundsMsg);
            }
        }).addTo(this.map);

        // Event-Listener für erfolgreiche Standortbestimmung
        this.map.on('locationfound', (e) => {
            console.log(`📍 Standort gefunden: ${e.latlng.lat}, ${e.latlng.lng} (Genauigkeit: ${Math.round(e.accuracy)}m)`);
            
            // Nächste Wildvogelhilfen finden und anzeigen
            this.findAndShowNearestStations(e.latlng.lat, e.latlng.lng, e.accuracy);
        });
    }

    findAndShowNearestStations(userLat, userLng, accuracy) {
        // Berechne Entfernungen zu allen Stationen
        const stationsWithDistance = this.stations
            .filter(station => {
                const lat = parseFloat(station.latitude);
                const lng = parseFloat(station.longitude);
                return !isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0;
            })
            .map(station => {
                const lat = parseFloat(station.latitude);
                const lng = parseFloat(station.longitude);
                const distance = this.calculateDistance(userLat, userLng, lat, lng);
                return { ...station, distance };
            })
            .sort((a, b) => a.distance - b.distance)
            .slice(0, 5); // Top 5 nächste Stationen

        if (stationsWithDistance.length > 0) {
            console.log('🔍 Nächste Wildvogelhilfen:', stationsWithDistance.map(s => `${s.name} (${s.distance.toFixed(1)}km)`));
            
            // Info-Panel mit nächsten Stationen erstellen
            const nearestList = stationsWithDistance
                .map(station => `<li><strong>${station.name}</strong><br><small>${station.address} (${station.distance.toFixed(1)}km)</small></li>`)
                .join('');

            // Popup mit nächsten Stationen anzeigen
            const popup = L.popup()
                .setLatLng([userLat, userLng])
                .setContent(`
                    <div style="max-width: 280px;">
                        <div style="text-align: center; margin-bottom: 0.5rem;">
                            <strong>📍 Ihr Standort</strong><br>
                            <small>Genauigkeit: ±${Math.round(accuracy)}m</small>
                        </div>
                        <div>
                            <strong>🏥 Nächste Wildvogelhilfen:</strong>
                            <ol style="margin: 0.5rem 0; padding-left: 1.2rem; font-size: 0.9rem; line-height: 1.3;">
                                ${nearestList}
                            </ol>
                        </div>
                    </div>
                `)
                .openOn(this.map);
        }
    }

    calculateDistance(lat1, lng1, lat2, lng2) {
        // Haversine-Formel für Entfernung zwischen zwei Koordinaten
        const R = 6371; // Erdradius in km
        const dLat = this.toRadians(lat2 - lat1);
        const dLng = this.toRadians(lng2 - lng1);
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
                  Math.sin(dLng/2) * Math.sin(dLng/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    toRadians(degrees) {
        return degrees * (Math.PI/180);
    }

    // --- Suche ---
    buildIndex() {
        // Index wird nicht mehr benötigt, da wir direkt in den Feldern suchen
        // Diese Funktion bleibt für Kompatibilität, macht aber nichts mehr
    }

    initSearchUI() {
        this.searchInput = document.getElementById('search-input');
        this.searchBtn = document.getElementById('search-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.resultsBox = document.getElementById('search-results');
        if (!this.searchInput) return;

        const handle = () => {
            const q = this.searchInput.value.trim();
            this.performSearch(q);
        };
        this.searchBtn?.addEventListener('click', handle);
        this.searchInput.addEventListener('input', (e) => {
            const q = e.target.value.trim();
            if (q.length === 0) {
                this.clearSearch();
            } else {
                this.performSearch(q, true);
            }
        });
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); handle(); }
            if (e.key === 'Escape') { this.clearSearch(); }
            if (['ArrowDown','ArrowUp'].includes(e.key)) { this.navigateResults(e.key); e.preventDefault(); }
        });
        this.clearBtn?.addEventListener('click', () => this.clearSearch());
        document.addEventListener('click', (e) => {
            if (!this.resultsBox.contains(e.target) && e.target !== this.searchInput) {
                this.hideResults();
            }
        });
    }

    performSearch(query, live=false) {
        this.lastQuery = query;
        if (!query) { this.clearSearch(); return; }
        const qLower = query.toLowerCase();
        
        // Suche nur in name, address und plz
        let candidates = this.stations.filter(station => {
            // Name durchsuchen
            if (station.name && station.name.toLowerCase().includes(qLower)) {
                return true;
            }
            
            // Adresse durchsuchen
            if (station.address && station.address.toLowerCase().includes(qLower)) {
                return true;
            }
            
            // PLZ durchsuchen (exakte Übereinstimmung oder Anfang)
            if (station.plz && (station.plz === query || station.plz.startsWith(query))) {
                return true;
            }
            
            return false;
        });
        
        console.log('🔎 Suche', query, 'Treffer:', candidates.length);
        this.renderResults(candidates.slice(0, 25));
        if (!live && candidates.length > 0) {
            this.focusStations(candidates);
        }
    }

    focusStations(stations) {
        // Bounds über ausgewählte Stationen
        const pts = stations.filter(s => {
            const lat = parseFloat(s.latitude);
            const lng = parseFloat(s.longitude);
            return !isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0;
        }).map(s => [parseFloat(s.latitude), parseFloat(s.longitude)]);
        if (pts.length === 1) {
            this.map.flyTo(pts[0], 11, { duration: 0.8 });
        } else if (pts.length > 1) {
            const group = L.featureGroup(pts.map(p => L.marker(p)));
            this.map.fitBounds(group.getBounds().pad(0.2));
        }
        // Marker hervorheben
        this.highlightMarkers(stations);
    }

    highlightMarkers(selected) {
        const set = new Set(selected.map(s => s.name+':'+s.plz));
        this.markers.forEach(m => {
            const st = m._station;
            if (st && set.has(st.name+':'+st.plz)) {
                m.getElement()?.classList.add('marker-highlight');
            } else {
                m.getElement()?.classList.remove('marker-highlight');
            }
        });
    }

    renderResults(list) {
        if (!this.resultsBox) return;
        if (this.lastQuery.length === 0) { this.resultsBox.innerHTML=''; this.hideResults(); return; }
        if (list.length === 0) {
            this.resultsBox.innerHTML = '<div style="padding:0.6rem;">Keine Treffer</div>';
            this.showResults();
            return;
        }
        const html = '<ul>' + list.map((st,i) => {
            const city = st._city ? st._city.charAt(0).toUpperCase()+st._city.slice(1) : '';
            return `<li data-idx="${i}"><strong>${st.plz||''}</strong> ${city} <span class="meta">${st.name}</span></li>`;
        }).join('') + '</ul>';
        this.resultsBox.innerHTML = html;
        this.showResults();
        this.resultsBox.querySelectorAll('li').forEach((li,i) => {
            li.addEventListener('click', () => {
                const st = list[i];
                this.focusStations([st]);
                this.hideResults();
            });
        });
    }

    navigateResults(direction) {
        const items = Array.from(this.resultsBox.querySelectorAll('li'));
        if (items.length === 0) return;
        let idx = items.findIndex(li => li.classList.contains('active'));
        if (direction === 'ArrowDown') idx = (idx + 1) % items.length; else idx = (idx - 1 + items.length) % items.length;
        items.forEach(li => li.classList.remove('active'));
        items[idx].classList.add('active');
        const clickEvt = new Event('click');
        items[idx].dispatchEvent(clickEvt);
    }

    clearSearch() {
        if (this.searchInput) this.searchInput.value='';
        this.lastQuery='';
        this.hideResults();
        this.highlightMarkers([]);
    }
    hideResults(){ this.resultsBox?.classList.add('hidden'); }
    showResults(){ this.resultsBox?.classList.remove('hidden'); }
    
    getRegionName(plzPrefix) {
        const regionMap = {
            '0': 'PLZ 0',
            '1': 'PLZ 1', 
            '2': 'PLZ 2',
            '3': 'PLZ 3',
            '4': 'PLZ 4',
            '5': 'PLZ 5',
            '6': 'PLZ 6',
            '7': 'PLZ 7',
            '8': 'PLZ 8',
            '9': 'PLZ 9',
            'österreich': 'Österreich',
            'schweiz': 'Schweiz',
            'italien': 'Italien'
        };
        return regionMap[plzPrefix] || 'Unbekannt';
    }

    showError(message) {
        const statsElement = document.getElementById('station-count');
        if (statsElement) {
            statsElement.innerHTML = `<span style="color: red;">⚠️ ${message}</span>`;
        }
    }
}

// Karte initialisieren wenn DOM geladen ist
document.addEventListener('DOMContentLoaded', () => {
    new WildvogelhilfeMap();
    
    // Widget-Funktionalität nur auf der Hauptseite
    if (document.getElementById('widget-toggle-btn')) {
        new WidgetManager();
    }
});

// Widget-Manager Klasse
class WidgetManager {
    constructor() {
        this.currentConfig = {
            width: '800',
            height: '600',
            includeSearch: true
        };
        this.baseUrl = window.location.origin + window.location.pathname.replace('index.html', '');
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateWidgetCode();
    }

    setupEventListeners() {
        // Toggle-Button
        const toggleBtn = document.getElementById('widget-toggle-btn');
        const widgetContent = document.getElementById('widget-content');
        const toggleIcon = document.getElementById('widget-toggle-icon');

        toggleBtn.addEventListener('click', () => {
            const isVisible = widgetContent.style.display !== 'none';
            widgetContent.style.display = isVisible ? 'none' : 'block';
            toggleIcon.textContent = isVisible ? '▼' : '▲';
        });

        // Größen-Buttons
        document.querySelectorAll('.size-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Alle Buttons deaktivieren
                document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
                // Aktuellen Button aktivieren
                e.target.classList.add('active');
                
                // Konfiguration aktualisieren
                this.currentConfig.width = e.target.dataset.width;
                this.currentConfig.height = e.target.dataset.height;
                this.updateWidgetCode();
            });
        });

        // Suchfunktion Checkbox
        document.getElementById('include-search').addEventListener('change', (e) => {
            this.currentConfig.includeSearch = e.target.checked;
            this.updateWidgetCode();
        });

        // Code kopieren
        document.getElementById('copy-widget-code').addEventListener('click', () => {
            this.copyToClipboard();
        });

        // Vorschau anzeigen
        document.getElementById('preview-widget').addEventListener('click', () => {
            this.showPreview();
        });
    }

    updateWidgetCode() {
        const { width, height, includeSearch } = this.currentConfig;
        
        const searchParam = !includeSearch ? '?hideSearch=true' : '';
        const widgetUrl = `${this.baseUrl}widget.html${searchParam}`;
        
        const code = `<!-- Wildvogelhilfe Karte Widget -->
<iframe 
    src="${widgetUrl}"
    width="${width}" 
    height="${height}"
    frameborder="0"
    style="border: 1px solid #ddd; border-radius: 8px; max-width: 100%;"
    title="Wildvogelhilfe Karte"
    loading="lazy">
    <p>Ihr Browser unterstützt keine iframes. 
    <a href="${widgetUrl}" target="_blank">Karte in neuem Fenster öffnen</a></p>
</iframe>`;

        document.getElementById('widget-code').value = code;
    }

    async copyToClipboard() {
        const codeTextarea = document.getElementById('widget-code');
        const copyBtn = document.getElementById('copy-widget-code');
        const originalText = copyBtn.textContent;

        try {
            await navigator.clipboard.writeText(codeTextarea.value);
            copyBtn.textContent = '✅ Kopiert!';
            copyBtn.style.background = '#28a745';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.background = '#4a7c59';
            }, 2000);
        } catch (err) {
            // Fallback für ältere Browser
            codeTextarea.select();
            document.execCommand('copy');
            copyBtn.textContent = '✅ Kopiert!';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        }
    }

    showPreview() {
        const previewContainer = document.getElementById('widget-preview-container');
        const previewFrame = document.getElementById('widget-preview');
        const { width, height, includeSearch } = this.currentConfig;
        
        const searchParam = !includeSearch ? '?hideSearch=true' : '';
        const widgetUrl = `${this.baseUrl}widget.html${searchParam}`;
        
        // Vorschau-Container anzeigen
        previewContainer.style.display = 'block';
        
        // Preview-Frame Größe setzen
        const previewWidth = width === '100%' ? '100%' : Math.min(parseInt(width), 800) + 'px';
        const previewHeight = Math.min(parseInt(height), 500) + 'px';
        
        previewFrame.style.width = previewWidth;
        previewFrame.style.height = previewHeight;
        previewFrame.src = widgetUrl;
        
        // Scroll zur Vorschau
        previewContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}
