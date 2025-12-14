const API_BASE = '/api'

export const api = {
  // Queue
  async addToQueue(urls) {
    const res = await fetch(`${API_BASE}/queue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls })
    })
    return res.json()
  },

  async getQueue() {
    const res = await fetch(`${API_BASE}/queue`)
    return res.json()
  },

  async removeFromQueue(id) {
    const res = await fetch(`${API_BASE}/queue/${id}`, { method: 'DELETE' })
    return res.json()
  },

  async retryDownload(id) {
    const res = await fetch(`${API_BASE}/queue/${id}/retry`, { method: 'POST' })
    return res.json()
  },

  // History
  async getHistory() {
    const res = await fetch(`${API_BASE}/history`)
    return res.json()
  },

  async clearHistory() {
    const res = await fetch(`${API_BASE}/history`, { method: 'DELETE' })
    return res.json()
  },

  // Settings
  async getSettings() {
    const res = await fetch(`${API_BASE}/settings`)
    return res.json()
  },

  async updateSettings(settings) {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    })
    return res.json()
  },

  // Download Control
  async startDownload() {
    const res = await fetch(`${API_BASE}/download/start`, { method: 'POST' })
    return res.json()
  },

  async stopDownload() {
    const res = await fetch(`${API_BASE}/download/stop`, { method: 'POST' })
    return res.json()
  },

  async getDownloadStatus() {
    const res = await fetch(`${API_BASE}/download/status`)
    return res.json()
  }
}
