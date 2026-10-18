/**
 * KrushiSetu API Client Wrapper
 * Handles JWT token injection, unified error management, and session state.
 */

const API = {
  BASE_URL: '',

  getToken() {
    return localStorage.getItem('krushisetu_token');
  },

  setToken(token) {
    if (token) {
      localStorage.setItem('krushisetu_token', token);
    } else {
      localStorage.removeItem('krushisetu_token');
    }
  },

  getHeaders(includeAuth = true, isJson = true) {
    const headers = {};
    if (isJson) {
      headers['Content-Type'] = 'application/json';
    }
    if (includeAuth) {
      const token = this.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return headers;
  },

  async request(endpoint, options = {}) {
    const url = `${this.BASE_URL}${endpoint}`;
    const includeAuth = options.includeAuth !== false;
    const isJson = options.isJson !== false;

    const config = {
      method: options.method || 'GET',
      headers: this.getHeaders(includeAuth, isJson),
      ...options
    };

    if (options.body && isJson && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401 && !url.includes('/login') && !url.includes('/register')) {
          this.setToken(null);
          localStorage.removeItem('krushisetu_user');
          if (!window.location.pathname.includes('login.html')) {
            window.location.href = 'login.html?expired=1';
          }
        }
        throw new Error(data.error || data.message || `Request failed with status ${response.status}`);
      }

      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err.message);
      throw err;
    }
  },

  // Auth APIs
  register(payload) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: payload,
      includeAuth: false
    });
  },

  login(payload) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: payload,
      includeAuth: false
    });
  },

  getProfile() {
    return this.request('/api/auth/me');
  },

  updateProfile(payload) {
    return this.request('/api/auth/profile', {
      method: 'PUT',
      body: payload
    });
  },

  logout() {
    this.setToken(null);
    localStorage.removeItem('krushisetu_user');
    window.location.href = 'login.html';
  }
};
