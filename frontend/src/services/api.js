import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

// Health check
export async function healthCheck() {
  const response = await api.get('/')
  return response.data
}

// ============================================================================
// Codex API
// ============================================================================

export async function getCodexEntries(type = null) {
  const params = type ? { type } : {}
  const response = await api.get('/api/codex/', { params })
  return response.data
}

export async function getCodexEntry(id) {
  const response = await api.get(`/api/codex/${id}`)
  return response.data
}

export async function createCodexEntry(entry, description) {
  const response = await api.post('/api/codex/', { ...entry, description })
  return response.data
}

export async function updateCodexEntry(id, entry, description) {
  const response = await api.put(`/api/codex/${id}`, { ...entry, description })
  return response.data
}

export async function deleteCodexEntry(id) {
  const response = await api.delete(`/api/codex/${id}`)
  return response.data
}

export async function searchCodex(query) {
  const response = await api.get('/api/codex/search', { params: { q: query } })
  return response.data
}

// ============================================================================
// Manuscript API
// ============================================================================

export async function getManuscriptStructure() {
  const response = await api.get('/api/manuscript/')
  return response.data
}

export async function getScene(book, act, chapter, scene) {
  const response = await api.get(`/api/manuscript/${book}/${act}/${chapter}/${scene}`)
  return response.data
}

export async function updateScene(book, act, chapter, scene, data) {
  const response = await api.put(`/api/manuscript/${book}/${act}/${chapter}/${scene}`, data)
  return response.data
}

export async function createScene(book, act, chapter, sceneData) {
  const response = await api.post(`/api/manuscript/${book}/${act}/${chapter}/scenes`, sceneData)
  return response.data
}

// ============================================================================
// AI API
// ============================================================================

export async function sendChat(message, contextEntries = [], sceneId = null) {
  const response = await api.post('/api/ai/chat', {
    message,
    context_entries: contextEntries,
    scene_id: sceneId,
  })
  return response.data
}

export default api
