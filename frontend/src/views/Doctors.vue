<template>
  <div class="container mt-4">
    <h2 class="mb-4">Doctors</h2>

    <div class="row mb-3">
      <div class="col-md-6">
        <input
          type="text"
          class="form-control"
          placeholder="Search by name or specialization..."
          v-model="searchQuery"
          @input="searchDoctors"
        >
      </div>
      <div class="col-md-6 text-end" v-if="user?.role === 'admin'">
        <button class="btn btn-primary" @click="showAddDoctorModal">Add Doctor</button>
      </div>
    </div>

    <div class="row">
      <div class="col-md-4 mb-3" v-for="doctor in doctors" :key="doctor.id">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">{{ doctor.full_name }}</h5>
            <p class="card-text">
              <strong>Specialization:</strong> {{ doctor.specialization }}<br>
              <strong>Department:</strong> {{ doctor.department_name }}<br>
              <strong>Experience:</strong> {{ doctor.experience_years }} years<br>
              <strong>Consultation Fee:</strong>  ₹ {{ doctor.consultation_fee }}<br>
              <span class="badge" :class="doctor.is_active ? 'bg-success' : 'bg-danger'">
                {{ doctor.is_active ? 'Active' : 'Inactive' }}
              </span>
            </p>
            <div v-if="user?.role === 'patient'">
              <button class="btn btn-sm btn-primary" @click="bookAppointment(doctor)">
                Book Appointment
              </button>
            </div>
            <div v-if="user?.role === 'admin'">
              <button class="btn btn-sm btn-warning me-2" @click="editDoctor(doctor)">Edit</button>
              <button class="btn btn-sm btn-danger" @click="deactivateDoctor(doctor.id)" v-if="doctor.is_active">
                Deactivate
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Doctor Modal (Admin Only) -->
    <div class="modal fade" id="doctorModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editMode ? 'Edit Doctor' : 'Add Doctor' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveDoctor">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input type="text" class="form-control" v-model="doctorForm.full_name" required>
              </div>
              <div class="mb-3" v-if="!editMode">
                <label class="form-label">Username</label>
                <input type="text" class="form-control" v-model="doctorForm.username" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" v-model="doctorForm.email" required>
              </div>
              <div class="mb-3" v-if="!editMode">
                <label class="form-label">Password</label>
                <input type="password" class="form-control" v-model="doctorForm.password" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input type="tel" class="form-control" v-model="doctorForm.phone">
              </div>
              <div class="mb-3">
                <label class="form-label">Specialization</label>
                <input type="text" class="form-control" v-model="doctorForm.specialization" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Qualification</label>
                <input type="text" class="form-control" v-model="doctorForm.qualification">
              </div>
              <div class="mb-3">
                <label class="form-label">Experience (years)</label>
                <input type="number" class="form-control" v-model="doctorForm.experience_years">
              </div>
              <div class="mb-3">
                <label class="form-label">Consultation Fee</label>
                <input type="number" class="form-control" v-model="doctorForm.consultation_fee">
              </div>
              <div v-if="error" class="alert alert-danger">{{ error }}</div>
              <button type="submit" class="btn btn-primary">Save</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Modal } from 'bootstrap'

export default {
  name: 'Doctors',
  setup() {
    const router = useRouter()
    const user = ref(JSON.parse(localStorage.getItem('user')))
    const doctors = ref([])
    const searchQuery = ref('')
    const editMode = ref(false)
    const error = ref('')
    let modal = null

    const doctorForm = ref({
      full_name: '',
      username: '',
      email: '',
      password: '',
      phone: '',
      specialization: '',
      qualification: '',
      experience_years: '',
      consultation_fee: ''
    })

    const loadDoctors = async () => {
      try {
        const endpoint = user.value.role === 'admin' ? '/api/admin/doctors' : '/api/patient/doctors'
        const response = await axios.get(endpoint, {
          params: { search: searchQuery.value }
        })
        doctors.value = response.data
      } catch (error) {
        console.error('Error loading doctors:', error)
      }
    }

    const searchDoctors = () => {
      loadDoctors()
    }

    const showAddDoctorModal = () => {
      editMode.value = false
      doctorForm.value = {
        full_name: '',
        username: '',
        email: '',
        password: '',
        phone: '',
        specialization: '',
        qualification: '',
        experience_years: '',
        consultation_fee: ''
      }
      modal = new Modal(document.getElementById('doctorModal'))
      modal.show()
    }

    const editDoctor = async (doctor) => {
      editMode.value = true
      doctorForm.value = { ...doctor }
      modal = new Modal(document.getElementById('doctorModal'))
      modal.show()
    }

    const saveDoctor = async () => {
      error.value = ''
      try {
        if (editMode.value) {
          await axios.put(`/api/admin/doctors/${doctorForm.value.id}`, doctorForm.value)
        } else {
          await axios.post('/api/admin/doctors', doctorForm.value)
        }
        modal.hide()
        loadDoctors()
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to save doctor'
      }
    }

    const deactivateDoctor = async (doctorId) => {
      if (confirm('Are you sure you want to deactivate this doctor?')) {
        try {
          await axios.delete(`/api/admin/doctors/${doctorId}`)
          loadDoctors()
        } catch (error) {
          console.error('Error deactivating doctor:', error)
        }
      }
    }

    const bookAppointment = (doctor) => {
      router.push({ name: 'Appointments', query: { doctorId: doctor.id } })
    }

    onMounted(() => {
      loadDoctors()
    })

    return {
      user,
      doctors,
      searchQuery,
      doctorForm,
      editMode,
      error,
      searchDoctors,
      showAddDoctorModal,
      editDoctor,
      saveDoctor,
      deactivateDoctor,
      bookAppointment
    }
  }
}
</script>
