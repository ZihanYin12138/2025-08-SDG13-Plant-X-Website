<script setup>
import ThemeToggle from './components/ThemeToggle.vue'

</script>

<template>
  <header class="section" style="padding: .75rem 0; border-bottom: 1px solid color-mix(in oklab, var(--fg) 10%, transparent); position: sticky; top: 0; background: var(--bg); z-index: 50;">
    <div class="container" style="display:flex; align-items:center; gap:.75rem;">
      <img src="@/assets/logo.svg" />
      <RouterLink to="/" style="font-weight: 800;">Plant'X</RouterLink>
      <nav style="margin-left:auto; display:flex; gap:.75rem;">
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/garden">Garden</RouterLink>
        <RouterLink to="/urbanwild">Urban & Wild</RouterLink>
        <RouterLink to="/community">Community</RouterLink>
      </nav>
      <ThemeToggle />
    </div>
  </header>

  <main class="container" style="padding: 1.25rem 1rem;">
    <RouterView v-slot="{ Component, route }">
    <Transition name="page" :duration="{ enter: 200, leave: 150 }">
      <component :is="Component" :key="route.fullPath" />
    </Transition>
    </RouterView>
  </main>

  <footer class="section" style="border-top: 1px solid color-mix(in oklab, var(--fg) 10%, transparent); color: var(--muted);">
    <div class="container">© {{ new Date().getFullYear() }} Plant'X</div>
  </footer>
</template>
