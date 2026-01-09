<template>
  <nav class="navbar navbar-expand-lg navbar-dark custom-navbar">
    <div class="container-fluid px-4">
      <router-link class="navbar-brand fw-bold d-flex align-items-center" to="/dashboard">
        <i class="bi bi-hospital me-2"></i>
        <span class="brand-text">Hospital Management</span>
      </router-link>
      <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto ms-lg-4">
          <li class="nav-item">
            <router-link class="nav-link" to="/dashboard">
              <i class="bi bi-speedometer2 me-1"></i>Dashboard
            </router-link>
          </li>

          <!-- Admin Navigation -->
          <template v-if="user && user.role === 'admin'">
            <li class="nav-item">
              <router-link class="nav-link" to="/patients">
                <i class="bi bi-people me-1"></i>Patients
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/doctors">
                <i class="bi bi-person-badge me-1"></i>Doctors
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/appointments">
                <i class="bi bi-calendar-check me-1"></i>Appointments
              </router-link>
            </li>
          </template>

          <!-- Doctor Navigation -->
          <template v-if="user && user.role === 'doctor'">
            <li class="nav-item">
              <router-link class="nav-link" to="/appointments">
                <i class="bi bi-calendar-check me-1"></i>My Appointments
              </router-link>
            </li>
          </template>

          <!-- Patient Navigation -->
          <template v-if="user && user.role === 'patient'">
            <li class="nav-item">
              <router-link class="nav-link" to="/doctors">
                <i class="bi bi-search me-1"></i>Find Doctors
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/appointments">
                <i class="bi bi-calendar-check me-1"></i>My Appointments
              </router-link>
            </li>
          </template>
        </ul>
        <div class="d-flex align-items-center gap-3">
          <!-- User Info -->
          <div class="user-info d-none d-lg-flex align-items-center text-white">
            <i class="bi bi-person-circle fs-4 me-2"></i>
            <div class="text-start">
              <div class="fw-semibold small">{{ user?.full_name }}</div>
              <small class="text-white-50" style="font-size: 0.75rem;">{{ user?.role }}</small>
            </div>
          </div>

          <!-- Logout Button - Always Visible -->
          <button class="btn btn-outline-light btn-sm logout-btn" @click="logout">
            <i class="bi bi-box-arrow-right me-1"></i>
            <span class="d-none d-md-inline">Logout</span>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'Navbar',
  setup() {
    const router = useRouter()
    const user = ref(null)

    onMounted(() => {
      const userData = localStorage.getItem('user')
      if (userData) {
        user.value = JSON.parse(userData)
      }
    })

    const logout = async () => {
      if (confirm('Are you sure you want to logout?')) {
        try {
          await axios.post('/api/auth/logout')
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          // Clear all local storage
          localStorage.clear()
          // Redirect to login
          router.push('/login')
          // Force page reload to clear any cached data
          setTimeout(() => {
            window.location.reload()
          }, 100)
        }
      }
    }

    return {
      user,
      logout
    }
  }
}
</script>

<style scoped>
.custom-navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
}

.navbar-brand {
  font-size: 1.25rem;
  letter-spacing: -0.5px;
}

.brand-text {
  background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-link {
  font-weight: 500;
  padding: 0.5rem 1rem !important;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.2);
}

.user-info {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.logout-btn {
  border: 2px solid rgba(255, 255, 255, 0.8);
  font-weight: 600;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: white;
  transform: translateY(-2px);
}

.logout-btn:active {
  transform: translateY(0);
}
</style>
