<!-- src/App.vue -->
<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggle from './components/ThemeToggle.vue'

const router = useRouter()

onMounted(() => {
  console.log('Vue app started')
  console.log('Current route:', router.currentRoute.value.path)
})
</script>

<template>
  <div>
    <header class="section"
      style="padding:.75rem 0;border-bottom:1px solid color-mix(in oklab, var(--fg) 10%, transparent);position:sticky;top:0;background:var(--bg);z-index:50;">
      <div class="container" style="display:flex;align-items:center;gap:.75rem;margin:0 auto;max-width:1300px;">
        <RouterLink to="/" aria-label="Plant'X Home">
          <img src="@/assets/logo.svg" alt="Plant'X Logo" />
        </RouterLink>
        <RouterLink to="/" style="font-weight:800;">Plant'X</RouterLink>

        <nav style="margin-left:auto;display:flex;gap:.99rem;font-size:larger;">
          <RouterLink to="/" @click="() => console.log('Clicked Home')">Home</RouterLink>
          <RouterLink to="/garden" @click="() => console.log('Clicked Garden')">Garden</RouterLink>
          <RouterLink to="/urbanwild" @click="() => console.log('Clicked UrbanWild')">Urban & Wild</RouterLink>
          <RouterLink to="/community" @click="() => console.log('Clicked Community')">Community</RouterLink>
        </nav>

        <ThemeToggle />
      </div>
    </header>

    <main class="container" style="padding:1.25rem 1rem;">
      <RouterView v-slot="{ Component, route }">
        <KeepAlive>
          <component v-if="route.meta?.keepAlive" :is="Component" />
        </KeepAlive>

        <Transition name="page" mode="out-in">
          <div v-if="!route.meta?.keepAlive" class="route-shell" :key="route.fullPath">
            <component :is="Component" />
          </div>
        </Transition>
      </RouterView>
    </main>

    <footer class="section"
      style="border-top:1px solid color-mix(in oklab, var(--fg) 10%, transparent);color:var(--muted);">
      <div class="container">© {{ new Date().getFullYear() }} Plant'X</div>
    </footer>
  </div>
</template>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.route-shell {
  display: block;
}

a.router-link-active {
  text-decoration: underline;
}
</style>
