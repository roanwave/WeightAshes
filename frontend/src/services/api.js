import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

export async function healthCheck() {
  const response = await api.get('/')
  return response.data
}

export default api
