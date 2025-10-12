// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomePage.vue'),
    meta: { title: "Home · Plant'X" }
  },
  {
    path: '/garden',
    name: 'Garden',
    component: () => import('../views/GardenPage.vue'),
    // 关键：给 Garden 打上 keepAlive，返回时保留内部搜索页状态
    meta: { title: "Garden · Plant'X", keepAlive: true }
  },
  {
    path: '/urbanwild',
    name: 'UrbanWild',
    component: () => import('../views/UrbanWild.vue'),
    meta: { title: "Urban Wild · Plant'X" }
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('../views/CommunityPage.vue'),
    meta: { title: "Community · Plant'X" }
  },
  {
    path: '/plants/:id',
    name: 'PlantDetail',
    component: () => import('../views/PlantDetail.vue'),
    props: true,
    meta: { title: "Plant Detail · Plant'X" }
  },
  {
    path: '/disease/:id',
    name: 'DiseaseDetail',
    component: () => import('../views/DiseaseDetail.vue'),
    props: true,
    meta: { title: "Disease Detail · Plant'X" }
  },
  {
    path: '/plantrcmd',
    name: 'PlantRcmd',
    component: () => import('../views/PlantRcmd.vue'),
    meta: { title: "Plant Recommendations · Plant'X" }
  },
  {
  path: '/climate',
  name: 'ClimateImpact',
  component: () => import('../views/ClimateImpact.vue'),
  meta: { title: "Climate Impact · Plant'X" }
  },
  {
  path: '/tp/mapping',
  name: 'TPmapping',
  component: () => import('@/views/TPmapping.vue')
}
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { left: 0, top: 0 }
  }
})

router.afterEach((to) => {
  document.title = (to.meta && to.meta.title) || "Plant'X"
})

export default router
