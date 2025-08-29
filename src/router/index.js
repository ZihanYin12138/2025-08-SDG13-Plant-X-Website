import { createRouter, createWebHistory } from 'vue-router'


const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/garden',
    name: 'Garden',
    component: () => import('../views/Garden.vue')
  },
  {
    path: '/urbanwild',
    name: 'UrbanWild',
    component: () => import('../views/UrbanWild.vue'),
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('../views/Community.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
})

//router.afterEach((to)=>{ document.title = to.meta?.title || "Plant'X" })

export default router
