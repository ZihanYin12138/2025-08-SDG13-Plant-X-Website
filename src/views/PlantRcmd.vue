<!-- src/views/PlantRcmd.vue -->
<template>
  <!-- Top Introduction -->
  <section class="container" id="plantrcmd">
    <div class="section-box">
      <h2>Plant Recommendation</h2>
      <p>Choose a location on map to see aggregated weather for the area and plant recommendations at bottom.</p>

      <!-- Maps and Weather -->
      <section class="container">
        <div class="twocol">
          <div class="section-box">
            <div class="panel-head">
              <div class="panel-title">
                Select Location (Australia)
              </div>

              <div class="panel-actions" style="display:flex; align-items:center; gap:10px;">
                <button class="btn sm ghost"
                        @click="openCoordModal"
                        :disabled="isRefreshing"
                        aria-haspopup="dialog"
                        aria-controls="coord-modal">
                  Input your own Coordinates
                </button>
              </div>
            </div>

            <div class="map-wrap">
              <div ref="mapEl" class="map" role="application" aria-label="Australia map (click to select)"></div>
              <div v-if="!pendingPoint && !point" class="map-hint">Point a map location / type in coordinates.</div>
            </div>

            <!-- Coordinate input pop-up window -->
            <Teleport to="body">
              <div v-if="showCoordModal"
                   class="modal-overlay"
                   @click.self="closeCoordModal"
                   aria-hidden="false">
                <div class="modal" id="coord-modal" role="dialog" aria-modal="true" aria-labelledby="coord-modal-title">
                  <div class="modal-head">
                    <h3 id="coord-modal-title" class="modal-title">Input your own coordinates</h3>
                    <button class="btn icon" @click="closeCoordModal" :disabled="isRefreshing" aria-label="Close">×</button>
                  </div>

                  <div class="coordbar">
                    <input
                      class="coord-input"
                      type="number"
                      step="0.01"
                      placeholder="Latitude (e.g. -33.8688)"
                      v-model="latInput"
                      @keyup.enter="submitCoord"
                    />
                    <input
                      class="coord-input"
                      type="number"
                      step="0.01"
                      placeholder="Longitude (e.g. 151.2093)"
                      v-model="lngInput"
                      @keyup.enter="submitCoord"
                    />
                    <button class="btn" @click="submitCoord" :disabled="isRefreshing || !latInput || !lngInput">Search / Recommend</button>
                    <button class="btn ghost" @click="clearAll" :disabled="isRefreshing || (!latInput && !lngInput && !point && !pendingPoint)">Clear</button>
                  </div>

                  <p v-if="inputError" class="error" style="margin-top:8px;">{{ inputError }}</p>
                  <p class="muted" style="margin-top:6px;">
                    Tip: Australia bounds approx. lat -48 ~ -10, lon 112 ~ 154.
                  </p>
                </div>
              </div>
            </Teleport>
          </div>

          <!-- Right: Weather KPI -->
          <div class="section-box weather-box">
            <div class="panel-head">
              <div class="panel-title">16-Day Aggregated Weather</div>
            </div>

            <div class="kpi-grid two-col">
              <div class="kpi" v-for="m in kpiList" :key="m.key">
                <div class="kpi-circle" :aria-busy="kpiLoading" :style="kpiStyle(m.key)">
                  <div class="kpi-value">
                    <template v-if="kpiLoading">…</template>
                    <template v-else>{{ m.format(metrics[m.key]) }}</template>
                  </div>
                </div>
                <div class="kpi-label">{{ m.label }}</div>
              </div>
            </div>

            <p v-if="kpiError" class="error">Weather load failed: {{ kpiError }}</p>
            <p class="muted" v-if="!point">Select a location to check aggregated weather.</p>
          </div>
        </div>
      </section>

      <!-- Bottom: Plant Recommendation Card -->
      <section class="container">
        <div class="section-box">
          <div class="panel-head">
            <div class="panel-title">Recommendation List</div>
            <div class="panel-actions">
              <span class="muted" v-if="point">For {{ point.lat.toFixed(2) }}, {{ point.lng.toFixed(2) }}</span>
            </div>
          </div>

          <!-- Statistics Bar -->
          <div class="list-toolbar" v-if="totalKnown">
            <div class="results-meta">
              Showing {{ startIndex }}–{{ endIndex }} of {{ total }} results
            </div>
          </div>

          <!-- Card Grid -->
          <div class="plants-grid">
            <template v-if="cardsLoading">
              <PlantCardSkeleton v-for="n in PAGE_SIZE" :key="'sk'+n" />
            </template>

            <p v-else-if="cardsError" class="error">Recommendations load failed: {{ cardsError }}</p>

            <template v-else>
              <RouterLink
                v-for="p in rcmdPlants"
                :key="`g-${p.general_plant_id}`"
                :to="toFor(p)"
                style="text-decoration: none;"
              >
                <PlantCard :plant="p" />
              </RouterLink>
            </template>
          </div>

          <!-- Pagination -->
          <div class="list-toolbar bottom" v-if="totalKnown && totalPages>1">
            <div class="pager">
              <button class="btn-ghost sm" :disabled="page<=1 || isRefreshing" @click="prevPage">‹ Prev</button>
              <span class="pager-num">Page</span>
              <input
                class="pager-input"
                type="number"
                :min="1"
                :max="totalPages"
                v-model.number="pageInput"
                @keyup.enter="goToPage(pageInput)"
                :disabled="isRefreshing"
              />
              <span>/ {{ totalPages }}</span>
              <button class="btn-ghost sm" :disabled="page>=totalPages || isRefreshing" @click="nextPage">Next ›</button>
            </div>
          </div>

          <!-- Empty state -->
          <p v-if="!cardsLoading && !cardsError && total===0" class="muted" style="margin-top:.5rem;">
            No recommendations yet. Please select a location and click the map.
          </p>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import 'leaflet/dist/leaflet.css'

import { getRecommendations } from '@/api/plantrcmd'
import { getPlantsForCardsByIds } from '@/api/plants'
import PlantCard from '@/components/PlantCard.vue'
import PlantCardSkeleton from '@/components/CardSkeleton.vue'

/* Map and points */
let leaflet = null
let map = null
let clickLayer = null
const mapEl = ref(null)

const point = ref(null)

const pendingPoint = ref(null)

/* Input box */
const latInput = ref('')
const lngInput = ref('')
const inputError = ref('')

/* Default coordinates: Melbourne CBD (-37.8136, 144.9631) */
const DEFAULT_POINT = { lat: -37.8136, lng: 144.9631 }

/* ========== KPI：aggregated_weather ========== */
const metrics = reactive({
  extreme_max_temp: null,
  extreme_min_temp: null,
  avg_sunshine_duration: null,
  avg_max_uv_index: null,
  avg_daily_precipitation: null,
  avg_relative_humidity: null
})
const kpiLoading = ref(false)
const kpiError = ref('')

const isRefreshing = ref(false)

/* KPI */
const kpiList = [
  { key: 'extreme_max_temp',        label: 'Extreme Max Temp',  format: v => v==null?'—':`${v.toFixed(1)}°C` },
  { key: 'extreme_min_temp',        label: 'Extreme Min Temp',  format: v => v==null?'—':`${v.toFixed(1)}°C` },
  { key: 'avg_sunshine_duration',   label: 'Avg Sunshine',      format: v => v==null?'—':`${v.toFixed(1)} h` },
  { key: 'avg_max_uv_index',        label: 'Avg Max UV',        format: v => v==null?'—':`${v.toFixed(1)}` },
  { key: 'avg_daily_precipitation', label: 'Avg Daily Precip',  format: v => v==null?'—':`${Math.round(v)} mm` },
  { key: 'avg_relative_humidity',   label: 'Avg Rel. Humidity', format: v => v==null?'—':`${v.toFixed(0)}%` },
]

/* ====== Recommended Card ====== */
const PAGE_SIZE = 8
const rcmdIds = ref([])
const total   = ref(0)
const page    = ref(1)
const pageInput = ref(1)

const cardsLoading = ref(false)
const cardsError   = ref('')
const rcmdPlants   = ref([])

const displayCoord = computed(() => pendingPoint.value || point.value)
const totalKnown = computed(() => total.value > 0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))
const startIndex = computed(() => total.value ? (page.value - 1) * PAGE_SIZE + 1 : 0)
const endIndex   = computed(() => total.value ? Math.min(total.value, page.value * PAGE_SIZE) : 0)

/* Pop-up switch and behavior */
const showCoordModal = ref(false)
function openCoordModal(){ showCoordModal.value = true }
function closeCoordModal(){ if(!isRefreshing.value) showCoordModal.value = false }
async function submitCoord(){
  await applyInputs()
  if (!inputError.value) closeCoordModal()
}

/* Press ESC to close the popup window */
function onKeydown(e){
  if(e.key === 'Escape' && showCoordModal.value){
    closeCoordModal()
  }
}

/* Widget: Safe to digital */
function toNum(x){ const n = Number(x); return Number.isFinite(n) ? n : null }

/* Detail routing (with from=rcmd, so that PlantDetail can return to the recommended page) */
function toFor(p){
  return {
    name: 'PlantDetail',
    params: { id: p.general_plant_id },
    query: { type: 'general', from: 'rcmd' },
    state: { preload: {
      general_plant_id: p.general_plant_id,
      threatened_plant_id: undefined,
      common_name: p.common_name || '',
      scientific_name: p.scientific_name || '',
      image_url: p.image_url || '',
      other_name: []
    } }
  }
}

/* Pull cards from rcmdIds slice based on page */
async function loadCards(){
  const ids = rcmdIds.value || []
  total.value = ids.length
  if (!ids.length){
    rcmdPlants.value = []
    return
  }

  cardsLoading.value = true
  cardsError.value   = ''
  try{
    const offset = (page.value - 1) * PAGE_SIZE
    const slice  = ids.slice(offset, offset + PAGE_SIZE)
    const simple = await getPlantsForCardsByIds(slice)
    rcmdPlants.value = simple.map(s => ([
      'general_plant_id','common_name','scientific_name','image_url'
    ].reduce((acc,k)=>{acc[k]=s[k]??(k==='image_url'?null:undefined);return acc},{ id_type:'general' })))
      .map(o=>({ ...o, id_type:'general' }))
  }catch(e){
    cardsError.value = e?.message || String(e)
    rcmdPlants.value = []
  }finally{
    cardsLoading.value = false
  }
}
function goToPage(p){
  const tp = totalPages.value
  const target = Math.min(Math.max(1, Number(p) || 1), tp)
  page.value = target
  pageInput.value = target
  loadCards()
}
function nextPage(){ goToPage(page.value + 1) }
function prevPage(){ goToPage(page.value - 1) }

/* —— Refresh: The backend returns the aggregated weather + recommendation ID at one time → reload the card —— */
async function refresh(){
  if (!point.value) return
  if (isRefreshing.value) return
  isRefreshing.value = true

  kpiLoading.value = true
  kpiError.value = ''
  cardsLoading.value = true
  cardsError.value = ''

  try{
    const { lat, lng } = point.value
    const bundle = await getRecommendations(lat, lng)

    // KPI
    const w =
      bundle?.aggregated_weather ||
      bundle?.weather ||
      bundle?.metrics ||
      bundle?.kpi ||
      {}
    metrics.extreme_min_temp        = toNum(w.extreme_min_temp ?? w.min_temp_c)
    metrics.extreme_max_temp        = toNum(w.extreme_max_temp ?? w.max_temp_c)
    metrics.avg_sunshine_duration   = toNum(w.avg_sunshine_duration ?? w.sun_hours_avg)
    metrics.avg_max_uv_index        = toNum(w.avg_max_uv_index ?? w.uv_index_max ?? w.uv_max ?? w.avg_uv_index)
    metrics.avg_daily_precipitation = toNum(w.avg_daily_precipitation ?? w.total_rain_mm ?? w.rain_avg_mm)
    metrics.avg_relative_humidity   = toNum(w.avg_relative_humidity ?? w.humidity_avg)

    // IDs
    const ids =
      (Array.isArray(bundle?.recommended_plant_ids) && bundle.recommended_plant_ids) ||
      (Array.isArray(bundle?.recommended_ids) && bundle.recommended_ids) ||
      (Array.isArray(bundle?.plant_ids) && bundle.plant_ids) ||
      (Array.isArray(bundle?.ids) && bundle.ids) || []

    rcmdIds.value = ids.map(n => Number(n)).filter(n => Number.isFinite(n) && n > 0)
    total.value   = Number(bundle?.total_recommendations ?? rcmdIds.value.length)

    page.value = 1
    pageInput.value = 1
    await loadCards()
  }catch(e){
    const msg = e?.message || String(e)
    kpiError.value = msg
    cardsError.value = msg
    rcmdIds.value = []
    rcmdPlants.value = []
    total.value = 0
  }finally{
    kpiLoading.value = false
    cardsLoading.value = false
    isRefreshing.value = false
  }
}

/* Map initialization (limited to Australia) */
onMounted(async () => {
  window.addEventListener('keydown', onKeydown)

  const L = await import('leaflet')
  leaflet = L

  const AUS_CENTER = { lat: -25.2744, lng: 133.7751 }
  const AUS_BOUNDS = L.latLngBounds(L.latLng(-48, 112), L.latLng(-10, 154))

  map = L.map(mapEl.value, {
    center: AUS_CENTER,
    zoom: 4,
    minZoom: 3,
    maxZoom: 12,
    maxBounds: AUS_BOUNDS,
    maxBoundsViscosity: 0.9,
    zoomControl: true,
    attributionControl: true
  })

  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap © CARTO'
  }).addTo(map)

  // Click on the map: directly submit coordinates and trigger a request; clicks are invalid before loading is complete
  map.on('click', async (e) => {
    if (isRefreshing.value) return
    inputError.value = ''
    const lat = +e.latlng.lat
    const lng = +e.latlng.lng
    // Use click coordinates directly: write to input box and submit
    latInput.value = lat.toFixed(4)
    lngInput.value = lng.toFixed(4)
    await applyInputs()
  })

  // Preset to Melbourne CBD and automatically submit once
  setPending(DEFAULT_POINT.lat, DEFAULT_POINT.lng, true)
  latInput.value = DEFAULT_POINT.lat.toFixed(4)
  lngInput.value = DEFAULT_POINT.lng.toFixed(4)
  await applyInputs()
})

onBeforeUnmount(() => {
  if (map) { map.remove(); map = null }
  window.removeEventListener('keydown', onKeydown)
})

/* Application input: check → submit as point → request */
async function applyInputs(){
  inputError.value = ''
  const lat = Number(latInput.value)
  const lng = Number(lngInput.value)
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) { inputError.value = 'Please input valid coordinates.'; return }
  if (lat < -90 || lat > 90 || lng < -180 || lng > 180) { inputError.value = 'Invalid coordinates.（lat -90~90，lon -180~180）'; return }
  if (lat < -48 || lat > -10 || lng < 112 || lng > 154) { inputError.value = 'Coordinates are not in Austrilia'; return }

  // Submit: Update map marker + set to submitted coordinates + request
  setMarker(lat, lng)
  pendingPoint.value = { lat, lng }
  point.value = { lat, lng }
  await refresh()
}

/* Clear: remove mark, clear input, reset all data */
function clearAll(){
  inputError.value = ''
  latInput.value = ''
  lngInput.value = ''
  pendingPoint.value = null
  point.value = null
  if (clickLayer) { clickLayer.remove(); clickLayer = null }
  // Reset KPI & recommendations
  metrics.extreme_max_temp = metrics.extreme_min_temp = null
  metrics.avg_sunshine_duration = metrics.avg_max_uv_index = null
  metrics.avg_daily_precipitation = metrics.avg_relative_humidity = null
  kpiError.value = ''
  cardsError.value = ''
  rcmdIds.value = []
  rcmdPlants.value = []
  total.value = 0
  page.value = 1
  pageInput.value = 1
  isRefreshing.value = false
}

/* Only set coordinates + map markers to be submitted (no request) */
function setPending(lat, lng, panTo){
  pendingPoint.value = { lat, lng }
  setMarker(lat, lng)
  if (panTo && map) map.setView([lat, lng], Math.max(6, map.getZoom()))
}

/* Set map marker (reuse) */
function setMarker(lat, lng){
  if (!map) return
  if (clickLayer) clickLayer.remove()
  clickLayer = leaflet.circleMarker([lat, lng], {
    radius: 8, color: '#2b8a3e', fillColor: '#2b8a3e', fillOpacity: .9, weight: 2
  }).addTo(map)
}

/* —— KPI color —— */
function kpiStyle(key){
  const v = metrics[key]
  if (v == null) return {}
  let c = ''
  switch (key) {
    case 'extreme_max_temp':
      c = v >= 38 ? '#e03131' : v >= 30 ? '#f08c00' : v >= 22 ? '#fab005' : '#2f9e44'
      break
    case 'extreme_min_temp':
      c = v <= 0 ? '#1c7ed6' : v <= 5 ? '#4dabf7' : v <= 12 ? '#82c91e' : '#2f9e44'
      break
    case 'avg_max_uv_index':
      c = v >= 11 ? '#d6336c' : v >= 8 ? '#e8590c' : v >= 6 ? '#f76707' : v >= 3 ? '#fab005' : '#2f9e44'
      break
    case 'avg_daily_precipitation':
      c = v >= 8 ? '#1864ab' : v >= 4 ? '#228be6' : v >= 1 ? '#74c0fc' : '#868e96'
      break
    case 'avg_relative_humidity':
      c = v >= 85 ? '#1971c2' : v >= 65 ? '#339af0' : v >= 40 ? '#2f9e44' : '#fab005'
      break
    case 'avg_sunshine_duration':
      c = v >= 10 ? '#e67700' : v >= 7 ? '#fab005' : v >= 4 ? '#fcc419' : '#868e96'
      break
  }
  return {
    '--kpi-color': c
  }
}
</script>

<style scoped>
.twocol{
  display: grid;
  grid-template-columns: 8fr 2fr;
  gap: 26px;
}
@media (max-width: 900px){
  .twocol{ grid-template-columns: 1fr; }
}

.section-box{
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  background: transparent;
}

.panel-head{ display:flex; align-items:center; justify-content:space-between; gap:.75rem; margin-bottom:10px; }
.panel-title{ font-weight: 700; text-align: center;}
.coords{ display:flex; gap:10px; color: var(--muted); }

.weather-box{
  border: 2px solid color-mix(in oklab, var(--fg) 14%, transparent);
  background:
    linear-gradient(135deg,
      color-mix(in oklab, var(--fg) 6%, transparent) 0%,
      transparent 60%);
  box-shadow: var(--shadow-sm);
  transition: border-color .2s ease;
}
.weather-box:hover{
  border-color: color-mix(in oklab, var(--fg) 24%, transparent);
}

.coordbar{
  display: flex; gap: 8px; align-items: center; margin-bottom: 10px; flex-wrap: wrap;
}
.coord-input{
  width: 220px; height: 40px;
  border: 1px solid var(--border); border-radius: 10px; padding: 0 12px;
  background: var(--surface); color: var(--fg);
  outline: none;
}
.coord-input:focus-visible{ outline: var(--ring); box-shadow: none; }
.btn{
  height: 40px; padding: 0 14px; border-radius: 10px;
  border: 1px solid var(--border); background: var(--card); color: var(--fg);
  cursor: pointer; box-shadow: var(--shadow-sm);
}
.btn:hover{ background: var(--hover); }
.btn.sm{ height: 32px; padding: 0 12px; border-radius: 8px; }
.btn.ghost{ background: transparent; }

.map-wrap { position: relative; z-index: 0; }
.map{
  position: relative; z-index: 0;
  width: 100%; height: 510px;
  border-radius: 12px; border: 1px solid var(--border);
  overflow: hidden; background: var(--surface);
}
.map-hint{
  position: absolute; inset: auto 10px 10px auto;
  background: color-mix(in oklab, var(--bg) 80%, transparent);
  border: 1px dashed color-mix(in oklab, var(--fg) 20%, transparent);
  border-radius: 10px; padding: 6px 10px; color: var(--muted);
}
:deep(.leaflet-container),
:deep(.leaflet-pane),
:deep(.leaflet-control-container){
  z-index: 0 !important;
}

.kpi-grid.two-col{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 25px;
}
.kpi{ text-align:center; }

.kpi-circle{
  width:70px; height:70px; margin:0 auto;
  border-radius: 50%;
  border: 2px solid var(--kpi-color, var(--border));
  display:grid; place-items:center;
  background:
    radial-gradient(circle at 50% 38%,
      color-mix(in oklab, var(--kpi-color, var(--fg)) 18%, transparent),
      transparent 60%),
    var(--card);
  box-shadow:
    0 0 0 4px color-mix(in oklab, var(--kpi-color, var(--fg)) 15%, transparent),
    var(--shadow-sm);
  transition: box-shadow .2s ease, transform .1s ease;
}
.kpi-circle:hover{ transform: translateY(-1px); box-shadow:
    0 0 0 6px color-mix(in oklab, var(--kpi-color, var(--fg)) 18%, transparent),
    var(--shadow-sm); }
.kpi-value{ font-weight: 700; line-height:1; }
.kpi-label{
  margin-top: 6px;
  color: color-mix(in oklab, var(--kpi-color, var(--fg)) 40%, var(--muted));
  font-weight: 600;
}

.list-toolbar{ display:flex; align-items:center; justify-content:space-between; gap:.75rem; margin: .5rem 0 1rem; }
.list-toolbar.bottom{ margin-top: 1rem; justify-content: center; }
.results-meta{ color: var(--muted); }
.pager{ display:flex; align-items:center; gap:.5rem; }
.pager .btn-ghost.sm{
  padding: .35rem .6rem; border-radius: 999px; border: 1px solid color-mix(in oklab, var(--fg) 20%, transparent); background: transparent; color: var(--fg);
}
.pager .btn-ghost.sm:disabled{ opacity:.5; cursor:not-allowed; }
.pager-input{ width: 3.5rem; height: 32px; padding: 0 .5rem; border-radius: 8px; border: 1px solid var(--border); background: var(--card); color: var(--fg); }
.pager-num{ color: var(--muted); }

.plants-grid { display: grid; gap: 1rem; grid-template-columns: repeat(4, 1fr); }
@media (max-width: 768px) { .plants-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .plants-grid { grid-template-columns: 1fr; } }

.muted{ color: var(--muted); }
.error{ color:#c00; margin-top:8px }

.modal-overlay{
  position: fixed; inset: 0;
  background: color-mix(in oklab, var(--bg) 65%, black 30%);
  backdrop-filter: blur(2px);
  display: grid; place-items: center;
  z-index: 1000;
}
.modal{
  width: min(680px, 92vw);
  background: var(--card);
  color: var(--fg);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
}
.modal-head{ display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
.modal-title{ font-weight: 700; }
.btn.icon{
  width: 40px; height: 30px; ;
  display:grid; place-items:center; font-size: 20px; line-height: 1;
}
</style>
