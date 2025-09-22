<!-- src/views/GardenPage.vue -->
<template>
  <!-- 顶部简介 -->
  <section class="container">
    <h2 class="title">Garden</h2>
    <p class="lead">
      Tools and tips for climate-adaptive home gardening — sunlight, soil, watering, composting, and more.
    </p>
  </section>

  <!-- 顶部：三等分滑块 -->
  <section class="container">
    <div class="seg-control" role="tablist" aria-label="Garden sections">
      <div class="seg-rail">
        <!-- 滑块 -->
        <div class="seg-thumb" :style="thumbStyle" aria-hidden="true"></div>

        <button role="tab" :aria-selected="active==='disease'" class="seg-item" @click="setActive('disease')">Disease</button>
        <button role="tab" :aria-selected="active==='plants'"  class="seg-item" @click="setActive('plants')">Plant</button>
        <button role="tab" :aria-selected="active==='rcmd'"    class="seg-item" @click="setActive('rcmd')">Recommend</button>
      </div>
    </div>
  </section>

  <!-- 内容区：动态组件 + 左右滑动动画 -->
  <section class="container">
    <Transition :name="transitionName" mode="out-in">
      <component :is="currentComponent" :key="active" />
    </Transition>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PlantSearch from '@/views/PlantSearch.vue'
import DiseaseSearch from '@/views/DiseaseSearch.vue'
import PlantRcmd from '@/views/PlantRcmd.vue'

const route = useRoute()
const router = useRouter()

const order = ['disease', 'plants', 'rcmd'] // 左→右顺序
const idMap = { disease: 'diseases', plants: 'plantsearch', rcmd: 'plantrcmd' }
const aliasToKey = {
  '#diseases': 'disease',
  '#disease':  'disease',     // 兼容旧别名
  '#plantsearch': 'plants',
  '#plants':      'plants',   // 兼容旧别名
  '#plantrcmd':   'rcmd',
  '#rcmd':        'rcmd'      // 兼容旧别名
}

const active = ref('plants')
const lastIndex = ref(order.indexOf(active.value))
const transitionName = ref('slide-left')

/** 统一的切换函数（可选择是否写回 hash，避免 watch 里循环） */
function activate(key, { writeHash = true } = {}) {
  const newIdx = order.indexOf(key)
  transitionName.value = newIdx > lastIndex.value ? 'slide-left' : 'slide-right'
  lastIndex.value = newIdx
  active.value = key

  if (writeHash) {
    const hash = '#' + idMap[key]
    if (route.hash !== hash) router.replace({ hash })
  }
}
function setActive(key) {
  activate(key, { writeHash: true })
}

/** 根据 hash 同步当前页（用于首次进入 & 之后的 hash 变化） */
function syncFromHash(h) {
  const key = aliasToKey[(h || '').toLowerCase()] || 'plants'
  activate(key, { writeHash: false })
}

/** 监听路由 hash 变化（包括 RouterLink 跳转、浏览器前进/后退等） */
watch(() => route.hash, (h) => { syncFromHash(h) })

/** 初次进入按 hash 定位 */
onMounted(() => { syncFromHash(route.hash) })

/* ===== 动态渲染与滑块样式 ===== */
const currentComponent = computed(() => {
  if (active.value === 'disease') return DiseaseSearch
  if (active.value === 'rcmd')    return PlantRcmd
  return PlantSearch
})
const thumbStyle = computed(() => {
  const idx = order.indexOf(active.value)
  return { transform: `translateX(${idx * 100}%)` }
})
</script>

<style scoped>
.title { margin: 0 0 .5rem; }
.lead { color: var(--muted); }

/* ========== 滑块式分段控件 ========== */
.seg-rail{
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-radius: 12px;
  border: 1.5px solid var(--border);
  background: var(--card);
  box-shadow: var(--shadow-sm);
}
.seg-item{
  position: relative;
  z-index: 1;
  height: 44px;
  border: 0;
  background: transparent;
  color: var(--fg);
  cursor: pointer;
  font: inherit;
}
.seg-item[aria-selected="true"]{ font-weight: 700; }
.seg-thumb{
  position: absolute; z-index: 0; top: 0; left: 0;
  width: calc(100% / 3); height: 100%;
  background: color-mix(in oklab, var(--brand) 16%, var(--surface));
  box-shadow: 0 0 0 2px color-mix(in oklab, var(--brand) 18%, transparent) inset;
  transition: transform .25s cubic-bezier(.22,.61,.36,1);
}

/* ========== 内容切换动画（方向感） ========== */
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active{
  transition: opacity .22s ease, transform .22s ease;
}
.slide-left-enter-from { opacity: 0; transform: translateX(28px); }
.slide-left-leave-to   { opacity: 0; transform: translateX(-28px); }
.slide-right-enter-from{ opacity: 0; transform: translateX(-28px); }
.slide-right-leave-to  { opacity: 0; transform: translateX(28px); }
</style>
