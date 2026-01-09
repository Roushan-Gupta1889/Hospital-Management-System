import { createApp } from 'vue'
import axios from 'axios'
import App from './App.vue'
import router from './router.js'

// Configure axios defaults
// Use Render backend URL in production, localhost in development
const API_URL = import.meta.env.VITE_API_URL || 'https://hospital-management-system-ye7s.onrender.com'
axios.defaults.baseURL = API_URL
axios.defaults.withCredentials = true
axios.defaults.headers.common['Content-Type'] = 'application/json'


// Add axios response interceptor for error handling
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('user')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)
app.use(router)
app.mount('#app')
