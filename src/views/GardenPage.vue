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

        <button
          role="tab"
          :aria-selected="active==='disease'"
          class="seg-item"
          @click="setActive('disease')"
        >Disease</button>

        <button
          role="tab"
          :aria-selected="active==='plants'"
          class="seg-item"
          @click="setActive('plants')"
        >Plant</button>

        <button
          role="tab"
          :aria-selected="active==='rcmd'"
          class="seg-item"
          @click="setActive('rcmd')"
        >Recommend</button>
      </div>
    </div>
  </section>

  <!-- 内容区：左右滑动动画 + 明确渲染组件 -->
  <section class="container">
    <Transition :name="transitionName" mode="out-in">
      <div :key="active">
        <DiseaseSearch v-if="active==='disease'" />
        <PlantRcmd     v-else-if="active==='rcmd'" />
        <PlantSearch   v-else />
      </div>
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

/** 左→右顺序用于决定动画方向 */
const order = ['disease', 'plants', 'rcmd']

/** 当前激活的分段 */
const active = ref('plants')
const lastIndex = ref(order.indexOf(active.value))
const transitionName = ref('slide-left')

/** 切换核心（可选择是否把 tab 写回到 URL 的 query） */
function activate(key, { writeQuery = true } = {}) {
  const newIdx = order.indexOf(key)
  transitionName.value = newIdx > lastIndex.value ? 'slide-left' : 'slide-right'
  lastIndex.value = newIdx
  active.value = key

  if (writeQuery) {
    const nextQuery = { ...route.query, tab: key }
    // 避免重复 replace 造成不必要的导航
    if (String(route.query.tab || '') !== key) {
      router.replace({ query: nextQuery })
    }
  }
}
function setActive(key) {
  if (!order.includes(key)) return
  activate(key, { writeQuery: true })
}

/** 从 URL 的 ?tab= 读取并应用 */
function applyTabFromQuery() {
  const tab = String(route.query.tab || '').toLowerCase()
  if (order.includes(tab)) {
    activate(tab, { writeQuery: false }) // 外部驱动，不回写，防循环
  }
}

/** 首次进入根据 ?tab 定位；其后监听 ?tab 变化（前进/后退等） */
onMounted(() => { applyTabFromQuery() })
watch(() => route.query.tab, () => { applyTabFromQuery() })

/** 滑块位移样式 */
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
  overflow: hidden; /* 让滑块圆角生效 */
}
.seg-item{
  position: relative;
  z-index: 1; /* 让文字在滑块之上 */
  height: 44px;
  border: 0;
  background: transparent;
  color: var(--fg);
  cursor: pointer;
  font: inherit;
}
.seg-item[aria-selected="true"]{
  font-weight: 700;
}
.seg-thumb{
  position: absolute;
  z-index: 0;
  top: 0; left: 0;
  width: calc(100% / 3);
  height: 100%;
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
