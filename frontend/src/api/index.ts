/** Axios HTTP 客户端：统一拦截器处理业务错误 + Token 自动附带 */
import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
const timeout = Number(import.meta.env.VITE_API_TIMEOUT) || 15000

const instance = axios.create({
  baseURL,
  timeout,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json;charset=UTF-8' },
})

// ==== Token 请求拦截器 ====
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('campus_forum_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

instance.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data?.code !== 0) {
      const err: any = new Error(data?.message || '业务错误')
      err.code = data?.code
      err.data = data?.data
      err.response = response
      return Promise.reject(err)
    }
    return data
  },
  (error) => {
    if (error.response?.data?.code !== undefined) {
      const err: any = new Error(error.response.data.message || '业务错误')
      err.code = error.response.data.code
      err.data = error.response.data.data
      err.response = error.response
      return Promise.reject(err)
    }
    return Promise.reject(error)
  }
)

export default instance
