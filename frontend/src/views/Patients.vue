<template>
  <div class="container mt-4">
    <h2 class="mb-4">Patient Management</h2>

    <div class="row mb-3">
      <div class="col-md-6">
        <input
          type="text"
          class="form-control"
          placeholder="Search patients..."
          v-model="searchQuery"
          @input="searchPatients"
        >
      </div>
    </div>

    <div class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Gender</th>
            <th>Blood Group</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="patient in patients" :key="patient.id">
            <td>{{ patient.id }}</td>
            <td>{{ patient.full_name }}</td>
            <td>{{ patient.email }}</td>
            <td>{{ patient.phone }}</td>
            <td>{{ patient.gender }}</td>
            <td>{{ patient.blood_group }}</td>
            <td>
              <span class="badge" :class="patient.is_active ? 'bg-success' : 'bg-danger'">
                {{ patient.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <button class="btn btn-sm btn-primary me-2" @click="viewPatient(patient)">View</button>
              <button class="btn btn-sm btn-danger" @click="deactivatePatient(patient.id)" v-if="patient.is_active">
                Deactivate
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- View Patient Modal -->
    <div class="modal fade" id="patientModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Patient Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedPatient">
            <p><strong>Name:</strong> {{ selectedPatient.full_name }}</p>
            <p><strong>Email:</strong> {{ selectedPatient.email }}</p>
            <p><strong>Phone:</strong> {{ selectedPatient.phone }}</p>
            <p><strong>Gender:</strong> {{ selectedPatient.gender }}</p>
            <p><strong>Blood Group:</strong> {{ selectedPatient.blood_group }}</p>
            <p><strong>Address:</strong> {{ selectedPatient.address }}</p>
            <p><strong>Emergency Contact:</strong> {{ selectedPatient.emergency_contact }}</p>
            <p><strong>Medical History:</strong> {{ selectedPatient.medical_history }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Modal } from 'bootstrap'

export default {
  name: 'Patients',
  setup() {
    const patients = ref([])
    const searchQuery = ref('')
    const selectedPatient = ref(null)
    let modal = null

    const loadPatients = async () => {
      try {
        const response = await axios.get('/api/admin/patients', {
          params: { search: searchQuery.value }
        })
        patients.value = response.data
      } catch (error) {
        console.error('Error loading patients:', error)
      }
    }

    const searchPatients = () => {
      loadPatients()
    }

    const viewPatient = async (patient) => {
      try {
        const response = await axios.get(`/api/admin/patients/${patient.id}`)
        selectedPatient.value = response.data
        modal = new Modal(document.getElementById('patientModal'))
        modal.show()
      } catch (error) {
        console.error('Error loading patient:', error)
      }
    }

    const deactivatePatient = async (patientId) => {
      if (confirm('Are you sure you want to deactivate this patient?')) {
        try {
          await axios.delete(`/api/admin/patients/${patientId}`)
          loadPatients()
        } catch (error) {
          console.error('Error deactivating patient:', error)
        }
      }
    }

    onMounted(() => {
      loadPatients()
    })

    return {
      patients,
      searchQuery,
      selectedPatient,
      searchPatients,
      viewPatient,
      deactivatePatient
    }
  }
}
</script>
