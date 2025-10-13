<!-- src/views/GardenPage.vue -->
<template>
  <section class="container">
    <h2 class="title">Garden</h2>
    <p class="lead">
      Tools and tips for climate-adaptive home gardening — sunlight, soil, watering, composting, and more.
    </p>
  </section>

  <section class="container">
    <div class="pane" role="region" aria-label="Garden sections">
      <div class="seg-control" role="tablist" aria-label="Garden sections tabs">
        <div class="seg-rail">
          <div class="seg-thumb" :style="thumbStyle" aria-hidden="true"></div>

          <button role="tab" :aria-selected="active==='disease'" class="seg-item" @click="setActive('disease')">
            Plant Disease Search
          </button>
          <button role="tab" :aria-selected="active==='plants'" class="seg-item" @click="setActive('plants')">
            Plant Search
          </button>
          <button role="tab" :aria-selected="active==='rcmd'" class="seg-item" @click="setActive('rcmd')">
            Plant Recommendations
          </button>
        </div>
      </div>

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
import { ref, computed, watch, onMounted, onActivated } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PlantSearch from '@/views/PlantSearch.vue'
import DiseaseSearch from '@/views/DiseaseSearch.vue'
import PlantRcmd from '@/views/PlantRcmd.vue'

const route = useRoute()
const router = useRouter()

const order = ['disease', 'plants', 'rcmd']

/** Initial active read from URL (fallback to plants if not available) */
const initialTab = (() => {
  const t = String(route.query.tab || '').toLowerCase()
  return order.includes(t) ? t : 'plants'
})()
const active = ref(initialTab)
const lastIndex = ref(order.indexOf(active.value))
const transitionName = ref('slide-left')

function activate(key, { writeQuery = true } = {}) {
  const newIdx = order.indexOf(key)
  transitionName.value = newIdx > lastIndex.value ? 'slide-left' : 'slide-right'
  lastIndex.value = newIdx
  active.value = key
  if (writeQuery) {
    const nextQuery = { ...route.query, tab: key }
    if (String(route.query.tab || '') !== key) router.replace({ query: nextQuery })
  }
}
function setActive(key) { if (order.includes(key)) activate(key, { writeQuery: true }) }

/** Synchronize tabs from URL - executed for the first time, back/forward, and when keepAlive is activated */
function applyTabFromQuery() {
  const tab = String(route.query.tab || '').toLowerCase()
  if (order.includes(tab)) activate(tab, { writeQuery: false })
}

onMounted(applyTabFromQuery)
onActivated(applyTabFromQuery)
watch(() => route.query.tab, applyTabFromQuery)

/** Slider displacement style */
const thumbStyle = computed(() => {
  const idx = order.indexOf(active.value)
  return { transform: `translateX(${idx * 100}%)` }
})
</script>

<style scoped>
.title { margin: 0 0 .5rem; }
.lead { color: var(--muted); }

.pane{
  border: 1.5px solid var(--border);
  border-radius: 14px;
  background: var(--card);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.pane-body{ padding: 14px 16px; }

:deep(.section-box){
  border: 0 !important;
  border-radius: 0 !important;
  padding: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.seg-rail{
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-bottom: 1.5px solid var(--border);
  background: var(--card);
}
.seg-item{
  position: relative;
  z-index: 1;
  height: 46px;
  border: none;
  background: transparent;
  color: var(--fg);
  cursor: pointer;
  font: inherit;
}
.seg-item[aria-selected="true"]{ font-weight: 700; }

.seg-item + .seg-item::before{
  content: ""; position: absolute; left: 0; top: 8px; bottom: 8px;
  width: 1.5px; background: var(--border);
}

.seg-thumb{
  position: absolute; z-index: 0; top: 0; left: 0;
  width: calc(100% / 3); height: 100%;
  background: color-mix(in oklab, var(--brand) 16%, var(--surface));
  box-shadow: 0 0 0 2px color-mix(in oklab, var(--brand) 18%, transparent) inset;
  transition: transform .25s cubic-bezier(.22,.61,.36,1);
}

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
