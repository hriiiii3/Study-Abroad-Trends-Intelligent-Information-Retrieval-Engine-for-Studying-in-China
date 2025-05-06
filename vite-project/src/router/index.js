import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/news/:id',
    name: 'NewsDetail',
    component: () => import('../views/NewsDetail.vue')
  },
  {
    path: '/policy/:id',
    name: 'PolicyDetail',
    component: () => import('../views/PolicyDetail.vue')
  },
  {
    path: '/news',
    name: 'NewsList',
    component: () => import('../views/TopicList.vue'),
    props: (route) => ({ 
      type: 'news', 
      topicId: Number(route.query.topic_id || 0) 
    })
  },
  {
    path: '/policy',
    name: 'PolicyList',
    component: () => import('../views/TopicList.vue'),
    props: (route) => ({ 
      type: 'policy', 
      topicId: Number(route.query.topic_id || 0) 
    })
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue'),
    meta: { requiresAdmin: true }
  },

  {
    path: '/visualization/:typeId',
    name: 'VisualizationType',
    component: () => import('../views/VisualizationDetail.vue')
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('../views/Favorites.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/visualization',
    name: 'CategoryList',
    component: () => import('../views/CategoryList.vue')
  },
  {
    path: '/visualizations',
    name: 'VisualizationsList',
    component: () => import('../views/VisualizationsList.vue')
  },
  {
    path: '/visualization-detail/:id',
    name: 'VisualizationDetail',
    component: () => import('../views/VisualizationDetail.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  
  if (to.meta.requiresAuth && !user) {
    next('/login')
  } else if (to.meta.requiresAdmin && (!user || !user.is_admin)) {
    next('/')
  } else {
    next()
  }
})

export default router 