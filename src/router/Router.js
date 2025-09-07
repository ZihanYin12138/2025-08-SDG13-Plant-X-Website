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
    path: '/learnmore',
    name: 'LearnMore',
    component: () => import('../views/LearnMore.vue'),
    meta: { title: "Learn More · Plant'X" }
  },
  {
    path: '/lmone',
    name: 'LmOne',
    component: () => import('../views/LmOne.vue'),
    meta: { title: "Lm One · Plant'X" }
  },
  {
    path: '/lmtwo',
    name: 'LmTwo',
    component: () => import('../views/LmTwo.vue'),
    meta: { title: "Lm Two · Plant'X" }
  },
  {
    path: '/lmthree',
    name: 'LmThree',
    component: () => import('../views/LmThree.vue'),
    meta: { title: "Lm Three · Plant'X" }
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
    component: () => import('@/views/PlantDetail.vue'),
    props: true, 
    meta: { title: "Plant Detail · Plant'X" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { left: 0, top: 0 }
    }
  }
})

router.afterEach((to)=>{ 
  document.title = to.meta?.title || "Plant'X" 
})

export default router
