<!-- src/views/PlantRcmd.vue -->
<template>
  <!-- 顶部简介 -->
  <section class="container" id="plantrcmd">
    <div class="section-box">
      <h2>Plant Recommendation</h2>
      <p>Choose a location on map to see plant recommendations and aggregated weather for the area.</p>

      <!-- 地图和天气 -->
      <section class="container">
        <div class="twocol">
          <!-- 左：地图与坐标输入 -->
          <div class="section-box">
            <div class="panel-head">
              <div class="panel-title">Select Location (Australia)</div>
              <div class="coords" v-if="displayCoord">
                <span>Lat: {{ displayCoord.lat.toFixed(4) }}</span>
                <span>Lon: {{ displayCoord.lng.toFixed(4) }}</span>
                <span class="muted" v-if="pendingPoint && !point">（UnSubmited）</span>
              </div>
            </div>

            <div class="coordbar">
              <input
                class="coord-input"
                type="number"
                step="0.01"
                placeholder="Latitude (e.g. -33.8688)"
                v-model="latInput"
                @keyup.enter="applyInputs"
              />
              <input
                class="coord-input"
                type="number"
                step="0.01"
                placeholder="Longitude (e.g. 151.2093)"
                v-model="lngInput"
                @keyup.enter="applyInputs"
              />
              <button class="btn" @click="applyInputs" :disabled="!latInput || !lngInput">Search / Recommend</button>
              <button class="btn ghost" @click="clearAll" :disabled="!latInput && !lngInput && !point && !pendingPoint">Clear</button>
            </div>
            <p v-if="inputError" class="error">{{ inputError }}</p>

            <div class="map-wrap">
              <div ref="mapEl" class="map" role="application" aria-label="Australia map (click to select)"></div>
              <div v-if="!pendingPoint && !point" class="map-hint">Point a map location / type in coordinates.</div>
            </div>
          </div>

          <!-- 右：天气 KPI -->
          <div class="section-box">
            <div class="panel-head">
              <div class="panel-title">16-Day Aggregated Weather</div>
            </div>

            <div class="kpi-grid two-col">
              <div class="kpi" v-for="m in kpiList" :key="m.key">
                <div class="kpi-circle" :aria-busy="kpiLoading">
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

      <!-- 底部：植物推荐卡片（与 PlantSearch 一致风格） -->
      <section class="container">
        <div class="section-box">
          <div class="panel-head">
            <div class="panel-title">Recommendation List</div>
            <div class="panel-actions">
              <span class="muted" v-if="point">For {{ point.lat.toFixed(2) }}, {{ point.lng.toFixed(2) }}</span>
            </div>
          </div>

          <!-- 统计条 -->
          <div class="list-toolbar" v-if="totalKnown">
            <div class="results-meta">
              Showing {{ startIndex }}–{{ endIndex }} of {{ total }} results
            </div>
          </div>

          <!-- 卡片网格 -->
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

          <!-- 分页 -->
          <div class="list-toolbar bottom" v-if="totalKnown && totalPages>1">
            <div class="pager">
              <button class="btn-ghost sm" :disabled="page<=1" @click="prevPage">‹ Prev</button>
              <span class="pager-num">Page</span>
              <input
                class="pager-input"
                type="number"
                :min="1"
                :max="totalPages"
                v-model.number="pageInput"
                @keyup.enter="goToPage(pageInput)"
              />
              <span>/ {{ totalPages }}</span>
              <button class="btn-ghost sm" :disabled="page>=totalPages" @click="nextPage">Next ›</button>
            </div>
          </div>

          <!-- 空态 -->
          <p v-if="!cardsLoading && !cardsError && total===0" class="muted" style="margin-top:.5rem;">
            No recommendations yet. Please select a location and click "Use Coordinates".
          </p>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import 'leaflet/dist/leaflet.css'

import { getRecommendations } from '@/api/plantrcmd'     // GET：后端聚合天气 + 推荐 IDs
import { getPlantsForCardsByIds } from '@/api/plants'    // 批量按 ID 取卡片信息
import PlantCard from '@/components/PlantCard.vue'
import PlantCardSkeleton from '@/components/CardSkeleton.vue'

/* 地图与点位 */
let leaflet = null
let map = null
let clickLayer = null
const mapEl = ref(null)

/** 提交后的坐标（真正用于请求） */
const point = ref(null)
/** 待提交的坐标（地图点击或输入变化） */
const pendingPoint = ref(null)

/* 输入框 */
const latInput = ref('')
const lngInput = ref('')
const inputError = ref('')

/* ✅ 预设默认坐标：墨尔本 CBD（-37.8136, 144.9631） */
const DEFAULT_POINT = { lat: -37.8136, lng: 144.9631 }

/* ========== KPI：直接使用后端 aggregated_weather ========== */
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

/* KPI 显示（不改样式） */
const kpiList = [
  { key: 'extreme_max_temp',        label: 'Extreme Max Temp',  format: v => v==null?'—':`${v.toFixed(1)}°C` },
  { key: 'extreme_min_temp',        label: 'Extreme Min Temp',  format: v => v==null?'—':`${v.toFixed(1)}°C` },
  { key: 'avg_sunshine_duration',   label: 'Avg Sunshine',      format: v => v==null?'—':`${v.toFixed(1)} h` },
  { key: 'avg_max_uv_index',        label: 'Avg Max UV',        format: v => v==null?'—':`${v.toFixed(1)}` },
  { key: 'avg_daily_precipitation', label: 'Avg Daily Precip',  format: v => v==null?'—':`${Math.round(v)} mm` },
  { key: 'avg_relative_humidity',   label: 'Avg Rel. Humidity', format: v => v==null?'—':`${v.toFixed(0)}%` },
]

/* ====== 推荐卡片（与 PlantSearch 卡一致） ====== */
const PAGE_SIZE = 8
const rcmdIds = ref([])            // 后端返回的推荐ID全集
const total   = ref(0)
const page    = ref(1)
const pageInput = ref(1)

const cardsLoading = ref(false)
const cardsError   = ref('')
const rcmdPlants   = ref([])       // PlantCardItem[]

const displayCoord = computed(() => pendingPoint.value || point.value)
const totalKnown = computed(() => total.value > 0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))
const startIndex = computed(() => total.value ? (page.value - 1) * PAGE_SIZE + 1 : 0)
const endIndex   = computed(() => total.value ? Math.min(total.value, page.value * PAGE_SIZE) : 0)

/* 小工具：安全转数字 */
function toNum(x){ const n = Number(x); return Number.isFinite(n) ? n : null }

/* 详情路由定位（带 from=rcmd，便于 PlantDetail 返回推荐页） */
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

/* 根据 page 从 rcmdIds 切片拉取卡片 */
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
    const simple = await getPlantsForCardsByIds(slice) // [{general_plant_id, common_name,...}]
    rcmdPlants.value = simple.map(s => ({
      id_type: 'general',
      general_plant_id: s.general_plant_id,
      common_name: s.common_name,
      scientific_name: s.scientific_name,
      image_url: s.image_url || null
    }))
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

/* —— 刷新：后端一次性返回聚合天气 + 推荐ID → 再加载卡片 —— */
async function refresh(){
  if (!point.value) return
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
  }
}

/* 地图初始化（限制澳大利亚范围） */
onMounted(async () => {
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

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map)

  // 点击地图：只设置“待提交”的坐标与标记，不请求
  map.on('click', (e) => {
    inputError.value = ''
    const lat = +e.latlng.lat
    const lng = +e.latlng.lng
    setPending(lat, lng, true)
    latInput.value = lat.toFixed(4)
    lngInput.value = lng.toFixed(4)
  })

  // ✅ 预设到墨尔本 CBD，并自动提交一次（如只想预填不请求，注释掉 applyInputs()）
  setPending(DEFAULT_POINT.lat, DEFAULT_POINT.lng, true) // 放置标记并移动镜头
  latInput.value = DEFAULT_POINT.lat.toFixed(4)
  lngInput.value = DEFAULT_POINT.lng.toFixed(4)
  applyInputs()  // 触发请求与列表加载
})

onBeforeUnmount(() => { if (map) { map.remove(); map = null } })

/* 应用输入：校验 → 提交为 point → 请求 */
function applyInputs(){
  inputError.value = ''
  const lat = Number(latInput.value)
  const lng = Number(lngInput.value)
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) { inputError.value = 'Please input valid coordinates.'; return }
  if (lat < -90 || lat > 90 || lng < -180 || lng > 180) { inputError.value = 'Invalid coordinates.（lat -90~90，lon -180~180）'; return }
  if (lat < -48 || lat > -10 || lng < 112 || lng > 154) { inputError.value = 'Coordinates are not in Austrilia'; return }

  // 提交：更新地图标记 + 设置为已提交坐标 + 请求
  setMarker(lat, lng)
  pendingPoint.value = { lat, lng }
  point.value = { lat, lng }
  refresh()
}

/* 清空：移除标记、清空输入、重置所有数据 */
function clearAll(){
  inputError.value = ''
  latInput.value = ''
  lngInput.value = ''
  pendingPoint.value = null
  point.value = null
  if (clickLayer) { clickLayer.remove(); clickLayer = null }
  // 重置 KPI & 推荐
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
}

/* 仅设置待提交坐标 + 地图标记（不请求） */
function setPending(lat, lng, panTo){
  pendingPoint.value = { lat, lng }
  setMarker(lat, lng)
  if (panTo && map) map.setView([lat, lng], Math.max(6, map.getZoom()))
}

/* 设置地图标记（复用） */
function setMarker(lat, lng){
  if (!map) return
  if (clickLayer) clickLayer.remove()
  clickLayer = leaflet.circleMarker([lat, lng], {
    radius: 8, color: '#2b8a3e', fillColor: '#2b8a3e', fillOpacity: .9, weight: 2
  }).addTo(map)
}
</script>

<style scoped>
/* ====== 你原有样式，未改动 ====== */
.twocol{
  display: grid;
  grid-template-columns: 8fr 2fr;
  gap: 16px;
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

/* 坐标输入条 */
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
.btn.ghost{
  background: transparent;
}

/* 地图不覆盖导航：建立堆叠上下文并降低 Leaflet 层级 */
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

/* KPI：右侧 30% 宽区域，两列栅格向下排布 */
.kpi-grid.two-col{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.kpi{ text-align:center; }
.kpi-circle{
  width:70px; height:70px; margin:0 auto;
  border-radius: 50%;
  border: 2px solid var(--border);
  display:grid; place-items:center;
  background: var(--card);
  box-shadow: var(--shadow-sm);
}
.kpi-value{ font-weight: 700; }
.kpi-label{ margin-top: 6px; color: var(--muted); }

/* ====== 卡片区样式（与 PlantSearch 保持一致） ====== */
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

/* 你原有的通用状态色 */
.muted{ color: var(--muted); }
.error{ color:#c00; margin-top:8px }
</style>
