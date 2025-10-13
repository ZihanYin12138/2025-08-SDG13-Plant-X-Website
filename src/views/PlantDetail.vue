<!-- src/views/PlantDetail.vue -->
<template>
  <section class="section container">
    <!-- Breadcrumb -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <button class="breadcrumb__link as-link" @click="smartBack">
        {{ backCrumbLabel }}
      </button>
      <span class="breadcrumb__sep">›</span>
      <span class="breadcrumb__current">
        {{ plant?.common_name || preload?.common_name || '...' }}
      </span>
    </nav>

    <div v-if="loading">Loading…</div>
    <p v-else-if="error" class="error">Load failed: {{ error }}</p>

    <article v-else-if="plant" class="detail">
      <!-- Left: main image -->
      <div class="media">
        <img :src="coverUrl" :alt="plant.common_name || 'Plant photo'" />
      </div>

      <!-- Right: title + facts + description -->
      <div class="meta">
        <h1 class="title">{{ plant.common_name }}</h1>
        <p class="latin">{{ plant.scientific_name }}</p>
        <p v-if="renderOther(plant.other_name)" class="aka">
          aka: {{ renderOther(plant.other_name) }}
        </p>

        <!-- ===== Only show specified 8 items ===== -->
        <div class="facts">
          <p v-if="cycleText"><strong>Cycle:</strong> {{ cycleText }}</p>
          <p v-if="wateringSmart"><strong>Watering:</strong> {{ wateringSmart }}</p>
          <p v-if="hardinessZoneText"><strong>Hardiness Zone:</strong> {{ hardinessZoneText }}</p>
          <p v-if="sunMergedText"><strong>Sun:</strong> {{ sunMergedText }}</p>
          <p v-if="leafText"><strong>Leaf:</strong> {{ leafText }}</p>
          <p v-if="conesText"><strong>Cones:</strong> {{ conesText }}</p>
          <p v-if="growthText"><strong>Growth Rate:</strong> {{ growthText }}</p>
          <p v-if="careLevelValue">
            <strong>{{ careLevelLabel }}:</strong> {{ careLevelValue }}
          </p>
        </div>

        <p v-if="descriptionText" class="desc">{{ descriptionText }}</p>
      </div>
    </article>

    <!-- Feature cards -->
    <section v-if="plant" class="cards">
      <article class="card" v-if="wateringTitle || waterBenchmark || wateringGuide">
        <h3 class="card__title">
          💧 Watering
          <small v-if="wateringTitle">&nbsp;· {{ wateringTitle }}</small>
        </h3>
        <p v-if="waterBenchmark" class="muted">Benchmark: {{ waterBenchmark }}</p>
        <p v-if="wateringGuide">{{ wateringGuide }}</p>
      </article>

      <article class="card" v-if="sunShort || sunlightGuide">
        <h3 class="card__title">☀️ Sunlight <small v-if="sunShort">&nbsp;· {{ sunShort }}</small></h3>
        <p v-if="sunlightGuide">{{ sunlightGuide }}</p>
      </article>

      <article class="card" v-if="pruningMonthsText || pruningGuide">
        <h3 class="card__title">✂️ Pruning</h3>
        <p v-if="pruningMonthsText" class="muted">Best Months: {{ pruningMonthsText }}</p>
        <p v-if="pruningGuide">{{ pruningGuide }}</p>
      </article>

      <article class="card" v-if="conservationAny">
        <h3 class="card__title">🛡️ Conservation</h3>
        <p v-if="conservationStatus"><strong>Status:</strong> {{ conservationStatus }}</p>
        <p v-if="provenance"><strong>Provenance:</strong> {{ provenance }}</p>
        <p v-if="localBenefits"><strong>Local Benefits:</strong> {{ localBenefits }}</p>
        <p v-if="hortPotential"><strong>Horticultural Potential:</strong> {{ hortPotential }}</p>
        <p v-if="propagationMethods"><strong>Propagation:</strong> {{ propagationMethods }}</p>
        <p v-if="propagationLevel"><strong>Propagation Level:</strong> {{ propagationLevel }}</p>
        <p v-if="cultivationNote"><strong>Cultivation Note:</strong> {{ cultivationNote }}</p>
        <p v-if="soilText"><strong>Soil:</strong> {{ soilText }}</p>
      </article>
    </section>

    <!-- Distribution map -->
    <h2>Hardiness Map</h2>
    <div v-if="plant?.distribution_map?.distribution_map_html" class="dist">
      <iframe
        class="dist__iframe"
        :srcdoc="plant.distribution_map.distribution_map_html"
        sandbox="allow-scripts allow-same-origin"
        referrerpolicy="no-referrer"
      ></iframe>
    </div>
  </section>

  <div class="center">
    <button class="btn btn-ghost" @click="smartBack">
      {{ backButtonLabel }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPlantById, getThreatenedById, type PlantDetail } from '@/api/plants'
import threatenedImg from '@/assets/placeholder.jpg'

/* Solve "Extraneous non-props attributes (id)" —— catch id passed through router-view */
const props = defineProps<{ id?: string | number }>()

type PreloadCard = {
  general_plant_id?: number
  threatened_plant_id?: number
  common_name?: string
  scientific_name?: string
  image_url?: string
  other_name?: string[] | string
}

const PLACEHOLDER_IMG =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
      <rect fill="#f3f4f6" width="100%" height="100%"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            fill="#9ca3af" font-family="system-ui" font-size="24">No image</text>
    </svg>`
  )

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const plant = ref<PlantDetail | null>(null)

/** ====== From where ====== */
const fromSource = computed(() =>
  String(route.query.from || '') ||
  (window as any)?.history?.state?.from ||
  ''
)
/* Use path instead of route name to avoid "No match for { name:'PlantRcmd' }" */
const backTo = computed(() =>
  fromSource.value === 'rcmd'
    ? '/plantrcmd'
    : '/garden#plantsearch'
)
const backCrumbLabel = computed(() =>
  fromSource.value === 'rcmd' ? 'Recommendations' : 'Plant Search'
)
const backButtonLabel = computed(() =>
  fromSource.value === 'rcmd' ? '← Back to Recommendations' : '← Back to Garden'
)

function smartBack() {
  if (window.history.length > 1) {
    router.back()
    return
  }
  router.push(backTo.value)
}

const isThreatened = computed(() => {
  const t = String(route.query.type || '').toLowerCase()
  if (t) return t === 'threatened'
  const idt = String((plant.value as any)?.id_type || '').toLowerCase()
  return idt === 'threatened'
})

const preload = ((): PreloadCard | undefined => {
  const s = (route as any).state?.preload ?? (window?.history?.state as any)?.preload
  return s as PreloadCard | undefined
})()

const coverUrl = computed(() => {
  if (isThreatened.value) return threatenedImg
  const arr = plant.value?.image_urls
  if (Array.isArray(arr) && arr.length) return arr[1] || arr[0]
  if (preload?.image_url) return preload.image_url
  return PLACEHOLDER_IMG
})

function renderOther(v?: string[] | string) {
  return Array.isArray(v) ? v.join(', ') : (v || '')
}

/* —— Text beautification —— */
function prettyCycle(v?: string) {
  if (!v) return ''
  const s = v.toLowerCase()
  if (s.includes('perennial')) return 'Perennial'
  if (s.includes('biennial')) return 'Biennial'
  if (s.includes('annual')) return 'Annual'
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

/* -------------------------
 * Threatened exclusive mapping
 * ------------------------- */
const tdesc = computed(() => (plant.value as any)?.threatened?.description || {})
const tcare = computed(() => (plant.value as any)?.threatened?.care_guide || {})

const conservationStatus   = computed(() => tdesc.value?.conservation_status || '')
const provenance           = computed(() => tdesc.value?.provenance || '')
const weedRating           = computed(() => tdesc.value?.weed_rating || '')
const localBenefits        = computed(() => tdesc.value?.local_benefits_description || '')
const hortPotential        = computed(() => tdesc.value?.horticultural_potential || '')

const propagationMethods   = computed(() => tcare.value?.propagation_methods || '')
const propagationLevel     = computed(() => tcare.value?.propagation_level || '')
const cultivationNote      = computed(() => tcare.value?.cultivation_note || '')
const soilText             = computed(() => {
  const soil = tcare.value?.soil
  return Array.isArray(soil) ? soil.join(', ') : (soil || '')
})

/** Description: prioritize threatened.description, then general description */
const descriptionText = computed(() => {
  if (isThreatened.value) {
    const parts = [
      tdesc.value?.conservation_benefit,
      tdesc.value?.local_benefits_description,
      tdesc.value?.horticultural_potential,
      tcare.value?.cultivation_note
    ].filter(Boolean)
    if (parts.length) return parts.join(' · ')
  }
  const d: any = plant.value?.description
  if (d) return d.brief || d.summary || d.description || ''
  return ''
})

/* —— Three main sections —— */
const cg = computed(() => (plant.value as any)?.care_guide || {})
const wateringTitle   = computed(() =>
  plant.value?.watering || cg.value?.watering || (cultivationNote.value ? 'See note' : '')
)
const waterBenchmark  = computed(() => cg.value?.watering_general_benchmark || '')
const wateringGuide   = computed(() => cg.value?.watering_guide || '')
const sunShort        = computed(() => {
  const arr = cg.value?.sunlight
  if (Array.isArray(arr) && arr.length) return arr.join(', ')
  if (tcare.value?.sun) return tcare.value.sun
  return ''
})
const sunlightGuide   = computed(() => cg.value?.sunlight_guide || '')
const pruningMonthsText = computed(() => {
  const p = cg.value?.pruning_month
  return Array.isArray(p) && p.length ? p.join(', ') : ''
})
const pruningGuide    = computed(() => cg.value?.pruning_guide || '')

/* ===========================
 *  Facts
 * =========================== */
const hardinessZoneText = computed(() => {
  const html = plant.value?.distribution_map?.distribution_map_html || ''
  const m = html.match(/"zone"[\s\S]*?"min"\s*:\s*(\d+)[\s\S]*?"max"\s*:\s*(\d+)/)
  if (m) {
    const min = Number(m[1]), max = Number(m[2])
    if (min && max) return min === max ? `USDA ${min}` : `USDA ${min}–${max}`
  }
  return ''
})
const cycleText  = computed(() =>
  prettyCycle(plant.value?.plant_cycle || (plant.value as any)?.description?.plant_cycle)
)
const growthText = computed(() =>
  prettyGrowth(plant.value?.growth_rate || (plant.value as any)?.care_guide?.growth_rate)
)
const sunMergedText = computed(() => {
  const vals: string[] = []
  const push = (x: any) => {
    if (!x) return
    if (Array.isArray(x)) vals.push(...x.map(String))
    else vals.push(String(x))
  }
  push((plant.value as any)?.threatened?.care_guide?.sun)
  push((plant.value as any)?.care_guide?.sunlight)
  push((plant.value as any)?.sun_expose)
  return Array.from(new Set(vals.map(s => s.trim()).filter(Boolean))).join(', ')
})
const wateringSmart = computed(() => {
  const top = plant.value?.watering
  const cgWater = (plant.value as any)?.care_guide?.watering
  const note = (plant.value as any)?.threatened?.care_guide?.cultivation_note
            || (plant.value as any)?.care_guide?.watering_guide
  return top || cgWater || (note ? 'See note' : '')
})
const joinList = (v: any): string =>
  Array.isArray(v) ? v.filter(Boolean).join(', ') : (v ?? '').toString()
const leafText  = computed(() =>
  joinList((plant.value as any)?.threatened?.description?.leaf ?? (plant.value as any)?.description?.leaf)
)
const conesText = computed(() =>
  joinList((plant.value as any)?.threatened?.description?.cones ?? (plant.value as any)?.description?.cones)
)
const careLevelValue = computed(() =>
  (plant.value as any)?.threatened?.care_guide?.propagation_level
  || (plant.value as any)?.care_guide?.care_level
  || ''
)
const careLevelLabel = computed(() =>
  (plant.value as any)?.threatened?.care_guide?.propagation_level ? 'Propagation Level' : 'Care Level'
)
const conservationAny = computed(() =>
  !!(conservationStatus.value
    || provenance.value
    || localBenefits.value
    || hortPotential.value
    || propagationMethods.value
    || propagationLevel.value
    || cultivationNote.value
    || soilText.value)
)

/* -------------------------
 * Loading
 * ------------------------- */
onMounted(async () => {
  loading.value = true
  error.value = ''

  // If there's preload, render first to avoid white screen
  if (preload) {
    const gpId = preload.general_plant_id ?? 0
    plant.value = {
      general_plant_id: gpId,
      threatened_plant_id: preload.threatened_plant_id,
      common_name: preload.common_name || '',
      scientific_name: preload.scientific_name || '',
      other_name: preload.other_name,
      image_urls: preload.image_url ? [preload.image_url] : []
    } as PlantDetail
  }

  try {
    const rawId = props.id ?? route.params.id
    const id = typeof rawId === 'string' ? parseInt(rawId, 10) : Number(rawId)

    const data = (String(route.query.type || '').toLowerCase() === 'threatened')
      ? await getThreatenedById(id)
      : await getPlantById(id)

    plant.value = data
  } catch (e: any) {
    if (!preload) error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* Breadcrumb */
.breadcrumb {
  display: flex; align-items: center; gap: .5rem;
  margin: 4px 0 12px; font-size: 14px;
}
.breadcrumb__link { color: var(--fg); font-weight: 700; text-decoration: none; }
.breadcrumb__link:hover { text-decoration: underline; }
.as-link {
  background: none; border: 0; padding: 0; cursor: pointer; font: inherit; color: var(--fg);
}
.breadcrumb__sep { color: var(--muted); }
.breadcrumb__current { color: var(--fg); }

/* Main content */
.detail{
  display:grid; gap:1.25rem;
  grid-template-columns:1.1fr .9fr; align-items:start;
}
@media (max-width:900px){ .detail{ grid-template-columns:1fr } }
.media img{
  width:100%; border-radius:12px; object-fit:cover;
  background: var(--surface);
}
.title{ margin:.25rem 0 }
.latin{ color:var(--muted); font-style:italic }
.aka{ color:var(--muted); margin:.25rem 0 }

/* Facts card */
.facts{
  display:grid; grid-template-columns: 1fr 1fr;
  gap:.5rem 1.25rem;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius:10px;
  padding:.75rem .9rem; margin-top:.75rem;
  box-shadow: var(--shadow-sm);
}
.facts p{ margin:0 }

.desc{ margin-top:.75rem; line-height:1.6 }
.error{ color:#c00 }

/* Three main sections */
.cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin-top: 18px;
}
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: var(--shadow-sm);
}
.card__title { margin: 0 0 6px; }
.muted { color: var(--muted); margin: 0 0 6px; }

/* Distribution map */
.dist{ margin-top:16px }
.dist__iframe{
  width:100%;
  min-height:550px;
  border:1px solid var(--border);
  border-radius:10px;
  background:var(--card);
  box-shadow: var(--shadow-sm);
}

/* Bottom return button container */
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50px;
}
.btn.btn-ghost {
  border: 1px solid var(--border);
  background: transparent;
  padding: .5rem .8rem;
  border-radius: 10px;
  cursor: pointer;
  background-color: rgb(76, 76, 76);
}
</style>
