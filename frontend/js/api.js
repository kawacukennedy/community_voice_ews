const API = (() => {
  const BASE_URL = (() => {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
    return 'https://community-voice-ews-api.onrender.com';
  })();

  const MAX_RETRIES = 2;
  const RETRY_DELAY = 1000;

  async function request(path, options = {}) {
    const url = `${BASE_URL}${path}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      try {
        const response = await fetch(url, config);
        if (!response.ok) {
          const error = await response.json().catch(() => ({ detail: response.statusText }));
          throw new Error(error.detail || `HTTP ${response.status}`);
        }
        return await response.json();
      } catch (err) {
        if (attempt < MAX_RETRIES && err.name === 'TypeError') {
          await new Promise(r => setTimeout(r, RETRY_DELAY * (attempt + 1)));
          continue;
        }
        throw err;
      }
    }
  }

  return {
    getReports: (filters = {}) => {
      const params = new URLSearchParams();
      if (filters.type) params.set('report_type', filters.type);
      if (filters.severity) params.set('severity', filters.severity);
      if (filters.status) params.set('status', filters.status);
      if (filters.limit) params.set('limit', filters.limit);
      const qs = params.toString();
      return request(`/api/reports${qs ? '?' + qs : ''}`);
    },

    getReport: (id) => request(`/api/reports/${id}`),

    createReport: (data) => request('/api/reports', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

    getAlerts: (filters = {}) => {
      const params = new URLSearchParams();
      if (filters.type) params.set('alert_type', filters.type);
      if (filters.severity) params.set('severity', filters.severity);
      if (filters.status !== undefined) params.set('status', filters.status);
      const qs = params.toString();
      return request(`/api/alerts${qs ? '?' + qs : ''}`);
    },

    createAlert: (data) => request('/api/alerts', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

    getStats: () => request('/api/stats'),

    getCommunities: () => request('/api/communities'),

    createCommunity: (data) => request('/api/communities', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

    classifyMessage: (text) => request(`/api/classify?text=${encodeURIComponent(text)}`),

    sendSMSWebhook: (from, text) => request('/api/webhooks/sms', {
      method: 'POST',
      body: JSON.stringify({ from, text }),
    }),

    syncICPAC: () => request('/api/icpac/sync', { method: 'POST' }),

    healthCheck: () => request('/api/health'),

    getBaseUrl: () => BASE_URL,
  };
})();
