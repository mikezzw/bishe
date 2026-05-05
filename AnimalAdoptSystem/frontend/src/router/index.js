import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/main/Home.vue')
  },

  {
    path: '/animals',
    name: 'Animals',
    component: () => import('../views/main/Animals.vue')
  },
  {
    path: '/animal/:id',
    name: 'AnimalDetail',
    component: () => import('../views/main/AnimalDetail.vue')
  },
  {
    path: '/adoptions',
    name: 'Adoptions',
    component: () => import('../views/main/Adoptions.vue')
  },
  {
    path: '/adoption/apply/:animalId',
    name: 'AdoptionApply',
    component: () => import('../views/main/AdoptionApply.vue')
  },
  {
    path: '/adoption/my',
    name: 'MyAdoptions',
    component: () => import('../views/main/MyAdoptions.vue')
  },
  {
    path: '/adoption/recommend',
    name: 'SmartRecommend',
    component: () => import('../views/main/SmartRecommend.vue')
  },
  {
    path: '/cloud-pets',
    name: 'MyCloudPets',
    component: () => import('../views/main/MyCloudPets.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/shelters',
    name: 'Shelters',
    component: () => import('../views/main/Shelters.vue')
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('../views/main/Community.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/main/Profile.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/login/Register.vue')
  },
  {
    path: '/password-reset',
    name: 'PasswordReset',
    component: () => import('../views/login/PasswordReset.vue')
  },
  {
    path: '/password-change',
    name: 'PasswordChange',
    component: () => import('../views/login/PasswordChange.vue'),
    meta: { requiresAuth: true }
  },
  // 基地管理相关路由
  {
    path: '/shelter/dashboard',
    name: 'ShelterDashboard',
    component: () => import('../views/shelter/ShelterDashboard.vue'),
    meta: { hideLayout: true }
  },
  {
    path: '/shelter/info',
    name: 'ShelterInfo',
    component: () => import('../views/shelter/ShelterInfo.vue'),
    meta: { hideLayout: true }
  },
  {
    path: '/shelter/animals',
    name: 'ShelterAnimals',
    component: () => import('../views/shelter/ShelterAnimals.vue'),
    meta: { hideLayout: true }
  },
  {
    path: '/shelter/adoptions',
    name: 'ShelterAdoptions',
    component: () => import('../views/shelter/ShelterAdoptions.vue'),
    meta: { hideLayout: true }
  },
  {
    path: '/shelter/activities',
    name: 'ShelterActivities',
    component: () => import('../views/shelter/ShelterActivities.vue'),
    meta: { hideLayout: true }
  },
  {
    path: '/shelter/volunteers',
    name: 'ShelterVolunteers',
    component: () => import('../views/shelter/ShelterVolunteers.vue'),
    meta: { hideLayout: true }
  },
  {
    path: '/shelter/donations',
    name: 'ShelterDonations',
    component: () => import('../views/shelter/ShelterDonations.vue'),
    meta: { hideLayout: true }
  },
  {
    path: '/volunteer/apply',
    name: 'VolunteerApply',
    component: () => import('../views/main/VolunteerApply.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/volunteer/activities',
    name: 'VolunteerActivities',
    component: () => import('../views/main/VolunteerActivities.vue')
  },

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫，检查登录状态
router.beforeEach((to, from, next) => {
  const requiresAuth = ['AdoptionApply', 'MyAdoptions', 'Profile', 'PasswordChange', 'VolunteerApply', 'MyCloudPets']
  const requiresShelter = ['ShelterDashboard', 'ShelterInfo', 'ShelterAnimals', 'ShelterAdoptions', 'ShelterActivities', 'ShelterVolunteers', 'ShelterDonations']
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  
  // 检查需要登录的路由
  if (requiresAuth.includes(to.name) && !token) {
    next('/login')
    return
  }
  
  // 检查需要基地管理员权限的路由
  if (requiresShelter.includes(to.name)) {
    if (!token) {
      next('/login')
      return
    }
    
    if (!user) {
      next('/login')
      return
    }
    
    if (user.user_type !== 'shelter') {
      // 如果不是基地管理员，重定向到首页并显示提示
      next({
        path: '/',
        query: { 
          error: '需要基地管理员权限才能访问此页面' 
        }
      })
      return
    }
    
    next()
    return
  }
  
  next()
})

export default router
