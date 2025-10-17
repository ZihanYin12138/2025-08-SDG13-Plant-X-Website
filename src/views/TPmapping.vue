<template>
  <section>
    <div class="container">
      <h2>Explore Threatened Plants Across Australia</h2>
      <p>
        Discover where Australia’s threatened plants live.
        <br />Filter by state—the map and list update instantly. Click a marker or card for details and ways to help.
      </p>
    </div>
    <div class="tp-wrapper">
      <div class="map-wrap">
        <div id="tp-map" class="map"></div>
      </div>
      <aside class="side">
        <header class="side-header">
          <select v-model="selectedState" class="state-select" aria-label="Filter by state">
            <option value="__ALL__">All states</option>
            <option v-for="s in states" :key="s" :value="s">{{ s }}</option>
          </select>
          <div class="count">Found {{ filteredCards.length }} plants</div>
        </header>
        <section class="card-list" v-if="!loading">
          <article v-for="p in filteredCards" :key="p.id" class="plant-card" role="button" tabindex="0"
            @click="openDetail(p.id)" @keyup.enter="openDetail(p.id)" @keyup.space.prevent="openDetail(p.id)">
            <div class="thumb" :style="{ backgroundImage: `url(${PLACEHOLDER})` }" />
            <div class="meta">
              <h3 class="common">{{ p.commonName || humanize(p.binomial) }}</h3>
              <div class="binomial">{{ humanize(p.binomial) }}</div>
              <div class="row">
                <span class="badge" :class="badgeClass(p.maxStatus)">{{ p.maxStatus || 'Unknown' }}</span>
                <span class="region">{{ p.state }}</span>
              </div>
            </div>
          </article>
          <div v-if="filteredCards.length === 0" class="empty">No plants for this state.</div>
        </section>
        <section v-else class="skeleton">
          <div class="sk-item" v-for="i in 6" :key="i"></div>
        </section>
      </aside>
      <transition name="fade">
        <div v-if="detail.show" class="modal-mask" @click.self="closeDetail"
          style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 9999;">
          <div class="modal" role="dialog" aria-modal="true">
            <button class="modal-close" aria-label="Close" @click="closeDetail">×</button>
            <div v-if="detail.loading" class="modal-loading">
              <div class="spinner"></div>
              <div>Loading plant detail…</div>
            </div>
            <template v-else>
              <header class="modal-head">
                <div class="modal-title">
                  <h2>{{ detailTitle }}</h2>
                  <div class="sub">{{ humanize(detail.data?.taxonomy?.binomial || detail.data?.binomial) }}</div>
                  <div class="tags">
                    <span class="badge" :class="badgeClass(detailStatus)">
                      {{ detailStatus || 'Unknown' }}
                    </span>
                    <span class="chip" v-if="detail.data?.id">ID: {{ detail.data.id }}</span>
                    <span class="chip" v-if="detail.data?.conservation?.iucnStatus || detail.data?.iucnStatus">
                      IUCN: {{ detail.data?.conservation?.iucnStatus || detail.data?.iucnStatus }}
                    </span>
                  </div>
                </div>
              </header>
              <section class="modal-body">
                <div class="info-grid-2col">
                  <div class="info">
                    <div class="label">State</div>
                    <div class="value">{{ detailState }}</div>
                  </div>
                  <div class="info">
                    <div class="label">Region</div>
                    <div class="value">{{ detailRegion }}</div>
                  </div>
                  <div class="info">
                    <div class="label">Latitude</div>
                    <div class="value">{{ coordOrDash('lat') }}</div>
                  </div>
                  <div class="info">
                    <div class="label">Longitude</div>
                    <div class="value">{{ coordOrDash('lng') }}</div>
                  </div>
                </div>
                <p class="desc" v-if="detailDescription" v-text="detailDescription"></p>
                <p class="desc empty" v-else>No description provided.</p>
                <section class="related" v-if="relatedTop10.length">
                  <h3 class="rel-title">Related plants</h3>
                  <div class="rel-list">
                    <button v-for="rp in relatedTop10" :key="rp.id" class="rel-card" @click="openDetail(rp.id)">
                      <div class="rel-name" :title="rp.commonName || humanize(rp.binomial)">
                        {{ rp.commonName || humanize(rp.binomial) }}
                      </div>
                      <div class="rel-meta">
                        <div class="rel-line">State: {{ rp.state || '—' }}</div>
                        <div class="rel-line">Region: {{ rp.region || '—' }}</div>
                        <div class="rel-line">ID: {{ rp.id }}</div>
                        <div class="rel-line">
                          Status:
                          <span class="badge small" :class="badgeClass(rp.maxStatus || rp.epbcStatus)">
                            {{ rp.maxStatus || rp.epbcStatus || 'Unknown' }}
                          </span>
                        </div>
                      </div>
                    </button>
                  </div>
                </section>
                <div class="btns">
                  <button class="btn" @click="viewOnMap(detail.id)">View on map</button>
                  <button class="btn outline" @click="closeDetail">Close</button>
                </div>
              </section>
            </template>
          </div>
        </div>
      </transition>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { getAllPlantsList, getPlantsMapData, getPlantDetail } from '@/api/tpmap'
import placeholder from '@/assets/placeholder.jpg'
const PLACEHOLDER = placeholder
const loading = ref(true)
const selectedState = ref('__ALL__')
const allPlants = ref([])
const mapPlants = ref([])
const states = ref([])
let map, markersLayer, focusRing
const idToMarker = new Map()
const detail = ref({ show: false, loading: false, id: null, data: null, error: null })
const humanize = (s) => (s || '').replaceAll('_', ' ')
const badgeClass = (status) => {
  const s = (status || '').toLowerCase()
  return { 'badge--ce': s === 'critically endangered', 'badge--en': s === 'endangered', 'badge--vu': s === 'vulnerable' }
}
const statusColor = (status) => {
  switch ((status || '').toLowerCase()) {
    case 'critically endangered': return '#ff3b30'
    case 'endangered': return '#ff6b00'
    case 'vulnerable': return '#f3b300'
    default: return '#6b7280'
  }
}
const unionPoints = computed(() => {
  const byId = new Map()
    ; (mapPlants.value || []).forEach(p => {
      if (p?.latitude != null && p?.longitude != null) byId.set(String(p.id), { ...p })
    })
    ; (allPlants.value || []).forEach(p => {
      if (p?.latitude == null || p?.longitude == null) return
      const key = String(p.id)
      if (!byId.has(key)) {
        byId.set(key, {
          ...p,
          markerColor: statusColor(p.maxStatus),
          popupContent: `
          <strong>${humanize(p.binomial)}</strong><br/>
          Status: ${p.maxStatus || ''}<br/>
          Region: ${p.region || ''}`
        })
      }
    })
  return Array.from(byId.values())
})
const filteredCards = computed(() => {
  if (selectedState.value === '__ALL__') return allPlants.value
  return allPlants.value.filter(p => p.state === selectedState.value)
})
const filteredMapPoints = computed(() => {

  return unionPoints.value
})
const detailStatus = computed(() =>
  detail.value?.data?.conservation?.maxStatus ||
  detail.value?.data?.maxStatus ||
  detail.value?.data?.conservation?.epbcStatus ||
  detail.value?.data?.epbcStatus ||
  ''
)
const detailTitle = computed(() => {
  const d = detail.value?.data
  const cn = d?.taxonomy?.commonName || d?.commonName
  const bn = humanize(d?.taxonomy?.binomial || d?.binomial || '')
  return cn || bn || 'Plant detail'
})
const detailDescription = computed(() => detail.value?.data?.description || '')
const detailState = computed(() => detail.value?.data?.location?.state || detail.value?.data?.state || '—')
const detailRegion = computed(() => detail.value?.data?.location?.region || detail.value?.data?.region || '—')
const relatedPlants = computed(() => {
  const d = detail.value.data
  if (!d || !Array.isArray(d.relatedPlants)) return []
  const currentId = String(d.id ?? d.plantId ?? '')
  const enrich = (r) => {
    const id = String(r.id)
    const fromList =
      allPlants.value.find(x => String(x.id) === id) ||
      unionPoints.value.find(x => String(x.id) === id) || {}
    return {
      ...fromList,
      ...r,
      maxStatus: r.maxStatus || fromList.maxStatus,
      epbcStatus: r.epbcStatus || fromList.epbcStatus,
      state: r.state || fromList.state,
      region: r.region || fromList.region,
      latitude: r.latitude ?? fromList.latitude,
      longitude: r.longitude ?? fromList.longitude,
    }
  }
  return d.relatedPlants.filter(rp => String(rp.id) !== currentId).map(enrich)
})
const relatedTop10 = computed(() => relatedPlants.value.slice(0, 10))
onMounted(async () => {
  try {
    const [listAll, mapRes] = await Promise.all([getAllPlantsList(), getPlantsMapData()])
    allPlants.value = (listAll || []).filter(p => p.latitude != null && p.longitude != null)
    mapPlants.value = mapRes?.plants ?? []
    const s = new Set(unionPoints.value.map(p => p.state).filter(Boolean))
    states.value = Array.from(s).sort()
    initMap()
    renderMarkers()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
onUnmounted(() => {
  // Clean up map instance
  if (map) {
    map.remove()
    map = null
  }
  if (markersLayer) {
    markersLayer.clearLayers()
    markersLayer = null
  }
  if (focusRing) {
    focusRing.remove()
    focusRing = null
  }
  idToMarker.clear()
})
// Listen for filter changes, focus on selected state
watch(selectedState, () => focusOnSelectedState())
function initMap() {
  // Check if map is already initialized
  if (map) {
    console.warn('Map already initialized, skipping...')
    return
  }

  // Check if DOM element exists
  const mapContainer = document.getElementById('tp-map')
  if (!mapContainer) {
    console.error('Map container not found')
    return
  }

  // Check if container is already used by Leaflet
  if (mapContainer._leaflet_id) {
    console.warn('Map container already has Leaflet instance, cleaning up...')
    // Clean up existing Leaflet instance
    mapContainer._leaflet_id = null
    // Clear container content
    mapContainer.innerHTML = ''
  }

  try {
    map = L.map('tp-map', { zoomControl: true, attributionControl: true })
    map.setView([-25.2744, 133.7751], 4)
    if (map.attributionControl?.setPrefix) map.attributionControl.setPrefix('')
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors'
    }).addTo(map)
    markersLayer = L.layerGroup().addTo(map)
    setTimeout(() => map.invalidateSize(), 150)
  } catch (error) {
    console.error('Error initializing map:', error)
  }
}
function renderMarkers() {
  if (!markersLayer) return
  markersLayer.clearLayers()
  idToMarker.clear()
  const pts = filteredMapPoints.value
  const sameCoordCounter = new Map()
  const jitter = (lat, lng) => {
    const key = `${lat},${lng}`
    const count = (sameCoordCounter.get(key) || 0) + 1
    sameCoordCounter.set(key, count)
    if (count === 1) return [lat, lng]
    const r = 0.0003 * (1 + Math.floor(count / 8))
    const angle = (count % 8) * (Math.PI / 4)
    return [lat + r * Math.cos(angle), lng + r * Math.sin(angle)]
  }
  pts.forEach(p => {
    const [lat, lng] = jitter(p.latitude, p.longitude)
    const marker = L.circleMarker([lat, lng], {
      radius: 6,
      weight: 2,
      color: '#fff',
      fillOpacity: 0.95,
      fillColor: p.markerColor || statusColor(p.maxStatus),
    })
    const popupHtml =
      (p.popupContent ||
        `<strong>${humanize(p.binomial)}</strong><br/>Status: ${p.maxStatus || ''}<br/>Region: ${p.region || ''}`) +
      `<br/><button class="popup-btn" data-id="${p.id}" style="margin-top:6px;padding:6px 10px;border:none;border-radius:8px;background:#111;color:#fff;cursor:pointer;">Detail</button>`
    marker.bindPopup(popupHtml, { autoPan: true, keepInView: true })
    marker.on('popupopen', (e) => {
      const container = e?.popup?.getElement?.() || null
      const attach = () => {
        const root = (e?.popup?.getElement?.() || container)
        const btn = root?.querySelector('.popup-btn')
        if (!btn) {
          if ((attach._try = (attach._try || 0) + 1) <= 5) return requestAnimationFrame(attach)
          return
        }
        btn.addEventListener('click', (ev) => {
          console.log('Detail button clicked for plant ID:', p.id)
          ev.preventDefault()
          ev.stopPropagation()
          openDetail(p.id)
          marker.closePopup()
        }, { once: true })
      }
      requestAnimationFrame(attach)
    })
    marker.on('click', () => marker.openPopup())
    marker.addTo(markersLayer)
    idToMarker.set(String(p.id), marker)
  })
  if (pts.length) {
    try {
      const group = L.featureGroup(markersLayer.getLayers())
      const b = group.getBounds().pad(0.2)
      if (b.isValid()) map.fitBounds(b, { maxZoom: 10 })
    } catch { }
  }
}
function focusOnSelectedState() {
  if (!map || selectedState.value === '__ALL__') {
    // If "All" is selected, show entire Australia
    map.setView([-25.2744, 133.7751], 4)
    return
  }

  // Get plant points for selected state
  const statePoints = unionPoints.value.filter(p => p.state === selectedState.value)

  if (statePoints.length === 0) {
    // If no points for this state, show entire Australia
    map.setView([-25.2744, 133.7751], 4)
    return
  }

  // Calculate bounds for all points in this state
  const bounds = L.latLngBounds()
  statePoints.forEach(point => {
    if (point.latitude && point.longitude) {
      bounds.extend([point.latitude, point.longitude])
    }
  })

  if (bounds.isValid()) {
    // Focus on state bounds with some padding
    map.fitBounds(bounds, {
      padding: [20, 20],
      maxZoom: 8  // Limit max zoom level to avoid over-zooming
    })
  }
}
function openPopupForPlant(id) {
  const m = idToMarker.get(String(id))
  if (!m) return false
  try { m.openPopup(); return true } catch { return false }
}
async function openDetail(id) {
  console.log('Opening detail for plant ID:', id)
  detail.value.show = true
  detail.value.loading = true
  detail.value.error = null
  detail.value.id = id
  detail.value.data = null

  // Force reactive update
  await new Promise(resolve => setTimeout(resolve, 0))

  // Add debug information
  console.log('Detail show state:', detail.value.show)
  console.log('Detail loading state:', detail.value.loading)

  try {
    console.log('Fetching plant detail for ID:', id)
    const res = await getPlantDetail(id)
    console.log('API response:', res)
    const plant = res?.plant ?? res?.data ?? res
    const fromList =
      allPlants.value.find(x => String(x.id) === String(id)) ||
      unionPoints.value.find(x => String(x.id) === String(id))
    const merged = { ...fromList, ...(plant || {}) }
    if (!merged.latitude && plant?.location?.latitude) merged.latitude = plant.location.latitude
    if (!merged.longitude && plant?.location?.longitude) merged.longitude = plant.location.longitude
    detail.value.data = merged
    console.log('Final detail data:', detail.value.data)
    highlightOnMap(detail.value.data)
  } catch (e) {
    console.error('Error loading plant detail:', e)
    detail.value.error = 'Failed to load plant detail.'
  } finally {
    detail.value.loading = false
    console.log('Detail loading completed, show:', detail.value.show)
  }
}
function closeDetail() {
  detail.value.show = false
  removeHighlight()
}
function coordOrDash(type) {
  const d = detail.value.data || {}
  const lat = d.location?.latitude ?? d.latitude
  const lng = d.location?.longitude ?? d.longitude
  if (type === 'lat') return lat != null ? lat : '—'
  if (type === 'lng') return lng != null ? lng : '—'
  return '—'
}
function viewOnMap(id) {
  const d = detail.value.data
  const lat = d?.location?.latitude ?? d?.latitude
  const lng = d?.location?.longitude ?? d?.longitude
  if (lat == null || lng == null) return
  closeDetail()
  requestAnimationFrame(() => {
    map.flyTo([lat, lng], Math.max(map.getZoom(), 8), { duration: 0.6 })
    const after = () => {
      highlightOnMap({ latitude: lat, longitude: lng })
      let tries = 0
      const tryOpen = () => {
        if (openPopupForPlant(id)) return
        if (++tries <= 5) setTimeout(tryOpen, 120)
      }
      tryOpen()
    }
    setTimeout(after, 650)
  })
}
function highlightOnMap(d) {
  removeHighlight()
  const lat = d?.location?.latitude ?? d?.latitude
  const lng = d?.location?.longitude ?? d?.longitude
  if (lat == null || lng == null) return
  focusRing = L.circle([lat, lng], { radius: 20000, color: '#111', weight: 1, fillColor: '#111', fillOpacity: 0.08 }).addTo(map)
}
function removeHighlight() {
  if (focusRing) {
    focusRing.remove()
    focusRing = null
  }
}
</script>

<style scoped>
.tp-wrapper {
  margin-top: var(--app-header-height);
  position: relative;
  isolation: auto;
  z-index: auto;
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 5px;
  height: calc(77vh - 24px);
  padding: 12px;
}

.map-wrap {
  background: var(--surface);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  position: relative;
  z-index: auto;
}

.map {
  width: 100%;
  height: 100%;
  min-height: 540px;
}

:deep(.leaflet-container) {
  background: var(--card);
  color: var(--fg);
}

:deep(.leaflet-popup-content-wrapper) {
  background: var(--card);
  color: var(--fg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-md);
  border-radius: 10px;
}

:deep(.leaflet-popup-tip) {
  background: var(--card);
  border: 1px solid var(--border);
}

:deep(.leaflet-pane.leaflet-popup-pane) {
  z-index: 5000 !important;
  pointer-events: auto;
}

:deep(.leaflet-top),
:deep(.leaflet-bottom) {
  z-index: 4000 !important;
}

.side {
  display: flex;
  flex-direction: column;
  background: var(--card);
  border-radius: 16px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  overflow: hidden;
  color: var(--fg);
}

.side-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-bottom: 1px solid var(--border-weak);
  position: sticky;
  top: 0;
  background: color-mix(in oklab, var(--card) 94%, transparent);
  z-index: 1;
}

.state-select {
  flex: 1;
  height: 40px;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0 12px;
  background: var(--surface);
  color: var(--fg);
}

.state-select:focus-visible {
  outline: var(--ring);
  outline-offset: 2px;
}

.count {
  font-size: 12px;
  color: var(--muted);
  white-space: nowrap;
}

.card-list {
  padding: 8px 10px 14px 10px;
  overflow-y: auto;
}

.empty {
  color: var(--muted);
  font-size: 13px;
  padding: 12px;
  text-align: center;
}

.plant-card {
  display: grid;
  grid-template-columns: 84px 1fr;
  gap: 12px;
  padding: 10px;
  border-radius: 14px;
  border: 1px solid var(--border);
  margin-bottom: 10px;
  cursor: pointer;
  transition: transform .08s ease, box-shadow .12s ease, border-color .12s ease, background .12s ease;
  background: var(--card);
  color: var(--fg);
}

.plant-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
  border-color: var(--brand);
  background: var(--surface);
}

.thumb {
  width: 84px;
  height: 84px;
  border-radius: 12px;
  background: var(--surface) center / cover no-repeat;
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.common {
  margin: 0;
  font-size: 16px;
  color: var(--fg);
  font-weight: 700;
}

.binomial {
  font-size: 12px;
  color: var(--muted);
}

.row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.badge {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
  background: var(--surface);
  color: var(--fg);
  border: 1px solid var(--border-weak);
  font-weight: 600;
}

.badge.small {
  font-size: 11px;
  padding: 2px 6px;
}

.badge--ce {
  background: color-mix(in oklab, #ff3b30 16%, var(--surface));
  color: #b30000;
}

.badge--en {
  background: color-mix(in oklab, #ff6b00 16%, var(--surface));
  color: #b34700;
}

.badge--vu {
  background: color-mix(in oklab, #f3b300 16%, var(--surface));
  color: #9a7b00;
}

.region {
  font-size: 12px;
  color: var(--muted);
}

.skeleton {
  padding: 12px;
}

.sk-item {
  height: 88px;
  border-radius: 14px;
  background: linear-gradient(90deg, var(--surface) 25%, color-mix(in oklab, var(--surface) 70%, var(--card)) 37%, var(--surface) 63%);
  background-size: 400% 100%;
  animation: shine 1.2s infinite;
  margin-bottom: 10px;
}

@keyframes shine {
  0% {
    background-position: 100% 50%
  }

  100% {
    background-position: 0 50%
  }
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: color-mix(in oklab, var(--fg) 35%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 9000;
  margin-top: 0;
}

.modal {
  width: min(860px, 94vw);
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  position: relative;
  color: var(--fg);
}

.modal-close {
  position: absolute;
  right: 10px;
  top: 8px;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 22px;
  line-height: 1;
  background: var(--surface);
  color: var(--fg);
  cursor: pointer;
}

.modal-close:hover {
  background: var(--hover);
}

.modal-head {
  display: flex;
  gap: 16px;
  padding: 18px 18px 6px 18px;
  border-bottom: 1px solid var(--border-weak);
}

.modal-title h2 {
  margin: 0;
  font-size: 20px;
  line-height: 1.2;
  color: var(--fg);
}

.sub {
  font-size: 13px;
  color: var(--muted);
  margin-top: 4px;
}

.tags {
  margin-top: 8px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
  background: var(--surface);
  color: var(--fg);
  border: 1px solid var(--border-weak);
}

.modal-body {
  padding: 16px 18px 18px 18px;
}

.info-grid-2col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 28px;
}

.info .label {
  width: 100px;
  font-size: 12px;
  color: var(--muted);
}

.info .value {
  font-size: 14px;
  color: var(--fg);
  font-weight: 600;
}

.desc {
  margin-top: 12px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--fg);
  white-space: pre-wrap;
}

.desc.empty {
  color: var(--muted);
}

.related {
  margin-top: 14px;
}

.rel-title {
  font-size: 14px;
  color: var(--fg);
  margin: 0 0 8px 0;
  font-weight: 700;
}

.rel-list {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}

@media (max-width: 1400px) {
  .rel-list {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 1280px) {
  .rel-list {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1100px) {
  .rel-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.rel-card {
  text-align: left;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--card);
  cursor: pointer;
  transition: box-shadow .12s ease, transform .06s ease, border-color .12s ease, background .12s ease;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: var(--fg);
}

.rel-card:hover {
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
  border-color: var(--brand);
  background: var(--surface);
}

.rel-name {
  font-size: 13px;
  color: var(--fg);
  font-weight: 700;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.rel-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: var(--muted);
}

.rel-line {
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btns {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}

.btn {
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid transparent;
  background: var(--fg);
  color: var(--card);
  cursor: pointer;
}

.btn:hover {
  filter: brightness(0.95);
}

.btn.outline {
  background: var(--card);
  color: var(--fg);
  border: 1px solid var(--border);
}

.btn.outline:hover {
  background: var(--hover);
}

.modal-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 48px 18px;
  color: var(--fg);
}

.spinner {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 3px solid var(--border-weak);
  border-top-color: var(--brand);
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity .15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 1100px) {
  .tp-wrapper {
    grid-template-columns: 1fr;
    height: auto;
  }

  .map {
    min-height: 420px;
  }
}
</style>
