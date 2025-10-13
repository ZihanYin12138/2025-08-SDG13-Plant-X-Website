<!-- src/views/UrbanThreaten.vue -->
<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UrbanMap from '@/views/UrbanMap.vue'
import TPmapping from '@/views/TPmapping.vue'
import ClimateImpact from '@/views/ClimateImpact.vue'

defineOptions({ name: 'UrbanWild' })

const route = useRoute()
const router = useRouter()

const order = ['urban', 'climate', 'threatened']

const initTab = (() => {
  const q = String(route.query.tab || '').toLowerCase()
  return order.includes(q) ? q : 'climate'
})()
const active = ref(initTab)

function setActive(key) {
  if (!order.includes(key)) return
  active.value = key
  const nextQuery = { ...route.query, tab: key }
  if (String(route.query.tab || '') !== key) router.replace({ query: nextQuery })
}

watch(() => route.query.tab, (t) => {
  const q = String(t || '').toLowerCase()
  if (order.includes(q)) active.value = q
})

const thumbStyle = computed(() => {
  const idx = order.indexOf(active.value)
  return { transform: `translateX(${idx * 100}%)` }
})
</script>

<template>
  <!-- Top Introduction -->
  <section class="container">
    <h2 class="title">Urban &amp; Threaten</h2>
    <p class="lead">
      Explore native and resilient species in urban and wild landscapes, supporting biodiversity and climate resilience.
    </p>
  </section>

  <section class="container">
    <div class="pane" role="region" aria-label="Urban & Threaten sections">

      <div class="seg-control" role="tablist" aria-label="Urban & Threaten tabs">
        <div class="seg-rail">
          <div class="seg-thumb" :style="thumbStyle" aria-hidden="true"></div>

          <button
            role="tab"
            :aria-selected="active==='urban'"
            class="seg-item"
            @click="setActive('urban')"
          >Urban Plants Map</button>

          <button
            role="tab"
            :aria-selected="active==='climate'"
            class="seg-item"
            @click="setActive('climate')"
          >Climate Impact On Threaten Plants</button>

          <button
            role="tab"
            :aria-selected="active==='threatened'"
            class="seg-item"
            @click="setActive('threatened')"
          >Threatened Plants Map</button>
        </div>
      </div>

      <div class="pane-body">
        <div v-show="active==='urban'">
          <UrbanMap />
        </div>

        <div v-show="active==='climate'">
          <ClimateImpact />
        </div>

        <div v-show="active==='threatened'">
          <TPmapping />
        </div>
      </div>
    </div>
  </section>
</template>

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
</style>
