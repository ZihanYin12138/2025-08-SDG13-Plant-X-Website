<!-- src/App.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggle from './components/ThemeToggle.vue'

const router = useRouter()


const PASSWORD = 'GROUP21password!'
const pwd = ref('')
const err = ref('')
const unlocked = ref(false)

function checkUnlocked() {
  unlocked.value = sessionStorage.getItem('gate:ok') === '1'
}
function submit() {
  err.value = ''
  if (pwd.value === PASSWORD) {
    sessionStorage.setItem('gate:ok', '1')
    checkUnlocked()
  } else {
    err.value = 'Wrong Password'
  }
}
function lock() {
  sessionStorage.removeItem('gate:ok')
  unlocked.value = false
}

// ====== Your original logic ======
onMounted(() => {
  checkUnlocked()
  console.log('Vue app started')
  console.log('Current route:', router.currentRoute.value.path)
})
</script>

<template>
  <!-- Before access: show password gate -->
  <div v-if="!unlocked" class="gate-wrap">
    <form class="gate-box" @submit.prevent="submit">
      <h1>Please input your password</h1>
      <input v-model="pwd" type="password" placeholder="Password" autofocus @keyup.enter="submit" />
      <button type="submit">Unlock</button>
      <p v-if="err" class="err">{{ err }}</p>
    </form>
  </div>

  <!-- After access: render the entire application -->
  <div v-else>
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
          <!-- <RouterLink to="/community" @click="() => console.log('Clicked Community')">Community</RouterLink> -->
          <!-- <button type="button" @click="lock" style="margin-left:.5rem">Lock</button> -->
        </nav>

        <ThemeToggle />
      </div>
    </header>

    <main class="container" style="padding:1.25rem 1rem;">
      <RouterView v-slot="{ Component, route }">
        <Transition name="page" mode="out-in">
          <div class="route-shell" :key="route.fullPath">
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
/* Transition animations (keeping your settings) */
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

/* Password gate styles */
.gate-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg, #f3f4f6);
}

.gate-box {
  width: 100%;
  max-width: 380px;
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, .06);
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: stretch;
}

.gate-box h1 {
  margin: 0;
  font-size: 18px;
  text-align: center;
}

.gate-box input {
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.gate-box button {
  padding: 10px;
  border-radius: 8px;
  border: 0;
  background: #111827;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.err {
  color: #dc2626;
  text-align: center;
  margin-top: 6px;
}
</style>
