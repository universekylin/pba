// src/api/axios.js
import axios from 'axios'

// 开发环境一律走同源 '/api'（由 Vite 代理到 3001）；生产再读 VITE_API_BASE
const baseURL = import.meta.env.DEV
  ? '/api'
  : (import.meta.env.VITE_API_BASE || '/api')

// 静态文件基址：你已经在 vite 里把 /static 也代理到 3001，
// 因此前端可以直接用相对路径 '/static/...'
export const fileBase = import.meta.env.VITE_FILE_BASE || ''

const api = axios.create({
  baseURL,
  timeout: 15000,
})

// 可选：启动时打印 baseURL 便于确认
if (typeof window !== 'undefined') {
  console.info('[api] baseURL =', baseURL)
}

api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      alert(data?.error || `Request failed (${status})`)
    } else if (error.request) {
      alert('Network error or server not responding')
    } else {
      alert('Request configuration error')
    }
    return Promise.reject(error)
  }
)

export default api
