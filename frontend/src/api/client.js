import axios from 'axios'

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('auth_token')
      window.location.href = '/signin'
    }
    return Promise.reject(error)
  }
)

// API methods
export const apiClient = {
  // Health check
  health: () => api.get('/health'),
  
  // Authentication (TODO: implement backend endpoints)
  auth: {
    signIn: (email, password) =>
      api.post('/auth/signin', { email, password }),
    signUp: (name, email, password) =>
      api.post('/auth/signup', { name, email, password }),
    signOut: () => api.post('/auth/signout'),
  },
  
  // Upload and parse degree evaluation
  uploadEval: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload-eval', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  
  // Submit preferences and get schedule recommendations
  getSchedule: (preferences, evalData) =>
    api.post('/upload-preferences', {
      preferences,
      eval_data: evalData,
    }),
  
  // Search courses
  searchCourses: (params) =>
    api.get('/search-courses', { params }),
  
  // Get professor rating
  getProfessorRating: (name) =>
    api.get(`/professor-rating/${encodeURIComponent(name)}`),
  
  // Schedules (TODO: implement backend endpoints)
  schedules: {
    list: () => api.get('/schedules'),
    get: (id) => api.get(`/schedules/${id}`),
    create: (schedule) => api.post('/schedules', schedule),
    update: (id, schedule) => api.put(`/schedules/${id}`, schedule),
    delete: (id) => api.delete(`/schedules/${id}`),
  },
  
  // Stats
  getStats: () => api.get('/stats'),
}

export default api
