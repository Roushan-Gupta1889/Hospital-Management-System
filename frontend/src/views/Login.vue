<template>
  <div class="login-container d-flex align-items-center justify-content-center">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-12 col-sm-10 col-md-8 col-lg-5 col-xl-4">
          <div class="card shadow-lg border-0 login-card">
            <div class="card-body p-4">
              <div class="text-center mb-3">
                <div class="hospital-icon mb-2">
                  <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor" class="bi bi-hospital" viewBox="0 0 16 16">
                    <path d="M8.5 5.034v1.1l.953-.55.5.867L9 7l.953.55-.5.866-.953-.55v1.1h-1v-1.1l-.953.55-.5-.866L7 7l-.953-.55.5-.866.953.55v-1.1h1ZM13.25 9a.25.25 0 0 0-.25.25v.5c0 .138.112.25.25.25h.5a.25.25 0 0 0 .25-.25v-.5a.25.25 0 0 0-.25-.25h-.5ZM13 11.25a.25.25 0 0 1 .25-.25h.5a.25.25 0 0 1 .25.25v.5a.25.25 0 0 1-.25.25h-.5a.25.25 0 0 1-.25-.25v-.5Zm.25 1.75a.25.25 0 0 0-.25.25v.5c0 .138.112.25.25.25h.5a.25.25 0 0 0 .25-.25v-.5a.25.25 0 0 0-.25-.25h-.5Zm-11-4a.25.25 0 0 0-.25.25v.5c0 .138.112.25.25.25h.5A.25.25 0 0 0 3 9.75v-.5A.25.25 0 0 0 2.75 9h-.5Zm0 2a.25.25 0 0 0-.25.25v.5c0 .138.112.25.25.25h.5a.25.25 0 0 0 .25-.25v-.5a.25.25 0 0 0-.25-.25h-.5ZM2 13.25a.25.25 0 0 1 .25-.25h.5a.25.25 0 0 1 .25.25v.5a.25.25 0 0 1-.25.25h-.5a.25.25 0 0 1-.25-.25v-.5Z"/>
                    <path d="M5 1a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1a1 1 0 0 1 1 1v4h3a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1h3V3a1 1 0 0 1 1-1V1Zm2 14h2v-3H7v3Zm3 0h1V3H5v12h1v-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3Zm0-14H6v1h4V1Zm2 7h3v7h-3V8Zm-8 7V8H1v7h3Z"/>
                  </svg>
                </div>
                <h4 class="fw-bold text-primary mb-1">Hospital Management</h4>
                <p class="text-muted small mb-0">Comprehensive Healthcare System</p>
              </div>

              <ul class="nav nav-pills nav-fill mb-3" role="tablist">
                <li class="nav-item" role="presentation">
                  <button class="nav-link active py-2" data-bs-toggle="tab" data-bs-target="#login">
                    <i class="bi bi-box-arrow-in-right me-1"></i> Login
                  </button>
                </li>
                <li class="nav-item" role="presentation">
                  <button class="nav-link py-2" data-bs-toggle="tab" data-bs-target="#register">
                    <i class="bi bi-person-plus me-1"></i> Register
                  </button>
                </li>
              </ul>

              <div class="tab-content">
                <!-- Login Tab -->
                <div class="tab-pane fade show active" id="login">
                  <form @submit.prevent="handleLogin">
                    <div class="mb-2">
                      <label class="form-label fw-semibold small">Username</label>
                      <input
                        type="text"
                        class="form-control"
                        v-model="loginForm.username"
                        placeholder="Enter your username"
                        :disabled="loading"
                        required
                      >
                    </div>
                    <div class="mb-2">
                      <label class="form-label fw-semibold small">Password</label>
                      <input
                        type="password"
                        class="form-control"
                        v-model="loginForm.password"
                        placeholder="Enter your password"
                        :disabled="loading"
                        required
                      >
                    </div>
                    <div v-if="error" class="alert alert-danger alert-dismissible fade show py-2 mb-2" role="alert">
                      <small><i class="bi bi-exclamation-triangle-fill me-2"></i>{{ error }}</small>
                      <button type="button" class="btn-close btn-close-sm" @click="error = ''"></button>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 mb-2" :disabled="loading">
                      <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                      <span v-if="loading">Logging in...</span>
                      <span v-else>Login</span>
                    </button>
                  </form>
                  <div class="alert alert-info border-0 py-2 mb-0">
                    <small><strong>Demo:</strong> Admin: <code>admin / admin123</code></small>
                  </div>
                </div>

                <!-- Register Tab -->
                <div class="tab-pane fade" id="register">
                  <form @submit.prevent="handleRegister">
                    <div class="row">
                      <div class="col-md-6 mb-2">
                        <label class="form-label fw-semibold small">Full Name</label>
                        <input
                          type="text"
                          class="form-control form-control-sm"
                          v-model="registerForm.full_name"
                          placeholder="Full name"
                          :disabled="loading"
                          required
                        >
                      </div>
                      <div class="col-md-6 mb-2">
                        <label class="form-label fw-semibold small">Username</label>
                        <input
                          type="text"
                          class="form-control form-control-sm"
                          v-model="registerForm.username"
                          placeholder="Username"
                          :disabled="loading"
                          required
                        >
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-6 mb-2">
                        <label class="form-label fw-semibold small">Email</label>
                        <input
                          type="email"
                          class="form-control form-control-sm"
                          v-model="registerForm.email"
                          placeholder="email@example.com"
                          :disabled="loading"
                          required
                        >
                      </div>
                      <div class="col-md-6 mb-2">
                        <label class="form-label fw-semibold small">Phone</label>
                        <input
                          type="tel"
                          class="form-control form-control-sm"
                          v-model="registerForm.phone"
                          placeholder="Phone"
                          :disabled="loading"
                          required
                        >
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-6 mb-2">
                        <label class="form-label fw-semibold small">Password</label>
                        <input
                          type="password"
                          class="form-control form-control-sm"
                          v-model="registerForm.password"
                          placeholder="Password"
                          :disabled="loading"
                          required
                        >
                      </div>
                      <div class="col-md-6 mb-2">
                        <label class="form-label fw-semibold small">Gender</label>
                        <select class="form-select form-select-sm" v-model="registerForm.gender" :disabled="loading">
                          <option value="">Select</option>
                          <option value="Male">Male</option>
                          <option value="Female">Female</option>
                          <option value="Other">Other</option>
                        </select>
                      </div>
                    </div>
                    <div v-if="error" class="alert alert-danger alert-dismissible fade show py-2 mb-2" role="alert">
                      <small><i class="bi bi-exclamation-triangle-fill me-2"></i>{{ error }}</small>
                      <button type="button" class="btn-close btn-close-sm" @click="error = ''"></button>
                    </div>
                    <div v-if="success" class="alert alert-success alert-dismissible fade show py-2 mb-2" role="alert">
                      <small><i class="bi bi-check-circle-fill me-2"></i>{{ success }}</small>
                      <button type="button" class="btn-close btn-close-sm" @click="success = ''"></button>
                    </div>
                    <button type="submit" class="btn btn-success w-100" :disabled="loading">
                      <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                      <span v-if="loading">Registering...</span>
                      <span v-else>Register as Patient</span>
                    </button>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const error = ref('')
    const success = ref('')
    const loading = ref(false)

    const loginForm = ref({
      username: '',
      password: ''
    })

    const registerForm = ref({
      username: '',
      email: '',
      password: '',
      full_name: '',
      phone: '',
      gender: ''
    })

    const handleLogin = async () => {
      error.value = ''
      loading.value = true
      try {
        const response = await axios.post('/api/auth/login', loginForm.value)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        router.push('/dashboard')
      } catch (err) {
        error.value = err.response?.data?.error || 'Login failed. Please check your credentials.'
      } finally {
        loading.value = false
      }
    }

    const handleRegister = async () => {
      error.value = ''
      success.value = ''
      loading.value = true
      try {
        await axios.post('/api/auth/register', registerForm.value)
        success.value = 'Registration successful! You can now login.'
        registerForm.value = {
          username: '',
          email: '',
          password: '',
          full_name: '',
          phone: '',
          gender: ''
        }
      } catch (err) {
        error.value = err.response?.data?.error || 'Registration failed. Please try again.'
      } finally {
        loading.value = false
      }
    }

    return {
      loginForm,
      registerForm,
      error,
      success,
      loading,
      handleLogin,
      handleRegister
    }
  }
}
</script>

<style scoped>
.login-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  overflow-y: auto;
  padding: 1rem;
}

@media (min-width: 768px) {
  .login-container {
    padding: 1.5rem;
  }
}

.login-card {
  border-radius: 15px;
  backdrop-filter: blur(10px);
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hospital-icon {
  color: #667eea;
  animation: bounce 1s ease-in-out;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.nav-pills .nav-link {
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-pills .nav-link.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: scale(1.05);
}

.form-control,
.form-select {
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.form-control:focus,
.form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
  transform: translateY(-2px);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(17, 153, 142, 0.4);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Alert animations */
.alert {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Compact form controls */
.form-control-sm,
.form-select-sm {
  font-size: 0.875rem;
  padding: 0.375rem 0.75rem;
}

.form-label {
  margin-bottom: 0.25rem;
}

.btn-close-sm {
  font-size: 0.7rem;
}

/* Responsive adjustments */
@media (max-width: 767px) {
  .row .col-md-6 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
}
</style>
