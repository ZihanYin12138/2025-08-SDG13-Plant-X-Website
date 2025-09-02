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
    path: '/plantcard',
    name: 'PlantCard',
    component: () => import('../components/PlantCard.vue'),
    meta: { title: "Plant Card · Plant'X" }
  },
  {
    path: '/learnmore',
    name: 'LearnMore',
    component: () => import('../views/LearnMore.vue'),
    meta: { title: "Learn More · Plant'X" }
  },
  {
    path: '/allplants',
    name: 'AllPlants',
    component: () => import('../views/AllPlants.vue'),
    meta: { title: "All Plants · Plant'X" }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to)=>{ 
  document.title = to.meta?.title || "Plant'X" 
})

export default router
