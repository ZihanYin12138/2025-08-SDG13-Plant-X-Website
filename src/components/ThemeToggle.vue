<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const theme = ref('light')
const nextLabel = computed(() => theme.value === 'dark' ? 'light' : 'dark')

const apply = (t) => document.documentElement.setAttribute('data-theme', t)
const persist = (t) => localStorage.setItem('theme', t)

const toggle = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  persist(theme.value)
  apply(theme.value)
}

let mq, onChange
onMounted(() => {
  const cached = localStorage.getItem('theme')
  mq = window.matchMedia('(prefers-color-scheme: dark)')
  const sys = mq.matches ? 'dark' : 'light'

  theme.value = cached || sys
  apply(theme.value)

  onChange = (e) => {
    if (!localStorage.getItem('theme')) { // 仅当未手动指定时跟随系统
      theme.value = e.matches ? 'dark' : 'light'
      apply(theme.value)
    }
  }
  mq.addEventListener?.('change', onChange)
})

onBeforeUnmount(() => {
  mq?.removeEventListener?.('change', onChange)
})
</script>


<style scoped>
.hide-on-mobile { display: none; }
@media (min-width: 768px) { .hide-on-mobile { display: inline; } }
</style>

<template>
  <button class="btn btn-ghost" @click="toggle" :title="`Switch to ${nextLabel} mode`" :aria-label="`Switch to ${nextLabel} mode`">
    <span v-if="theme==='dark'" aria-hidden="true">🌙</span>
    <span v-else aria-hidden="true">☀️</span>
    <span class="hide-on-mobile">{{ theme==='dark' ? 'Dark' : 'Light' }}</span>
  </button>
</template>

    