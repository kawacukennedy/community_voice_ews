const MapManager = (() => {
  let map = null;
  let markerCluster = null;
  let alertLayer = null;
  let userMarker = null;
  let markers = {};
  let currentFilter = 'all';

  const MARKER_COLORS = {
    flood: '#007AFF',
    drought: '#FF6B00',
    pest: '#AF52DE',
    disease: '#FF3B30',
    fire: '#FF4500',
    conflict: '#FFD60A',
    health: '#34C759',
    other: '#8E8E93',
  };

  const MARKER_ICONS = {
    flood: '🌊',
    drought: '☀️',
    pest: '🐛',
    disease: '🤒',
    fire: '🔥',
    conflict: '⚔️',
    health: '🏥',
    other: '📌',
  };

  function createCustomIcon(type, severity) {
    const color = MARKER_COLORS[type] || MARKER_COLORS.other;
    const icon = MARKER_ICONS[type] || MARKER_ICONS.other;
    const size = severity === 'critical' ? 40 : severity === 'high' ? 36 : 32;

    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${size/2}" cy="${size/2}" r="${size/2 - 1}" fill="${color}" opacity="0.9" stroke="white" stroke-width="2"/>
      <text x="${size/2}" y="${size/2 + 1}" text-anchor="middle" dominant-baseline="central" font-size="${size/2 - 2}">${icon}</text>
    </svg>`;

    return L.divIcon({
      html: svg,
      className: '',
      iconSize: [size, size],
      iconAnchor: [size/2, size/2],
      popupAnchor: [0, -size/2],
    });
  }

  function init(containerId) {
    map = L.map(containerId, {
      center: [1.0, 36.0],
      zoom: 5,
      zoomControl: false,
      attributionControl: false,
    });

    L.control.zoom({ position: 'topright' }).addTo(map);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 18,
      minZoom: 3,
    }).addTo(map);

    L.control.attribution({
      position: 'bottomleft',
      prefix: false,
    }).addTo(map);

    markerCluster = L.markerClusterGroup({
      chunkedLoading: true,
      maxClusterRadius: 50,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      disableClusteringAtZoom: 14,
    });
    map.addLayer(markerCluster);

    alertLayer = L.layerGroup().addTo(map);

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const { latitude, longitude } = pos.coords;
          map.setView([latitude, longitude], 8);
          userMarker = L.circleMarker([latitude, longitude], {
            radius: 8,
            color: '#007AFF',
            fillColor: '#007AFF',
            fillOpacity: 0.3,
            weight: 2,
            opacity: 0.6,
          }).addTo(map);
          userMarker.bindPopup('Your location');
        },
        () => {},
        { enableHighAccuracy: false, timeout: 10000 }
      );
    }

    return map;
  }

  function addReportMarker(report) {
    const lat = report.latitude;
    const lng = report.longitude;
    if (!lat || !lng) return null;

    const key = report.id;
    if (markers[key]) {
      markerCluster.removeLayer(markers[key]);
    }

    const type = report.report_type || 'other';
    const severity = report.severity || 'moderate';
    const icon = createCustomIcon(type, severity);

    const marker = L.marker([lat, lng], { icon });

    const time = report.submitted_at ? new Date(report.submitted_at).toLocaleString() : 'Just now';
    const typeIcon = MARKER_ICONS[type] || '📌';
    const severityLabel = severity.charAt(0).toUpperCase() + severity.slice(1);

    marker.bindPopup(`
      <div style="font-family:-apple-system,sans-serif;min-width:200px">
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
          <span style="font-size:18px">${typeIcon}</span>
          <span style="font-weight:600;font-size:14px;text-transform:capitalize">${type}</span>
          <span style="margin-left:auto;font-size:11px;color:#8E8E93">${severityLabel}</span>
        </div>
        <p style="font-size:13px;color:#3A3A3C;margin:0 0 6px;line-height:1.4">${report.message || 'No details'}</p>
        <div style="font-size:11px;color:#8E8E93;display:flex;justify-content:space-between">
          <span>${time}</span>
          <span>${report.location_name || ''}</span>
        </div>
      </div>
    `);

    markerCluster.addLayer(marker);
    markers[key] = marker;

    if (currentFilter !== 'all' && type !== currentFilter) {
      marker.setOpacity(0.3);
    }

    return marker;
  }

  function addAlertMarker(alert) {
    const lat = alert.latitude;
    const lng = alert.longitude;
    if (!lat || !lng) return;

    const color = '#FF3B30';
    const radius = alert.severity === 'critical' ? 20 : alert.severity === 'high' ? 15 : 10;

    const circle = L.circleMarker([lat, lng], {
      radius,
      color: color,
      fillColor: color,
      fillOpacity: 0.15,
      weight: 2,
      opacity: 0.6,
    });

    circle.bindPopup(`
      <div style="font-family:-apple-system,sans-serif;min-width:200px">
        <div style="color:#FF3B30;font-weight:600;font-size:14px;margin-bottom:4px">🚨 ${alert.title}</div>
        <p style="font-size:13px;color:#3A3A3C;margin:0 0 4px">${alert.message}</p>
        <div style="font-size:11px;color:#8E8E93">${alert.region || ''}</div>
      </div>
    `);

    alertLayer.addLayer(circle);
  }

  function clearReports() {
    markerCluster.clearLayers();
    markers = {};
  }

  function clearAlerts() {
    alertLayer.clearLayers();
  }

  function setFilter(type) {
    currentFilter = type;
    Object.entries(markers).forEach(([id, marker]) => {
      const report = window.appState?.reports?.find(r => r.id === id);
      if (report) {
        const opacity = type === 'all' || report.report_type === type ? 1 : 0.3;
        marker.setOpacity(opacity);
        if (opacity === 1 && !markerCluster.hasLayer(marker)) {
          markerCluster.addLayer(marker);
        }
      }
    });
  }

  function flyTo(lat, lng, zoom = 10) {
    map.flyTo([lat, lng], zoom, { duration: 1 });
  }

  function getMap() {
    return map;
  }

  return {
    init,
    addReportMarker,
    addAlertMarker,
    clearReports,
    clearAlerts,
    setFilter,
    flyTo,
    getMap,
  };
})();
