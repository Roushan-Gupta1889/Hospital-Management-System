import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'
import Patients from './views/Patients.vue'
import Doctors from './views/Doctors.vue'
import Appointments from './views/Appointments.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/patients',
    name: 'Patients',
    component: Patients,
    meta: { requiresAuth: true, role: ['admin'] }
  },
  {
    path: '/doctors',
    name: 'Doctors',
    component: Doctors,
    meta: { requiresAuth: true, role: ['admin', 'patient'] }
  },
  {
    path: '/appointments',
    name: 'Appointments',
    component: Appointments,
    meta: { requiresAuth: true, role: ['admin', 'doctor', 'patient'] }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')

  if (to.meta.requiresAuth && !user) {
    next('/login')
  } else if (to.meta.role && !to.meta.role.includes(user?.role)) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
