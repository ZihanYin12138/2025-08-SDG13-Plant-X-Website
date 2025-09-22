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
    meta: { title: "Garden · Plant'X" }
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
    path: '/allplants',
    name: 'AllPlants',
    component: () => import('../views/AllPlants.vue'),
    meta: { title: "All Plants · Plant'X" }
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
