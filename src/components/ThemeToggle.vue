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

let mq
onMounted(() => {
  const cached = localStorage.getItem('theme')
  const sysDark = window.matchMedia('(prefers-color-scheme: dark)')
  mq = sysDark
  const sys = sysDark.matches ? 'dark' : 'light'
  theme.value = cached || sys
  apply(theme.value)
  // 当用户在系统设置里切换深浅色时同步
  mq.addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) { // 用户未手动选择时，跟随系统
      theme.value = e.matches ? 'dark' : 'light'
      apply(theme.value)
    }
  })
})
onBeforeUnmount(() => { mq && mq.removeEventListener?.('change', () => {}) })
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

    