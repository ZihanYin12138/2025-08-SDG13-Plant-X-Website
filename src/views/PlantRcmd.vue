<!-- src/views/PlantRcmd.vue -->
<template>
  <!-- 顶部简介 -->
  <section class="container" id="plantrcmd">
  <div class="section-box">
    <h2>Plant Recommendation</h2>
    <p>Choose a location to see plant recommendations and aggregated weather for the area.</p>

  <!-- 地图和天气 -->
  <section class="container">
    <div class="twocol">
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
          <button class="btn" @click="applyInputs" :disabled="!latInput || !lngInput">Use Coordinates</button>
          <button class="btn ghost" @click="clearAll" :disabled="!latInput && !lngInput && !point && !pendingPoint">Clear</button>
        </div>
        <p v-if="inputError" class="error">{{ inputError }}</p>

        <div class="map-wrap">
          <div ref="mapEl" class="map" role="application" aria-label="Australia map (click to select)"></div>
          <div v-if="!pendingPoint && !point" class="map-hint">Point a map location / type in coordinates.</div>
        </div>

      </div>

      <!-- 右：天气 KPI（2 列一行，向下排列；仅提交后可刷新） -->
      <div class="section-box">
        <div class="panel-head">
          <div class="panel-title">16-Day Aggregated Weather</div>
          <!-- <button class="btn sm" :disabled="!point || kpiLoading" @click="refresh">
            {{ kpiLoading ? 'Loading…' : 'Refresh' }}
          </button> -->
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

  <!-- 底部：植物推荐表 -->
  <section class="container">
    <div class="section-box">
      <div class="panel-head">
        <div class="panel-title">Recommendation List</div>
        <div class="panel-actions">
          <span class="muted" v-if="point">For {{ point.lat.toFixed(2) }}, {{ point.lng.toFixed(2) }}</span>
        </div>
      </div>

      <div class="table-wrap">
        <table class="rcmd-table" v-if="!rcmdLoading && !rcmdError && recommendations.length">
          <thead>
            <tr>
              <th style="width:28%">Plant</th>
              <th>Type</th>
              <th>Sun</th>
              <th>Watering</th>
              <th>Fit Score</th>
              <th>Rationale</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in recommendations" :key="r.id ?? (r.common_name + r.scientific_name)">
              <td>
                <RouterLink
                  v-if="r.id"
                  :to="{ name: 'PlantDetail', params: { id: r.id }, query: { type: r.id_type || 'general' }, state: { preload: r } }"
                >
                  {{ r.common_name || r.scientific_name || '—' }}
                </RouterLink>
                <span v-else>{{ r.common_name || r.scientific_name || '—' }}</span>
              </td>
              <td>{{ r.category || r.type || '—' }}</td>
              <td>{{ r.sun || '—' }}</td>
              <td>{{ r.watering || '—' }}</td>
              <td><strong>{{ fmtScore(r.fit_score) }}</strong></td>
              <td class="reason">{{ r.reason || r.explanation || '—' }}</td>
            </tr>
          </tbody>
        </table>

        <div v-else-if="rcmdLoading" class="skeleton-table">
          <div v-for="i in 6" :key="i" class="row">
            <span class="cell w30"></span><span class="cell w10"></span><span class="cell w10"></span>
            <span class="cell w10"></span><span class="cell w10"></span><span class="cell w30"></span>
          </div>
        </div>

        <p v-else-if="rcmdError" class="error">Recommendations load failed: {{ rcmdError }}</p>
        <p v-else class="muted">No recommendations yet. Please select a location and click "Use Coordinates" to see recommendations.</p>
      </div>
    </div>
  </section>

  </div>

  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import 'leaflet/dist/leaflet.css'
import { postCoordinates } from '@/api/plantrcmd'
import { getPlantById } from '@/api/plants'

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

/* KPI */
const metrics = reactive({
  max_temp_c: null,
  min_temp_c: null,
  avg_temp_c: null,
  total_rain_mm: null,
  sun_hours_avg: null,
  wind_kph_avg: null
})
const kpiLoading = ref(false)
const kpiError = ref('')
const kpiList = [
  { key: 'max_temp_c',    label: 'Max Temp',     format: v => v==null?'—':`${v.toFixed(1)}°C` },
  { key: 'min_temp_c',    label: 'Min Temp',     format: v => v==null?'—':`${v.toFixed(1)}°C` },
  { key: 'avg_temp_c',    label: 'Avg Temp',     format: v => v==null?'—':`${v.toFixed(1)}°C` },
  { key: 'total_rain_mm', label: 'Rainfall',     format: v => v==null?'—':`${Math.round(v)} mm` },
  { key: 'sun_hours_avg', label: 'Sun Duration', format: v => v==null?'—':`${v.toFixed(1)} h` },
  { key: 'wind_kph_avg',  label: 'Wind',         format: v => v==null?'—':`${v.toFixed(1)} kph` },
]

/* 推荐（沿用你原表格结构） */
const recommendations = ref([])
const rcmdLoading = ref(false)
const rcmdError = ref('')

const displayCoord = computed(() => pendingPoint.value || point.value)

function fmtScore(s){ return (typeof s === 'number') ? s.toFixed(0) : (s ?? '—') }

/* —— 一次 POST：拿天气 + 推荐ID，再按 ID 拉详情并映射到表格 —— */
async function refresh () {
  if (!point.value) return
  kpiLoading.value = true
  rcmdLoading.value = true
  kpiError.value = ''
  rcmdError.value = ''
  try {
    const bundle = await postCoordinates(point.value.lat, point.value.lng)

    // weather 兼容映射
    const w = bundle.weather || {}
    metrics.max_temp_c    = toNum(w.max_temp_c ?? w.maxTempC)
    metrics.min_temp_c    = toNum(w.min_temp_c ?? w.minTempC)
    metrics.avg_temp_c    = toNum((w.avg_temp_c ?? w.avgTempC) ?? avg([w.max_temp_c ?? w.maxTempC, w.min_temp_c ?? w.minTempC]))
    metrics.total_rain_mm = toNum(w.total_rain_mm ?? w.rain_mm ?? w.totalRainMm)
    metrics.sun_hours_avg = toNum(w.sun_hours_avg ?? w.sun_hours ?? w.sunHours)
    metrics.wind_kph_avg  = toNum(w.wind_kph_avg ?? w.wind_kph ?? w.windKph)

    // 推荐ID + 可选元信息（理由/分数）
    const ids =
      (Array.isArray(bundle.recommended_ids) && bundle.recommended_ids) ||
      (Array.isArray(bundle.plant_ids) && bundle.plant_ids) ||
      (Array.isArray(bundle.ids) && bundle.ids) || []

    const metaList =
      (Array.isArray(bundle.items) && bundle.items) ||
      (Array.isArray(bundle.recommendations) && bundle.recommendations) || []

    const metaMap = new Map()
    for (const m of metaList) {
      const mid = m?.id ?? m?.plant_id ?? m?.general_plant_id
      if (mid != null) metaMap.set(Number(mid), m)
    }

    // 拉详情并映射到表格字段
    const details = await Promise.all(
      ids.map(id => getPlantById(id).catch(() => null))
    )
    recommendations.value = details.filter(Boolean).map(d => {
      const id = d.general_plant_id ?? d.id ?? d.plant_id
      const meta = metaMap.get(Number(id)) || {}
      return {
        id,
        id_type: 'general',
        common_name: d.common_name || '',
        scientific_name: d.scientific_name || '',
        category: d.category || d.type || '',
        sun: d.sunlight || d.sun_exposure || d.sun || '',
        watering: d.watering || '',
        fit_score: toNum(meta.fit_score ?? meta.score ?? meta.rank),
        reason: meta.reason || meta.explanation || ''
      }
    })
  } catch (e) {
    const msg = e && e.message ? e.message : String(e)
    kpiError.value = msg
    rcmdError.value = msg
    Object.keys(metrics).forEach(k => (metrics[k] = null))
    recommendations.value = []
  } finally {
    kpiLoading.value = false
    rcmdLoading.value = false
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
  // 重置 KPI & 推荐 & 错误
  Object.keys(metrics).forEach(k=> (metrics[k]=null))
  kpiError.value = ''
  rcmdError.value = ''
  recommendations.value = []
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

/* 小工具 */
function toNum(x){ const n = Number(x); return Number.isFinite(n) ? n : null }
function avg(arr){ const ns = arr.map(toNum).filter(n=>Number.isFinite(n)); return ns.length? ns.reduce((a,b)=>a+b,0)/ns.length : null }
</script>


<style scoped>
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

/* 推荐表 */
.table-wrap{ margin-top: 8px; }
.rcmd-table{ width: 100%; border-collapse: collapse; }
.rcmd-table th, .rcmd-table td{
  text-align: left; padding: 10px; border-bottom: 1px solid var(--border);
  vertical-align: top;
}
.rcmd-table thead th{ color: var(--muted); font-weight: 600; }
.reason{ color: var(--muted); }

/* Skeleton & 状态 */
.skeleton-table .row{ display:flex; gap: 8px; padding: 10px 0; border-bottom: 1px solid var(--border); }
.skeleton-table .cell{
  display:inline-block; height: 14px; border-radius: 6px; background: var(--surface);
  animation: pulse 1.2s ease-in-out infinite;
}
.w30{ width:30%; } .w10{ width:10%; }
@keyframes pulse{ 0%,100%{opacity:.6} 50%{opacity:1} }

.muted{ color: var(--muted); }
.error{ color:#c00; margin-top:8px }
</style>
