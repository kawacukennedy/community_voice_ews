const appState = {
  reports: [],
  alerts: [],
  communities: [],
  stats: null,
  activeTab: 'reports',
  currentFilter: 'all',
  refreshInterval: null,
};

function init() {
  MapManager.init('map');

  setupTabs();
  setupFilters();
  setupReportForm();

  loadData();
  startAutoRefresh();

  if (API.getBaseUrl().includes('localhost')) {
    showNotification('Development Mode', 'Using local backend at ' + API.getBaseUrl(), 'info');
  }
}

function setupTabs() {
  document.querySelectorAll('.sidebar-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.sidebar-tab').forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      appState.activeTab = tab.dataset.tab;
      renderTabContent();
    });
  });
}

function setupFilters() {
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      appState.currentFilter = chip.dataset.filter;
      MapManager.setFilter(appState.currentFilter);
      renderTabContent();
    });
  });
}

function setupReportForm() {
  const msgEl = document.getElementById('reportMessage');
  if (msgEl) {
    msgEl.addEventListener('input', () => {
      const count = msgEl.value.length;
      document.getElementById('charCount').textContent = count;

      if (count > 20) {
        debounce(previewClassification, 500)(msgEl.value);
      } else {
        document.getElementById('reportPreview').style.display = 'none';
      }
    });
  }

  const latEl = document.getElementById('reportLatitude');
  const lngEl = document.getElementById('reportLongitude');
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        latEl.value = pos.coords.latitude.toFixed(4);
        lngEl.value = pos.coords.longitude.toFixed(4);
      },
      () => {},
      { timeout: 5000 }
    );
  }
}

let debounceTimer = {};
function debounce(fn, delay) {
  const key = fn.name || Math.random().toString(36);
  return (...args) => {
    clearTimeout(debounceTimer[key]);
    debounceTimer[key] = setTimeout(() => fn(...args), delay);
  };
}

async function previewClassification(text) {
  try {
    const result = await API.classifyMessage(text);
    const preview = document.getElementById('reportPreview');
    preview.style.display = 'block';
    document.getElementById('previewType').innerHTML = `<strong>Type:</strong> ${result.report_type}`;
    document.getElementById('previewSeverity').innerHTML = `<strong>Severity:</strong> ${result.severity}`;
    document.getElementById('previewConfidence').innerHTML = `<strong>Confidence:</strong> ${(result.confidence * 100).toFixed(0)}%`;
  } catch (e) {
    // silent fail for preview
  }
}

async function loadData() {
  try {
    const [reports, alerts, stats, communities] = await Promise.all([
      API.getReports({ limit: 200 }),
      API.getAlerts({ status: 'active' }),
      API.getStats(),
      API.getCommunities(),
    ]);

    appState.reports = reports;
    appState.alerts = alerts;
    appState.stats = stats;
    appState.communities = communities;

    MapManager.clearReports();
    MapManager.clearAlerts();

    reports.forEach(r => MapManager.addReportMarker(r));
    alerts.forEach(a => MapManager.addAlertMarker(a));

    updateStats();
    renderTabContent();
  } catch (err) {
    console.error('Failed to load data:', err);
    if (!appState.reports.length) {
      document.getElementById('sidebarContent').innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">⚠️</div>
          <div class="empty-state-title">Connection Error</div>
          <div class="empty-state-text">Could not reach the server. Make sure the backend is running at ${API.getBaseUrl()}</div>
          <button class="btn btn-primary" onclick="loadData()" style="margin-top:12px">Retry</button>
        </div>
      `;
    }
  }
}

function updateStats() {
  if (!appState.stats) return;

  document.getElementById('statReports').textContent = appState.stats.total_reports || 0;
  document.getElementById('statAlerts').textContent = appState.stats.active_alerts || 0;
  document.getElementById('statCommunities').textContent = appState.stats.total_communities || 0;

  const criticalCount = appState.stats.reports_by_severity?.critical || 0;
  document.getElementById('statCritical').textContent = criticalCount;
}

function renderTabContent() {
  const container = document.getElementById('sidebarContent');

  switch (appState.activeTab) {
    case 'reports':
      renderReports(container);
      break;
    case 'alerts':
      renderAlerts(container);
      break;
    case 'communities':
      renderCommunities(container);
      break;
  }
}

function renderReports(container) {
  let items = appState.reports;

  if (appState.currentFilter !== 'all') {
    items = items.filter(r => r.report_type === appState.currentFilter);
  }

  if (!items.length) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📋</div>
        <div class="empty-state-title">No Reports Yet</div>
        <div class="empty-state-text">Reports from SMS and web submissions will appear here</div>
      </div>
    `;
    return;
  }

  container.innerHTML = items.map(r => {
    const type = r.report_type || 'other';
    const sev = r.severity || 'moderate';
    const time = r.submitted_at ? timeAgo(r.submitted_at) : '';
    const typeIcon = { flood: '🌊', drought: '☀️', pest: '🐛', disease: '🤒', fire: '🔥', conflict: '⚔️', health: '🏥', other: '📌' } [type] || '📌';

    return `
      <div class="card" onclick="focusReport('${r.id}')">
        <div class="card-header">
          <span class="card-type-badge ${type}">${typeIcon} ${type}</span>
          <span class="severity-indicator">
            <span class="severity-dot ${sev}"></span>
            ${sev.charAt(0).toUpperCase() + sev.slice(1)}
          </span>
        </div>
        <div class="card-title">${r.location_name || 'Unknown Location'}</div>
        <div class="card-message">${r.message || 'No description'}</div>
        <div class="card-meta">
          <span>🕐 ${time}</span>
          ${r.source ? `<span>📡 ${r.source}</span>` : ''}
          ${r.location_name ? `<span>📍 ${r.location_name}</span>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

function renderAlerts(container) {
  const items = appState.alerts;

  if (!items.length) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔔</div>
        <div class="empty-state-title">No Active Alerts</div>
        <div class="empty-state-text">Your region is clear. Alerts will appear here when issued.</div>
      </div>
    `;
    return;
  }

  container.innerHTML = items.map(a => {
    const sev = a.severity || 'moderate';
    const time = a.created_at ? timeAgo(a.created_at) : '';

    return `
      <div class="card" style="border-left:4px solid ${sev === 'critical' ? '#FF3B30' : sev === 'high' ? '#FF6B00' : '#FFD60A'}">
        <div class="card-header">
          <span class="card-type-badge ${a.alert_type || 'other'}">🚨 ${a.alert_type || 'Alert'}</span>
          <span class="severity-indicator">
            <span class="severity-dot ${sev}"></span>
            ${sev.charAt(0).toUpperCase() + sev.slice(1)}
          </span>
        </div>
        <div class="card-title">${a.title}</div>
        <div class="card-message">${a.message}</div>
        <div class="card-meta">
          <span>🕐 ${time}</span>
          ${a.region ? `<span>📍 ${a.region}</span>` : ''}
          ${a.source ? `<span>📡 ${a.source}</span>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

function renderCommunities(container) {
  const items = appState.communities;

  if (!items.length) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🏘️</div>
        <div class="empty-state-title">No Communities Registered</div>
        <div class="empty-state-text">Registered communities will appear here</div>
      </div>
    `;
    return;
  }

  container.innerHTML = items.map(c => `
    <div class="card">
      <div class="card-header">
        <span style="font-weight:600">${c.name}</span>
        <span class="severity-dot ${c.is_active ? 'low' : 'moderate'}" style="width:10px;height:10px;"></span>
      </div>
      <div style="font-size:13px;color:var(--color-text-secondary)">
        ${c.region ? `${c.region}` : ''}${c.country ? `, ${c.country}` : ''}
      </div>
      <div class="card-meta">
        <span>📞 ${c.phone}</span>
        <span>🗣️ ${c.language || 'en'}</span>
      </div>
    </div>
  `).join('');
}

function timeAgo(dateStr) {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = Math.floor((now - date) / 1000);

  if (diff < 60) return 'just now';
  if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
  if (diff < 604800) return Math.floor(diff / 86400) + 'd ago';
  return date.toLocaleDateString();
}

function focusReport(id) {
  const report = appState.reports.find(r => r.id === id);
  if (report && report.latitude && report.longitude) {
    MapManager.flyTo(report.latitude, report.longitude, 12);
  }
}

function startAutoRefresh() {
  if (appState.refreshInterval) clearInterval(appState.refreshInterval);
  appState.refreshInterval = setInterval(loadData, 30000);
}

function locateMe() {
  if (!navigator.geolocation) {
    showNotification('Error', 'Geolocation not supported', 'error');
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      MapManager.flyTo(pos.coords.latitude, pos.coords.longitude, 10);
      showNotification('Location Found', 'Map centered on your location', 'success');
    },
    () => showNotification('Error', 'Could not determine your location', 'error')
  );
}

function openReportModal() {
  document.getElementById('reportModal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
  document.body.style.overflow = '';
}

async function submitReport() {
  const message = document.getElementById('reportMessage').value.trim();
  if (!message) {
    showNotification('Error', 'Please describe what you observed', 'error');
    return;
  }

  const data = {
    message,
    latitude: parseFloat(document.getElementById('reportLatitude').value) || null,
    longitude: parseFloat(document.getElementById('reportLongitude').value) || null,
    location_name: document.getElementById('reportLocation').value.trim() || null,
    phone_number: document.getElementById('reportPhone').value.trim() || null,
    source: 'web',
  };

  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.textContent = 'Submitting...';

  try {
    const result = await API.createReport(data);
    showNotification('Report Submitted', `Classified as ${result.report_type} (${result.severity})`, 'success');
    closeModal('reportModal');
    document.getElementById('reportMessage').value = '';
    document.getElementById('reportLocation').value = '';
    document.getElementById('reportPhone').value = '';
    document.getElementById('reportPreview').style.display = 'none';
    document.getElementById('charCount').textContent = '0';
    await loadData();
  } catch (err) {
    showNotification('Error', err.message || 'Failed to submit report', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Submit Report';
  }
}

function showNotification(title, message, type = 'info') {
  const container = document.getElementById('notifications');
  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };

  const el = document.createElement('div');
  el.className = `notification ${type}`;
  el.innerHTML = `
    <span class="notification-icon">${icons[type] || 'ℹ️'}</span>
    <div class="notification-content">
      <div class="notification-title">${title}</div>
      <div class="notification-message">${message}</div>
    </div>
    <button class="notification-close" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(el);
  setTimeout(() => {
    if (el.parentElement) {
      el.style.opacity = '0';
      el.style.transform = 'translateX(100%)';
      setTimeout(() => el.remove(), 300);
    }
  }, 5000);
}

document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    closeModal(e.target.id);
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => closeModal(m.id));
  }
});

document.addEventListener('DOMContentLoaded', init);
