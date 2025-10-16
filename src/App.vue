<!-- src/App.vue -->
<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggle from './components/ThemeToggle.vue'

const router = useRouter()

const mobileOpen = ref(false)
function toggleMobile() { mobileOpen.value = !mobileOpen.value }
function closeMobile() { mobileOpen.value = false }

onMounted(() => {
  console.log('Vue app started')
  console.log('Current route:', router.currentRoute.value.path)

  const onKey = (e) => { if (e.key === 'Escape') closeMobile() }
  window.addEventListener('keydown', onKey)

  const stop = watch(() => router.currentRoute.value.fullPath, () => closeMobile())

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', onKey)
    stop()
  })
})
</script>

<template>
  <div>
    <!-- Header -->
    <header class="app-header section">
      <div class="container header-inner">
        <RouterLink to="/" aria-label="Plant'X Home" class="brand">
          <img src="@/assets/logo.svg" alt="Plant'X Logo" />
          <span class="brand-text">Plant'X</span>
        </RouterLink>

        <nav class="nav-desktop" aria-label="Primary">
          <RouterLink to="/" class="nav-link">Home</RouterLink>
          <RouterLink to="/garden" class="nav-link">Plant Encyclopedia</RouterLink>
          <RouterLink to="/urbanwild" class="nav-link">Plant Map</RouterLink>
          <RouterLink to="/community" class="nav-link">Community</RouterLink>
        </nav>

        <div class="header-actions">
          <ThemeToggle />

          <button
            class="hamburger"
            @click="toggleMobile"
            :aria-expanded="mobileOpen ? 'true' : 'false'"
            aria-controls="mobile-menu"
            aria-label="Toggle navigation"
          >
            <span class="hamburger-box" :class="{ open: mobileOpen }">
              <span class="hamburger-inner"></span>
            </span>
          </button>
        </div>
      </div>

      <nav
        id="mobile-menu"
        class="nav-mobile"
        v-show="mobileOpen"
        aria-label="Mobile"
      >
        <RouterLink to="/" class="navm-link" @click="closeMobile">Home</RouterLink>
        <RouterLink to="/garden" class="navm-link" @click="closeMobile">Plant Encyclopedia</RouterLink>
        <RouterLink to="/urbanwild" class="navm-link" @click="closeMobile">Plant Map</RouterLink>
        <RouterLink to="/community" class="navm-link" @click="closeMobile">Community</RouterLink>
      </nav>
    </header>

    <!-- Main -->
    <main class="container main-wrap">
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

    <!-- Footer -->
    <footer class="section app-footer">
      <div class="container">© {{ new Date().getFullYear() }} Plant'X</div>
    </footer>
  </div>
</template>

<style scoped>
.app-header{
  position: sticky; top: 0; z-index: 50;
  background: var(--bg);
  padding: calc(.5rem + env(safe-area-inset-top, 0px)) 0 .5rem 0;
  border-bottom: 1px solid color-mix(in oklab, var(--fg) 10%, transparent);
  backdrop-filter: saturate(140%) blur(6px);
  box-shadow: var(--shadow-sm);
}
.header-inner{
  display: flex; align-items: center; gap: .75rem;
  margin: 0 auto; max-width: 1300px;
}
.brand{ display: inline-flex; align-items: center; gap: .5rem; min-height: 44px; margin-right: auto; }
.brand img{ height: 28px; width: auto; }
.brand-text{ font-weight: 800; color: var(--c-text); display: none; }
@media (min-width: 480px){ .brand-text{ display: inline; } }

.nav-desktop{
  margin-left: auto; display: none; gap: 1rem;
  font-size: clamp(0.98rem, 0.9rem + 0.2vw, 1.05rem);
  justify-content: flex-end;
}
.nav-link{
  padding: .55rem .75rem; border-radius: 10px; color: var(--c-text);
}
.nav-link:hover{ background: var(--hover); }
a.router-link-active{ text-decoration: underline; }

.header-actions{ display: flex; align-items: center; gap: .5rem; }

.hamburger{
  display: inline-flex; align-items: center; justify-content: center;
  width: 44px; height: 44px; border-radius: 10px;
  border: 1px solid var(--border-weak); background: var(--card);
}
.hamburger:hover{ background: var(--hover); }
.hamburger:focus-visible{ outline: var(--ring); outline-offset: 2px; }
.hamburger-box{ position: relative; width: 20px; height: 14px; }
.hamburger-inner, .hamburger-inner::before, .hamburger-inner::after{
  content:""; position:absolute; left:0; right:0; height:2px; background:var(--c-text); border-radius:2px;
}
.hamburger-inner{ top:50%; transform:translateY(-50%); }
.hamburger-inner::before{ top:-6px; }
.hamburger-inner::after{ top:6px; }
.hamburger-box.open .hamburger-inner{ background:transparent; }
.hamburger-box.open .hamburger-inner::before{ transform: translateY(6px) rotate(45deg); }
.hamburger-box.open .hamburger-inner::after{ transform: translateY(-6px) rotate(-45deg); }

.nav-mobile{
  display: grid; grid-template-columns: 1fr; gap: .5rem;
  padding: .5rem 1rem 1rem; border-bottom: 1px solid var(--border-weak);
  background: var(--bg);
}
.navm-link{
  padding: .75rem .9rem; border-radius: 12px; background: var(--card);
  color: var(--c-text); border: 1px solid var(--border-weak); min-height: 44px;
}
.navm-link:hover{ background: var(--hover); }

/* ≥768px 显示桌面导航，隐藏汉堡和移动菜单 */
@media (min-width: 768px){
  .nav-desktop{ display: flex; }
  .hamburger{ display: none; }
  .nav-mobile{ display: none !important; }
}

/* ===== Main / Footer / Transition ===== */
.main-wrap{ padding: 1rem 1rem calc(1.25rem + env(safe-area-inset-bottom, 0px)); }
@media (min-width: 768px){ .main-wrap{ padding: 1.25rem 1rem 1.5rem; } }
.route-shell{ display: block; }

.app-footer{
  border-top: 1px solid color-mix(in oklab, var(--fg) 10%, transparent);
  color: var(--muted);
  padding-bottom: calc(1rem + env(safe-area-inset-bottom, 0px));
}

.page-enter-active, .page-leave-active{ transition: opacity .2s ease, transform .2s ease; }
.page-enter-from, .page-leave-to{ opacity:0; transform: translateY(6px); }

@media (prefers-reduced-motion: reduce){
  .page-enter-active, .page-leave-active{ transition: none; }
}
</style>

