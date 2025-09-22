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
    path: '/disease',
    name: 'DiseaseSearch',
    redirect: { name: 'Garden', hash: '#diseases' },
    meta: { title: "Diseases · Plant'X" }
  },
  { path: '/diseases',     redirect: { name: 'Garden', hash: '#diseases' } },
  { path: '/plants',       redirect: { name: 'Garden', hash: '#plantsearch' } },
  { path: '/plantsearch',  redirect: { name: 'Garden', hash: '#plantsearch' } },
  { path: '/rcmd',         redirect: { name: 'Garden', hash: '#plantrcmd' } },

  {
    path: '/plantrcmd',
    name: 'PlantRcmd',
    component: () => import('../views/PlantRcmd.vue'),
    meta: { title: "Plant Recommendation · Plant'X" }
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
]

const HEADER_OFFSET = 15

function normalizeHash(hash) {
  const h = (hash || '').toLowerCase()
  const map = {
    '#plants': '#plantsearch',
    '#plant': '#plantsearch',
    '#rcmd': '#plantrcmd',
    '#disease': '#diseases'
  }
  return map[h] || h
}

function scrollToHash(hash) {
  const el = document.querySelector(hash)
  if (!el) return false
  const rect = el.getBoundingClientRect()
  const absoluteTop = rect.top + window.scrollY - HEADER_OFFSET
  window.scrollTo({ top: absoluteTop, left: 0, behavior: 'smooth' })
  return true
}

const router = createRouter({
  history: createWebHistory(),
  routes,
  async scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition

    if (to.hash) {
      const targetHash = normalizeHash(to.hash)
      for (let i = 0; i < 20; i++) {
        await new Promise(r => setTimeout(r, 50))
        if (scrollToHash(targetHash)) return false
      }
      return { left: 0, top: 0 }
    }

    return { left: 0, top: 0 }
  }
})

router.afterEach((to) => {
  document.title = (to.meta && to.meta.title) || "Plant'X"
})

export default router
