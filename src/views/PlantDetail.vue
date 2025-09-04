<template>
  <section class="section container">
    <!-- 面包屑 -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <RouterLink class="breadcrumb__link" to="/garden">Species</RouterLink>
      <span class="breadcrumb__sep">›</span>
      <span class="breadcrumb__current">
        {{ plant?.common_name || preload?.common_name || '...' }}
      </span>
    </nav>

    <div v-if="loading">Loading…</div>
    <p v-else-if="error" class="error">加载失败：{{ error }}</p>

    <article v-else-if="plant" class="detail">
      <!-- 左：主图 -->
      <div class="media">
        <img :src="coverUrl" :alt="plant.common_name" />
      </div>

      <!-- 右：标题 + facts + 简介 -->
      <div class="meta">
        <h1 class="title">{{ plant.common_name }}</h1>
        <p class="latin">{{ plant.scientific_name }}</p>
        <p v-if="renderOther(plant.other_name)" class="aka">
          aka: {{ renderOther(plant.other_name) }}
        </p>

        <!-- Facts -->
        <div class="facts">
          <p v-if="plant.plant_cycle">
            <strong>Cycle:</strong> {{ prettyCycle(plant.plant_cycle) }}
          </p>
          <p v-if="hardinessZone">
            <strong>Hardiness Zone:</strong> {{ hardinessZone }}
          </p>
          <p v-if="hasLeaf"><strong>Leaf:</strong> Yes</p>
          <p v-if="careLevel"><strong>Care Level:</strong> {{ careLevel }}</p>

          <p v-if="plant.watering"><strong>Watering:</strong> {{ plant.watering }}</p>
          <p v-if="sunText"><strong>Sun:</strong> {{ sunText }}</p>
          <p v-if="plant.growth_rate">
            <strong>Growth Rate:</strong> {{ prettyGrowth(plant.growth_rate) }}
          </p>
        </div>

        <!-- 简介（从 description 表里挑一段） -->
        <p v-if="plant.description" class="desc">
          {{ (plant.description && (plant.description.brief || plant.description.summary || plant.description.description || '')) }}
        </p>

        
      </div>
    </article>

    <!-- ===== 三大板块：Watering / Sunlight / Pruning ===== -->
    <section v-if="plant" class="cards">
      <!-- Watering -->
      <article class="card" v-if="wateringTitle || wateringGuide">
        <h3 class="card__title">
          💧 Watering
          <small v-if="wateringTitle">&nbsp;· {{ wateringTitle }}</small>
        </h3>
        <p v-if="waterBenchmark" class="muted">Benchmark: {{ waterBenchmark }}</p>
        <p v-if="wateringGuide">{{ wateringGuide }}</p>
      </article>

      <!-- Sunlight -->
      <article class="card" v-if="sunShort || sunlightGuide">
        <h3 class="card__title">☀️ Sunlight <small v-if="sunShort">&nbsp;· {{ sunShort }}</small></h3>
        <p v-if="sunlightGuide">{{ sunlightGuide }}</p>
      </article>

      <!-- Pruning -->
      <article class="card" v-if="pruningMonthsText || pruningGuide">
        <h3 class="card__title">✂️ Pruning</h3>
        <p v-if="pruningMonthsText" class="muted">Best Months: {{ pruningMonthsText }}</p>
        <p v-if="pruningGuide">{{ pruningGuide }}</p>
      </article>
    </section>

    <!-- （可选）分布图：后端返回完整 HTML 用 iframe 展示 -->
    <div v-if="plant?.distribution_map?.distribution_map_html" class="dist">
      <iframe
        class="dist__iframe"
        :srcdoc="plant.distribution_map.distribution_map_html"
        sandbox="allow-scripts allow-same-origin"
        referrerpolicy="no-referrer"
      ></iframe>
    </div>
  </section>
  <RouterLink class="btn btn-ghost" to="/garden">Going Back to Garden</RouterLink>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getPlantById, type PlantDetail, type Plant } from '@/api/plants'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const plant = ref<PlantDetail | null>(null)

// 从卡片传来的兜底
const preload = (route as any).state?.preload as Plant | undefined

// 封面：优先详情第一张 → 兜底卡片图
const coverUrl = computed(() => {
  if (plant.value?.image_urls?.length) return plant.value.image_urls[1]
  return preload?.image_url || ''
})

function renderOther(v?: string[] | string) {
  return Array.isArray(v) ? v.join(', ') : (v || '')
}

/* —— 友好文案 —— */
function prettyCycle(v?: string) {
  if (!v) return ''
  const s = v.toLowerCase()
  if (s.includes('every year')) return 'Perennial'
  if (s.includes('every 2')) return 'Biennial'
  return v
}
function prettyGrowth(v?: string) {
  if (!v) return ''
  const s = v.toLowerCase()
  if (s === 'low' || s === 'slow') return 'Low'
  if (s === 'moderate') return 'Moderate'
  if (s === 'high' || s === 'fast') return 'Fast'
  return v
}
const sunText = computed(() => {
  const raw = plant.value?.sun_expose
  if (!raw) return ''
  return Array.isArray(raw) ? raw.join(', ') : raw
})

/* —— facts 派生 —— */
const hardinessZone = computed(() => {
  // 你给的样例中 zone 没直接在 JSON 里提供（在 distribution_map 的 HTML 内）；
  // 如需精确解析可在后端单独提供。这里先留空或自行写死。
  return ''
})
const hasLeaf = computed(() => true)
const careLevel = computed(() => (plant.value as any)?.care_guide?.care_level || '')

/* —— 三大板块数据 —— */
const cg = computed(() => (plant.value as any)?.care_guide || {})
const wateringTitle = computed(() => plant.value?.watering || cg.value?.watering || '')
const waterBenchmark = computed(() => cg.value?.watering_general_benchmark || '')
const wateringGuide = computed(() => cg.value?.watering_guide || '')
const sunShort = computed(() => {
  const arr = cg.value?.sunlight
  if (Array.isArray(arr) && arr.length) return arr.join(', ')
  return ''
})
const sunlightGuide = computed(() => cg.value?.sunlight_guide || '')
const pruningMonthsText = computed(() => {
  const p = cg.value?.pruning_month
  return Array.isArray(p) && p.length ? p.join(', ') : ''
})
const pruningGuide = computed(() => cg.value?.pruning_guide || '')

onMounted(async () => {
  loading.value = true
  error.value = ''

  // 先用 preload 渲染，避免白屏
  if (preload) {
    plant.value = {
      general_plant_id: preload.general_plant_id,
      common_name: preload.common_name,
      scientific_name: preload.scientific_name,
      other_name: preload.other_name,
      image_urls: preload.image_url ? [preload.image_url] : []
    } as PlantDetail
  }

  try {
    const idParam = route.params.id
    const id = typeof idParam === 'string' ? parseInt(idParam, 10) : Number(idParam)
    const data = await getPlantById(id)
    plant.value = data
  } catch (e: any) {
    if (!preload) error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* 面包屑 */
.breadcrumb {
  display: flex; align-items: center; gap: .5rem;
  margin: 4px 0 12px; font-size: 14px;
}
.breadcrumb__link { color: #1f2937; font-weight: 700; text-decoration: none; }
.breadcrumb__link:hover { text-decoration: underline; }
.breadcrumb__sep { color: #6b7280; }
.breadcrumb__current { color: #111827; }

/* 主体 */
.detail{display:grid;gap:1.25rem;grid-template-columns:1.1fr .9fr;align-items:start;}
@media (max-width:900px){ .detail{ grid-template-columns:1fr } }
.media img{width:100%;border-radius:12px;object-fit:cover}
.title{margin:.25rem 0}
.latin{color:var(--muted);font-style:italic}
.aka{color:var(--muted);margin:.25rem 0}

.facts{
  display:grid; grid-template-columns: 1fr 1fr;
  gap:.5rem 1.25rem; background:#f3f4f6;
  border-radius:10px; padding:.75rem .9rem; margin-top:.75rem;
}
.facts p{margin:0}

.desc{margin-top:.75rem;line-height:1.6}
.error{color:#c00}

/* 三大板块 */
.cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin-top: 18px;
}
.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.card__title { margin: 0 0 6px; }
.muted { color: #6b7280; margin: 0 0 6px; }

/* 分布图 */
.dist{margin-top:16px}
.dist__iframe{
  width:100%;
  min-height:420px;
  border:1px solid #e5e7eb;
  border-radius:10px;
  background:#fff;
}

.btn btn-ghost{
    text-align: center;
}
</style>
