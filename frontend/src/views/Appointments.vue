<template>
  <div class="container mt-4">
    <h2 class="mb-4">Appointments</h2>

    <!-- Patient: Book Appointment Button -->
    <div v-if="user?.role === 'patient'" class="mb-3">
      <button class="btn btn-primary" @click="showBookingModal">Book New Appointment</button>
      <button class="btn btn-success ms-2" @click="exportTreatments">Export Treatment History</button>
    </div>

    <!-- Filter Options -->
    <div class="row mb-3">
      <div class="col-md-4">
        <select class="form-select" v-model="statusFilter" @change="loadAppointments">
          <option value="">All Statuses</option>
          <option value="booked">Booked</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
    </div>

    <!-- Appointments Table -->
    <div class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th v-if="user?.role !== 'patient'">Patient</th>
            <th v-if="user?.role !== 'doctor'">Doctor</th>
            <th>Date</th>
            <th>Time</th>
            <th>Reason</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="appointment in appointments" :key="appointment.id">
            <td>{{ appointment.id }}</td>
            <td v-if="user?.role !== 'patient'">{{ appointment.patient_name }}</td>
            <td v-if="user?.role !== 'doctor'">{{ appointment.doctor_name }}</td>
            <td>{{ appointment.appointment_date }}</td>
            <td>{{ appointment.appointment_time }}</td>
            <td>{{ appointment.reason }}</td>
            <td>
              <span class="badge" :class="{
                'bg-success': appointment.status === 'completed',
                'bg-warning': appointment.status === 'booked',
                'bg-danger': appointment.status === 'cancelled'
              }">{{ appointment.status }}</span>
            </td>
            <td>
              <button class="btn btn-sm btn-info me-2" @click="viewAppointment(appointment)">View</button>

              <!-- Patient Actions -->
              <template v-if="user?.role === 'patient' && appointment.status === 'booked'">
                <button class="btn btn-sm btn-warning me-2" @click="rescheduleAppointment(appointment)">
                  Reschedule
                </button>
                <button class="btn btn-sm btn-danger" @click="cancelAppointment(appointment.id)">
                  Cancel
                </button>
              </template>

              <!-- Doctor Actions -->
              <template v-if="user?.role === 'doctor' && appointment.status === 'booked'">
                <button class="btn btn-sm btn-success me-2" @click="completeAppointment(appointment)">
                  Complete
                </button>
                <button class="btn btn-sm btn-danger" @click="cancelAppointmentDoctor(appointment.id)">
                  Cancel
                </button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Book Appointment Modal -->
    <div class="modal fade" id="bookingModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ rescheduleMode ? 'Reschedule Appointment' : 'Book Appointment' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitBooking">
              <div class="mb-3" v-if="!rescheduleMode">
                <label class="form-label">Select Doctor</label>
                <select class="form-select" v-model="bookingForm.doctor_id" required>
                  <option value="">Choose a doctor...</option>
                  <option v-for="doctor in availableDoctors" :key="doctor.id" :value="doctor.id">
                    {{ doctor.full_name }} - {{ doctor.specialization }}
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Date</label>
                <input type="date" class="form-control" v-model="bookingForm.appointment_date" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Time</label>
                <input type="time" class="form-control" v-model="bookingForm.appointment_time" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Reason</label>
                <textarea class="form-control" v-model="bookingForm.reason" rows="3"></textarea>
              </div>
              <div v-if="bookingError" class="alert alert-danger">{{ bookingError }}</div>
              <button type="submit" class="btn btn-primary">
                {{ rescheduleMode ? 'Reschedule' : 'Book Appointment' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Complete Appointment Modal (Doctor) -->
    <div class="modal fade" id="completeModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Complete Appointment</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitCompletion">
              <div class="mb-3">
                <label class="form-label">Diagnosis</label>
                <textarea class="form-control" v-model="treatmentForm.diagnosis" rows="3" required></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Prescription</label>
                <textarea class="form-control" v-model="treatmentForm.prescription" rows="3"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Treatment Notes</label>
                <textarea class="form-control" v-model="treatmentForm.treatment_notes" rows="3"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Next Visit Date (Optional)</label>
                <input type="date" class="form-control" v-model="treatmentForm.next_visit_date">
              </div>
              <button type="submit" class="btn btn-success">Complete Appointment</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- View Appointment Modal -->
    <div class="modal fade" id="viewModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Appointment Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedAppointment">
            <p><strong>Patient:</strong> {{ selectedAppointment.patient_name }}</p>
            <p><strong>Doctor:</strong> {{ selectedAppointment.doctor_name }}</p>
            <p><strong>Date:</strong> {{ selectedAppointment.appointment_date }}</p>
            <p><strong>Time:</strong> {{ selectedAppointment.appointment_time }}</p>
            <p><strong>Reason:</strong> {{ selectedAppointment.reason }}</p>
            <p><strong>Status:</strong> {{ selectedAppointment.status }}</p>

            <div v-if="selectedAppointment.treatment">
              <hr>
              <h5>Treatment Details</h5>
              <p><strong>Diagnosis:</strong> {{ selectedAppointment.treatment.diagnosis }}</p>
              <p><strong>Prescription:</strong> {{ selectedAppointment.treatment.prescription }}</p>
              <p><strong>Notes:</strong> {{ selectedAppointment.treatment.treatment_notes }}</p>
              <p><strong>Next Visit:</strong> {{ selectedAppointment.treatment.next_visit_date || 'N/A' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { Modal } from 'bootstrap'

export default {
  name: 'Appointments',
  setup() {
    const route = useRoute()
    const user = ref(JSON.parse(localStorage.getItem('user')))
    const appointments = ref([])
    const availableDoctors = ref([])
    const statusFilter = ref('')
    const bookingError = ref('')
    const rescheduleMode = ref(false)
    const selectedAppointment = ref(null)
    let bookingModal = null
    let completeModal = null
    let viewModal = null

    const bookingForm = ref({
      doctor_id: route.query.doctorId || '',
      appointment_date: '',
      appointment_time: '',
      reason: ''
    })

    const treatmentForm = ref({
      diagnosis: '',
      prescription: '',
      treatment_notes: '',
      next_visit_date: ''
    })

    const loadAppointments = async () => {
      try {
        let endpoint = ''
        if (user.value.role === 'admin') {
          endpoint = '/api/admin/appointments'
        } else if (user.value.role === 'doctor') {
          endpoint = '/api/doctor/appointments'
        } else if (user.value.role === 'patient') {
          endpoint = '/api/patient/appointments'
        }

        const response = await axios.get(endpoint, {
          params: { status: statusFilter.value }
        })
        appointments.value = response.data
      } catch (error) {
        console.error('Error loading appointments:', error)
      }
    }

    const loadDoctors = async () => {
      try {
        const response = await axios.get('/api/patient/doctors')
        availableDoctors.value = response.data
      } catch (error) {
        console.error('Error loading doctors:', error)
      }
    }

    const showBookingModal = () => {
      rescheduleMode.value = false
      bookingForm.value = {
        doctor_id: route.query.doctorId || '',
        appointment_date: '',
        appointment_time: '',
        reason: ''
      }
      bookingModal = new Modal(document.getElementById('bookingModal'))
      bookingModal.show()
    }

    const rescheduleAppointment = (appointment) => {
      rescheduleMode.value = true
      selectedAppointment.value = appointment
      bookingForm.value = {
        doctor_id: appointment.doctor_id,
        appointment_date: appointment.appointment_date,
        appointment_time: appointment.appointment_time,
        reason: appointment.reason
      }
      bookingModal = new Modal(document.getElementById('bookingModal'))
      bookingModal.show()
    }

    const submitBooking = async () => {
      bookingError.value = ''
      try {
        if (rescheduleMode.value) {
          await axios.put(`/api/appointments/${selectedAppointment.value.id}`, bookingForm.value)
        } else {
          await axios.post('/api/appointments', bookingForm.value)
        }
        bookingModal.hide()
        loadAppointments()
      } catch (err) {
        bookingError.value = err.response?.data?.error || 'Failed to book appointment'
      }
    }

    const cancelAppointment = async (appointmentId) => {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
          await axios.delete(`/api/appointments/${appointmentId}`)
          loadAppointments()
        } catch (error) {
          console.error('Error cancelling appointment:', error)
        }
      }
    }

    const completeAppointment = (appointment) => {
      selectedAppointment.value = appointment
      treatmentForm.value = {
        diagnosis: '',
        prescription: '',
        treatment_notes: '',
        next_visit_date: ''
      }
      completeModal = new Modal(document.getElementById('completeModal'))
      completeModal.show()
    }

    const submitCompletion = async () => {
      try {
        await axios.post(`/api/doctor/appointments/${selectedAppointment.value.id}/complete`, treatmentForm.value)
        completeModal.hide()
        loadAppointments()
      } catch (error) {
        console.error('Error completing appointment:', error)
      }
    }

    const cancelAppointmentDoctor = async (appointmentId) => {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
          await axios.post(`/api/doctor/appointments/${appointmentId}/cancel`)
          loadAppointments()
        } catch (error) {
          console.error('Error cancelling appointment:', error)
        }
      }
    }

    const viewAppointment = async (appointment) => {
      try {
        const response = await axios.get(`/api/appointments/${appointment.id}`)
        selectedAppointment.value = response.data
        viewModal = new Modal(document.getElementById('viewModal'))
        viewModal.show()
      } catch (error) {
        console.error('Error loading appointment:', error)
      }
    }

    const exportTreatments = async () => {
      try {
        const response = await axios.post('/api/patient/export-treatments')
        alert('Export started! Task ID: ' + response.data.task_id + '. You will be notified when complete.')
      } catch (error) {
        console.error('Error exporting treatments:', error)
      }
    }

    onMounted(() => {
      loadAppointments()
      if (user.value.role === 'patient') {
        loadDoctors()
      }
    })

    return {
      user,
      appointments,
      availableDoctors,
      statusFilter,
      bookingForm,
      treatmentForm,
      bookingError,
      rescheduleMode,
      selectedAppointment,
      loadAppointments,
      showBookingModal,
      rescheduleAppointment,
      submitBooking,
      cancelAppointment,
      completeAppointment,
      submitCompletion,
      cancelAppointmentDoctor,
      viewAppointment,
      exportTreatments
    }
  }
}
</script>
