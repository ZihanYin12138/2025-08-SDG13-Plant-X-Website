<!-- src/views/GardenPage.vue -->
<template>
  <!-- 顶部简介 -->
  <section class="container">
    <h2 class="title">Garden</h2>
    <p class="lead">
      Tools and tips for climate-adaptive home gardening — sunlight, soil, watering, composting, and more.
    </p>
  </section>

  <!-- 内容区（滑块与内容在同一框内） -->
  <section class="container">
    <div class="pane" role="region" aria-label="Garden sections">
      <!-- 顶部：分段滑块（与内容同框） -->
      <div class="seg-control" role="tablist" aria-label="Garden sections tabs">
        <div class="seg-rail">
          <!-- 滑块拇指 -->
          <div class="seg-thumb" :style="thumbStyle" aria-hidden="true"></div>

          <button
            role="tab"
            :aria-selected="active==='disease'"
            class="seg-item"
            @click="setActive('disease')"
          >Plant Disease Search</button>

          <button
            role="tab"
            :aria-selected="active==='plants'"
            class="seg-item"
            @click="setActive('plants')"
          >Plant Search</button>

          <button
            role="tab"
            :aria-selected="active==='rcmd'"
            class="seg-item"
            @click="setActive('rcmd')"
          >Plant Recommendations</button>
        </div>
      </div>

      <!-- 面板主体：渲染具体内容（已与上方同框） -->
      <div class="pane-body">
        <Transition :name="transitionName" mode="out-in">
          <div :key="active">
            <DiseaseSearch v-if="active==='disease'" />
            <PlantRcmd     v-else-if="active==='rcmd'" />
            <PlantSearch   v-else />
          </div>
        </Transition>
      </div>
    </div>
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

/** 切换核心（写回 URL 的 ?tab=，便于分享/后退前进） */
function activate(key, { writeQuery = true } = {}) {
  const newIdx = order.indexOf(key)
  transitionName.value = newIdx > lastIndex.value ? 'slide-left' : 'slide-right'
  lastIndex.value = newIdx
  active.value = key

  if (writeQuery) {
    const nextQuery = { ...route.query, tab: key }
    if (String(route.query.tab || '') !== key) {
      router.replace({ query: nextQuery })
    }
  }
}
function setActive(key) {
  if (!order.includes(key)) return
  activate(key, { writeQuery: true })
}

/** 从 URL 的 ?tab= 读取并应用（支持浏览器前进/后退） */
function applyTabFromQuery() {
  const tab = String(route.query.tab || '').toLowerCase()
  if (order.includes(tab)) {
    activate(tab, { writeQuery: false }) // 外部驱动，不回写，防循环
  }
}

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

/* ================== 外层统一面板（滑块与内容同框） ================== */
.pane{
  border: 1.5px solid var(--border);
  border-radius: 14px;
  background: var(--card);
  box-shadow: var(--shadow-sm);
  overflow: hidden; /* 让内部滑块圆角裁剪一致 */
}
.pane-body{
  padding: 14px 16px; /* 统一内部边距 */
}

/* 隐藏子页本身的外框，让视觉上只有一层 */
:deep(.section-box){
  border: 0 !important;
  border-radius: 0 !important;
  padding: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

/* ========== 顶部滑块 ========== */
.seg-control{ }
.seg-rail{
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  /* 本身不再用外边框，改为底部细分隔线以与主体区分 */
  border-bottom: 1.5px solid var(--border);
  background: var(--card);
}
.seg-item{
  position: relative;
  z-index: 1;
  height: 46px;
  border: none;               /* 与同框风格统一 */
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
