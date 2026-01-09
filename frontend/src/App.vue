<template>
  <div id="app">
    <Navbar v-if="isLoggedIn" />
    <router-view />
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'

export default {
  name: 'App',
  components: {
    Navbar
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const isLoggedIn = ref(false)

    // Check login status
    const checkLoginStatus = () => {
      const userData = localStorage.getItem('user')
      isLoggedIn.value = userData !== null
    }

    // Check on mount
    checkLoginStatus()

    // Watch route changes to update navbar visibility
    watch(() => route.path, () => {
      checkLoginStatus()
    })

    return {
      isLoggedIn
    }
  }
}
</script>

<style>
* {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body {
  background-color: #f5f7fa;
  color: #2d3748;
}

.container {
  margin-top: 20px;
}

/* Card enhancements */
.card {
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Button enhancements */
.btn {
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

/* Table enhancements */
.table {
  background: white;
}

.table thead th {
  border-bottom: 2px solid #e2e8f0;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  color: #4a5568;
}

/* Form enhancements */
.form-control,
.form-select {
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.form-control:focus,
.form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-label {
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

/* Badge enhancements */
.badge {
  padding: 0.35em 0.75em;
  font-weight: 500;
}

/* Alert enhancements */
.alert {
  border: none;
  border-left: 4px solid;
}

/* Loading spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

/* Smooth transitions */
* {
  transition: background-color 0.2s ease, color 0.2s ease;
}
</style>
