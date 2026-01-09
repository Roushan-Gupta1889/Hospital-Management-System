<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold mb-0">
        <i class="bi bi-speedometer2 me-2"></i>Dashboard
      </h2>
      <span class="text-muted">Welcome back, {{ user?.full_name }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-muted">Loading dashboard data...</p>
    </div>

    <!-- Admin Dashboard -->
    <div v-else-if="user?.role === 'admin'" class="row">
      <div class="col-md-3 mb-4">
        <div class="card stat-card stat-card-primary h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <p class="text-muted mb-1 stat-label">Total Doctors</p>
                <h2 class="fw-bold mb-0">{{ stats.total_doctors || 0 }}</h2>
              </div>
              <div class="stat-icon bg-primary">
                <i class="bi bi-person-badge"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-4">
        <div class="card stat-card stat-card-success h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <p class="text-muted mb-1 stat-label">Total Patients</p>
                <h2 class="fw-bold mb-0">{{ stats.total_patients || 0 }}</h2>
              </div>
              <div class="stat-icon bg-success">
                <i class="bi bi-people"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-4">
        <div class="card stat-card stat-card-info h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <p class="text-muted mb-1 stat-label">Total Appointments</p>
                <h2 class="fw-bold mb-0">{{ stats.total_appointments || 0 }}</h2>
              </div>
              <div class="stat-icon bg-info">
                <i class="bi bi-calendar-check"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-4">
        <div class="card stat-card stat-card-warning h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <p class="text-muted mb-1 stat-label">Pending</p>
                <h2 class="fw-bold mb-0">{{ stats.pending_appointments || 0 }}</h2>
              </div>
              <div class="stat-icon bg-warning">
                <i class="bi bi-clock-history"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Doctor Dashboard -->
    <div v-if="user?.role === 'doctor'" class="row">
      <div class="col-md-4 mb-3">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <h5 class="card-title">Total Patients</h5>
            <h2>{{ doctorStats.total_patients }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card bg-success text-white">
          <div class="card-body">
            <h5 class="card-title">Total Appointments</h5>
            <h2>{{ doctorStats.total_appointments }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card bg-info text-white">
          <div class="card-body">
            <h5 class="card-title">Completed</h5>
            <h2>{{ doctorStats.completed_appointments }}</h2>
          </div>
        </div>
      </div>

      <div class="col-12">
        <h4 class="mt-3">Today's Appointments</h4>
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Time</th>
                <th>Patient</th>
                <th>Reason</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in doctorStats.today_appointments" :key="app.id">
                <td>{{ app.appointment_time }}</td>
                <td>{{ app.patient_name }}</td>
                <td>{{ app.reason }}</td>
                <td>
                  <span class="badge" :class="{
                    'bg-success': app.status === 'completed',
                    'bg-warning': app.status === 'booked',
                    'bg-danger': app.status === 'cancelled'
                  }">{{ app.status }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Patient Dashboard -->
    <div v-if="user?.role === 'patient'">
      <h4>Available Departments</h4>
      <div class="row mb-4">
        <div class="col-md-4 mb-3" v-for="dept in departments" :key="dept.id">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">{{ dept.name }}</h5>
              <p class="card-text">{{ dept.description }}</p>
              <p class="text-muted">{{ dept.doctors_count }} doctors available</p>
            </div>
          </div>
        </div>
      </div>

      <h4>Upcoming Appointments</h4>
      <div class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Doctor</th>
              <th>Specialization</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in upcomingAppointments" :key="app.id">
              <td>{{ app.appointment_date }}</td>
              <td>{{ app.appointment_time }}</td>
              <td>{{ app.doctor_name }}</td>
              <td>{{ app.doctor_specialization }}</td>
              <td>
                <span class="badge bg-warning">{{ app.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Dashboard',
  setup() {
    const user = ref(JSON.parse(localStorage.getItem('user')))
    const stats = ref({})
    const doctorStats = ref({})
    const departments = ref([])
    const upcomingAppointments = ref([])
    const loading = ref(true)

    let no

    const loadAdminDashboard = async () => {
      try {
        const response = await axios.get('/api/admin/dashboard')
        stats.value = response.data
      } catch (error) {
        console.error('Error loading admin dashboard:', error)
      } finally {
        loading.value = false
      }
    }

    const loadDoctorDashboard = async () => {
      try {
        const response = await axios.get('/api/doctor/dashboard')
        doctorStats.value = response.data
      } catch (error) {
        console.error('Error loading doctor dashboard:', error)
      } finally {
        loading.value = false
      }
    }

    const loadPatientDashboard = async () => {
      try {
        const response = await axios.get('/api/patient/dashboard')
        departments.value = response.data.departments
        upcomingAppointments.value = response.data.upcoming_appointments
      } catch (error) {
        console.error('Error loading patient dashboard:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      if (user.value?.role === 'admin') {
        loadAdminDashboard()
      } else if (user.value?.role === 'doctor') {
        loadDoctorDashboard()
      } else if (user.value?.role === 'patient') {
        loadPatientDashboard()
      }
    })

    return {
      user,
      stats,
      doctorStats,
      departments,
      upcomingAppointments,
      loading
    }
  }
}
</script>

<style scoped>
.stat-card {
  border-radius: 12px;
  border: none;
  overflow: hidden;
}

.stat-card .card-body {
  padding: 1.5rem;
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  opacity: 0.9;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}
</style>
