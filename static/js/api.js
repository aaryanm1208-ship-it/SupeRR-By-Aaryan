/**
 * API Data Service for SupeRR Selector.
 * Handles fetching, caching, and error handling for all platform endpoints.
 */

const API = {
  cache: {},

  async fetchJson(endpoint, params = {}) {
    const url = new URL(endpoint, window.location.origin);
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
        url.searchParams.append(key, params[key]);
      }
    });

    const cacheKey = url.toString();
    if (this.cache[cacheKey]) {
      return this.cache[cacheKey];
    }

    try {
      const response = await fetch(url.toString());
      if (!response.ok) {
        throw new Error(`API Error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      this.cache[cacheKey] = data;
      return data;
    } catch (err) {
      console.error(`Failed to load from ${endpoint}:`, err);
      throw err;
    }
  },

  async getSummary() {
    return this.fetchJson('/api/summary');
  },

  async getBatters(params = {}) {
    return this.fetchJson('/api/batters', params);
  },

  async getBowlers(params = {}) {
    return this.fetchJson('/api/bowlers', params);
  },

  async getPlayerDetail(category, playerId) {
    return this.fetchJson(`/api/player/${category}/${playerId}`);
  },

  async getExplanations() {
    return this.fetchJson('/api/explanations');
  },

  async getResearchData() {
    return this.fetchJson('/api/research');
  },

  async getFigures() {
    const res = await this.fetchJson('/api/figures');
    return Array.isArray(res) ? res : (res.figures || []);
  }
};

window.API = API;

