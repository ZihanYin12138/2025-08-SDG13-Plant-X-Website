<template>
  <div class="urban-map-container">
    <!-- 搜索 -->
    <div class="top-toolbar" role="search" aria-label="Tree search toolbar">
      <div class="toolbar-row">
        <div class="search-input-group">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search tree names, IDs or enter coordinates (e.g.: -37.81793,144.96478)"
            class="search-input"
            :class="{ 'error': searchError }"
            @keyup.enter="performSearch"
            @input="clearError"
            @keydown.esc="clearAll"
            aria-label="Search trees by text or coordinates"
          />
          <button @click="performSearch" class="search-btn" aria-label="Search">Search</button>
          <button v-if="searchQuery" @click="clearAll" class="clear-btn" aria-label="Clear search">×</button>
        </div>

        <div class="toolbar-actions">
          <div class="radius-control compact" aria-label="Search radius (meters)">
            <label>Radius: <strong>{{ radius }}m</strong></label>
            <input
              v-model.number="radius"
              type="range"
              min="50"
              max="1000"
              step="50"
              class="radius-slider"
              @input="onRadiusChange"
            />
          </div>
          <!-- <button class="geo-btn" @click="useMyLocation" aria-label="Use my location">Use my location</button> -->
        </div>
      </div>

      <!-- Hint & Error Chips -->
      <div class="feedback">
        <!-- <span v-if="searchType === 'coordinates'" class="chip chip-green">📍 Coordinates</span>
        <span v-else-if="searchType === 'text'" class="chip chip-blue">🔍 Text</span> -->
        <span v-if="searchError" class="chip chip-error">⚠️ {{ searchError }}</span>
      </div>
    </div>

    <!-- Map Container -->
    <div ref="mapContainer" class="map-container">
      <!-- Legend (保留为地图上的浮层) -->
      <div class="legend">
        <h4>Maturity Legend</h4>
        <div class="legend-item">
          <span class="legend-color juvenile"></span>
          <span>Juvenile</span>
        </div>
        <div class="legend-item">
          <span class="legend-color semi-mature"></span>
          <span>Semi-Mature</span>
        </div>
        <div class="legend-item">
          <span class="legend-color mature"></span>
          <span>Mature</span>
        </div>
        <div class="legend-item">
          <span class="legend-color unknown"></span>
          <span>Unknown</span>
        </div>
      </div>

      <!-- Trees List (保持为地图上的侧栏浮层) -->
      <div
        class="trees-sidebar"
        v-if="trees.length > 0"
        ref="sidebarEl"
        @click.stop
        @mousedown.stop
        @dblclick.stop
        @contextmenu.stop
        @touchstart.stop
      >
        <div class="sidebar-header">
          <h3>Found {{ trees.length }} trees</h3>
          <button @click="closeSidebar" class="close-btn" aria-label="Close sidebar">×</button>
        </div>

        <!-- 阻断滚轮向地图冒泡，确保侧栏可用滚轮下滑 -->
        <div class="trees-list" @wheel.stop @touchmove.stop ref="treesListEl">
          <div
            v-for="tree in trees"
            :key="tree.com_id"
            class="tree-card"
            :class="{ active: selectedTreeId === tree.com_id }"
            @click="selectTree(tree, 'card')"
            @mouseenter="hoverTree(tree)"
            @mouseleave="unhoverTree(tree)"
            :ref="el => setCardRef(el, tree.com_id)"
          >
            <div class="tree-info">
              <h4>{{ tree.common_name || 'Unknown Tree' }}</h4>
              <p class="scientific-name">{{ tree.scientific_name }}</p>
              <div class="tree-details">
                <span class="maturity" :class="tree.maturity_std?.toLowerCase()">
                  {{ tree.maturity_std || 'Unknown' }}
                </span>
                <span class="distance">{{ tree.distance }}m</span>
              </div>
              <div class="tree-extra-info">
                <div class="info-row">
                  <span class="label">Family:</span>
                  <span class="value">{{ tree.family }}</span>
                </div>
                <div class="info-row" v-if="tree.age">
                  <span class="label">Age:</span>
                  <span class="value">{{ tree.age }} years</span>
                </div>
                <div class="info-row" v-if="tree.located_in">
                  <span class="label">Location:</span>
                  <span class="value">{{ tree.located_in }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-overlay" aria-live="polite">
        <div class="spinner"></div>
        <p>Searching for trees...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { searchTrees } from '@/api/trees'

// 修复Leaflet默认图标问题
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

export default {
  name: 'UrbanMap',
  emits: ['map-click', 'api-response'],
  setup(props, { emit }) {
    const mapContainer = ref(null)
    const map = ref(null)
    const markers = ref(null)
    const circleLayer = ref(null)
    const centerMarkerRef = ref(null)
    const sidebarEl = ref(null)
    const treesListEl = ref(null)

    // 读取 :root CSS 变量（支持暗/亮主题切换）
    function cssVar(name, fallback = '') {
      const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
      return v || fallback
    }

    // Reactive data
    const trees = ref([])
    const loading = ref(false)
    const searchQuery = ref('')
    const radius = ref(100)
    const selectedTreeId = ref('')
    const currentCenter = ref([-37.81793, 144.96478])  // 初始中心：CBD
    const searchError = ref('')
    const searchType = ref('') // 'coordinates' or 'text'

    // Melbourne Metropolitan bounds（近似包络）
    const melbMetroBounds = L.latLngBounds(
      L.latLng(-38.35, 144.25),  // SW
      L.latLng(-37.35, 145.65)   // NE
    )

    // Maturity color mapping
    const maturityColors = {
      'Juvenile': '#5C8E2F',
      'Semi-Mature': '#A6A43A',
      'Mature': '#F3A24A',
      'Unknown': '#777777'
    }

    // 索引
    const markerIndex = ref(new Map())        // com_id -> marker
    const cardRefs = ref(Object.create(null)) // com_id -> card element
    const pulseLayer = ref(null)              // 临时脉冲圈

    // 供 v-for 回调 ref 使用
    function setCardRef(el, id) {
      const key = String(id)
      if (el) cardRefs.value[key] = el
      else delete cardRefs.value[key]
    }

    function clearError() { searchError.value = '' }
    function clearAll() { searchQuery.value = ''; searchError.value = ''; searchType.value = '' }

    function parseCoordinates(input) {
      if (!input || typeof input !== 'string') return null
      const cleaned = input.trim()
      const separators = [',', ' ', ';', '\t']
      let parts = null
      for (const sep of separators) {
        if (cleaned.includes(sep)) {
          parts = cleaned.split(sep).map(p => p.trim()).filter(p => p)
          break
        }
      }
      if (!parts || parts.length !== 2) return null
      const lat = parseFloat(parts[0])
      const lng = parseFloat(parts[1])
      if (isNaN(lat) || isNaN(lng)) return null
      if (lat < -90 || lat > 90) return null
      if (lng < -180 || lng > 180) return null
      return { lat, lng }
    }

    onMounted(async () => {
      initMap()
      await nextTick()
      armOverlayEventGuards()
    })

    onUnmounted(() => { if (map.value) map.value.remove() })

    function initMap() {
      if (!mapContainer.value) return

      // Create map with Melbourne bounds & viscosity
      map.value = L.map(mapContainer.value, {
        zoomControl: true,
        minZoom: 9,
        maxZoom: 20,
        maxBounds: melbMetroBounds,
        maxBoundsViscosity: 1.0,
        inertia: true,
        worldCopyJump: false
      })

      // 初次视野：适配全市，再聚焦到CBD
      map.value.fitBounds(melbMetroBounds, { padding: [20, 20] })
      map.value.setView(currentCenter.value, 12)

      // Tile layer
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
      }).addTo(map.value)

      // Marker group
      markers.value = L.layerGroup().addTo(map.value)

      // Center marker
      centerMarkerRef.value = L.marker(currentCenter.value, {
        icon: L.divIcon({
          className: 'center-marker',
          html: '<div class="center-marker-inner">📍</div>',
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        })
      }).addTo(map.value)
      centerMarkerRef.value.bindPopup('Search Center')

      // Search circle
      updateSearchCircle()

      // Map click → 更新中心并搜索（对浮层点击做兜底过滤）
      map.value.on('click', (e) => {
        const t = e.originalEvent?.target
        const hitOverlay = t?.closest?.('.trees-sidebar, .legend, .leaflet-control, .top-toolbar, .map-controls')
        if (hitOverlay) return

        currentCenter.value = [e.latlng.lat, e.latlng.lng]
        emit('map-click', { lat: e.latlng.lat, lon: e.latlng.lng, time: new Date().toLocaleTimeString() })
        updateSearchCircle()
        performSearch()
      })

      // 初始搜索
      setTimeout(() => performSearch(), 300)
    }

    function armOverlayEventGuards() {
      if (sidebarEl.value) {
        L.DomEvent.disableClickPropagation(sidebarEl.value)
        L.DomEvent.disableScrollPropagation(sidebarEl.value)
      }
      const legend = mapContainer.value?.querySelector('.legend')
      if (legend) {
        L.DomEvent.disableClickPropagation(legend)
        L.DomEvent.disableScrollPropagation(legend)
      }
      const oldControls = mapContainer.value?.querySelector('.map-controls')
      if (oldControls) {
        L.DomEvent.disableClickPropagation(oldControls)
        L.DomEvent.disableScrollPropagation(oldControls)
      }
    }

    function updateSearchCircle() {
      if (!map.value) return
      if (circleLayer.value) map.value.removeLayer(circleLayer.value)
      if (centerMarkerRef.value) centerMarkerRef.value.setLatLng(currentCenter.value)

      const brand = cssVar('--brand', '#2cb67d')
      circleLayer.value = L.circle(currentCenter.value, {
        radius: radius.value,
        color: brand,
        weight: 2,
        fill: false,
        dashArray: '5, 5'
      }).addTo(map.value)
    }

    async function performSearch() {
      if (loading.value) return
      searchError.value = ''
      searchType.value = ''
      loading.value = true
      trees.value = []
      selectedTreeId.value = ''
      markerIndex.value.clear()
      markers.value?.clearLayers()

      try {
        const coordinates = parseCoordinates(searchQuery.value)

        if (!searchQuery.value.trim()) {
          searchType.value = 'location'
        } else if (coordinates) {
          searchType.value = 'coordinates'
          currentCenter.value = [coordinates.lat, coordinates.lng]
          if (map.value) map.value.setView(currentCenter.value, Math.max(map.value.getZoom(), 14))
          updateSearchCircle()
          searchQuery.value = '' // 坐标模式后清空文本框
        } else {
          const hasNumbers = /\d/.test(searchQuery.value)
          const hasComma = searchQuery.value.includes(',')
          if (hasNumbers && hasComma) {
            searchError.value = 'Invalid coordinate format, please use: latitude,longitude (e.g.: -37.81793,144.96478)'
            return
          }
          searchType.value = 'text'
        }

        const params = {
          lat: currentCenter.value[0],
          lon: currentCenter.value[1],
          radius: radius.value,
          search: (searchType.value === 'coordinates' || searchType.value === 'location') ? '' : searchQuery.value
        }

        const data = await searchTrees(params)
        if (data?.success) {
          trees.value = data.trees || []
          displayTreesOnMap()
          emit('api-response', {
            center: data.center,
            total: data.total,
            time: new Date().toLocaleTimeString()
          })
          await nextTick()
          armOverlayEventGuards()
        } else {
          searchError.value = 'Search failed, please check input or try again later'
        }
      } catch (err) {
        console.error('Error searching for trees:', err)
        searchError.value = 'An error occurred during search, please try again later'
      } finally {
        loading.value = false
      }
    }

    function displayTreesOnMap() {
      if (!map.value || !markers.value) return
      markers.value.clearLayers()
      markerIndex.value.clear()

      trees.value.forEach(tree => {
        const color = maturityColors[tree.maturity_std] || '#777777'
        const marker = L.circleMarker([tree.latitude, tree.longitude], {
          radius: 6,
          color,
          weight: 2,
          fillColor: color,
          fillOpacity: 0.9
        })

        // 点击 marker：偏移避开侧栏 + 滚动侧栏卡片居中
        marker.on('click', () => selectTree(tree, 'marker'))

        marker.on('mouseover', () => marker.setStyle({ weight: 4 }))
        marker.on('mouseout',  () => {
          if (selectedTreeId.value !== tree.com_id) marker.setStyle({ weight: 2 })
        })

        const popupContent = `
          <div class="tree-popup">
            <h4>${tree.common_name || 'Unknown Tree'}</h4>
            <p><strong>Scientific Name:</strong> ${tree.scientific_name}</p>
            <p><strong>Family:</strong> ${tree.family}</p>
            <p><strong>Maturity:</strong> ${tree.maturity_std}</p>
            <p><strong>Distance:</strong> ${tree.distance}m</p>
            ${tree.age ? `<p><strong>Age:</strong> ${tree.age} years</p>` : ''}
          </div>
        `
        marker.bindPopup(popupContent)

        markers.value.addLayer(marker)
        if (tree.com_id != null) markerIndex.value.set(String(tree.com_id), marker)
      })
    }

    // 视图偏移：让选中点避开右侧侧栏（用于 marker 点击）
    function panToWithSidebarOffset(latlng) {
      const m = map.value
      if (!m) return
      const zoom = Math.max(m.getZoom(), 18)
      const p = m.project(latlng, zoom)
      const sidebarWidth = (sidebarEl.value?.offsetWidth || 260)
      const offsetX = -(sidebarWidth / 2 + 30)
      const pOffset = L.point(p.x + offsetX, p.y)
      m.setView(m.unproject(pOffset, zoom), zoom, { animate: true })
    }

    // 视图居中（用于卡片点击）
    function panToCenter(latlng) {
      const m = map.value
      if (!m) return
      const zoom = Math.max(m.getZoom(), 18)
      m.setView(latlng, zoom, { animate: true })
    }

    // 将对应卡片滚动到侧栏中间（仅 marker 点击时使用）
    function scrollCardIntoView(comId) {
      const el = cardRefs.value[String(comId)]
      if (!el) return
      if (el.scrollIntoView) {
        el.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'smooth' })
        return
      }
      const list = treesListEl.value
      if (!list) return
      const listRect = list.getBoundingClientRect()
      const elRect = el.getBoundingClientRect()
      const delta = (elRect.top - listRect.top) - (list.clientHeight / 2 - el.clientHeight / 2)
      list.scrollBy({ top: delta, behavior: 'smooth' })
    }

    // 高亮 marker + 打开 popup + 轻量脉冲
    function highlightMarker(marker, latlng) {
      const brand = cssVar('--brand', '#2cb67d')

      markers.value?.eachLayer((layer) => {
        if (layer instanceof L.CircleMarker) layer.setStyle({ weight: 2 })
      })

      marker.setStyle({ weight: 5, color: brand, fillColor: brand })
      marker.bringToFront()
      marker.openPopup()

      if (pulseLayer.value) {
        map.value?.removeLayer(pulseLayer.value)
        pulseLayer.value = null
      }
      pulseLayer.value = L.circle(latlng, {
        radius: 18,
        color: brand,
        weight: 2,
        fillOpacity: 0,
        dashArray: '2,6'
      }).addTo(map.value)

      setTimeout(() => {
        if (pulseLayer.value) {
          map.value?.removeLayer(pulseLayer.value)
          pulseLayer.value = null
        }
      }, 900)
    }

    async function selectTree(tree, source = 'card') {
      selectedTreeId.value = tree.com_id
      const marker = markerIndex.value.get(String(tree.com_id))
      const latlng = L.latLng(tree.latitude, tree.longitude)

      if (marker) {
        highlightMarker(marker, latlng)
        if (source === 'marker') {
          panToWithSidebarOffset(latlng)
          await nextTick()
          scrollCardIntoView(tree.com_id)  // 仅 marker 点击时滚动侧栏
        } else {
          panToCenter(latlng)              // 卡片点击：让 Popup 到地图正中
          // 不滚动侧栏
        }
      } else {
        // 兜底：无索引时按经纬度匹配
        markers.value?.eachLayer((layer) => {
          if (layer instanceof L.CircleMarker) {
            const ll = layer.getLatLng()
            if (Math.abs(ll.lat - tree.latitude) < 0.0001 && Math.abs(ll.lng - tree.longitude) < 0.0001) {
              highlightMarker(layer, latlng)
            } else {
              layer.setStyle({ weight: 2 })
            }
          }
        })
        if (source === 'marker') {
          panToWithSidebarOffset(latlng)
          await nextTick()
          scrollCardIntoView(tree.com_id)
        } else {
          panToCenter(latlng)
        }
      }
    }

    function hoverTree(tree) {
      const marker = markerIndex.value.get(String(tree.com_id))
      if (marker && selectedTreeId.value !== tree.com_id) marker.setStyle({ weight: 4 })
    }
    function unhoverTree(tree) {
      const marker = markerIndex.value.get(String(tree.com_id))
      if (marker && selectedTreeId.value !== tree.com_id) marker.setStyle({ weight: 2 })
    }

    function onRadiusChange() {
      updateSearchCircle()
      performSearch()
    }

    function closeSidebar() {
      trees.value = []
      selectedTreeId.value = ''
      markerIndex.value.clear()
      if (markers.value) markers.value.clearLayers()
    }

    function useMyLocation() {
      if (!navigator.geolocation) return
      navigator.geolocation.getCurrentPosition(
        pos => {
          const lat = pos.coords.latitude
          const lon = pos.coords.longitude
          const ll = L.latLng(lat, lon)
          if (melbMetroBounds.contains(ll)) {
            currentCenter.value = [lat, lon]
            map.value?.setView(currentCenter.value, 15)
            updateSearchCircle()
            performSearch()
          } else {
            searchError.value = 'Your location is outside the Melbourne metropolitan area'
          }
        },
        () => { searchError.value = 'Unable to access location' },
        { enableHighAccuracy: true, timeout: 8000 }
      )
    }

    const setCenter = (lat, lon) => {
      const ll = L.latLng(lat, lon)
      const clamped = melbMetroBounds.contains(ll) ? ll : melbMetroBounds.getCenter()
      currentCenter.value = [clamped.lat, clamped.lng]
      if (map.value) {
        map.value.setView(currentCenter.value, 17)
        updateSearchCircle()
      }
    }

    watch(trees, async () => {
      await nextTick()
      armOverlayEventGuards()
    })

    return {
      mapContainer,
      trees,
      loading,
      searchQuery,
      radius,
      selectedTreeId,
      searchError,
      searchType,
      performSearch,
      onRadiusChange,
      closeSidebar,
      setCenter,
      clearError,
      clearAll,
      useMyLocation,
      sidebarEl,
      treesListEl,
      selectTree,
      hoverTree,
      unhoverTree,
      setCardRef
    }
  }
}
</script>

<style scoped>
.urban-map-container {
  position: relative;
  width: 100%;
  height: 600px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  background: var(--card);
  color: var(--fg);
  z-index: 0;
  isolation: isolate;
}

.top-toolbar {
  background: color-mix(in oklab, var(--card) 92%, transparent);
  backdrop-filter: saturate(180%) blur(8px);
  border-bottom: 1px solid var(--border-weak);
  padding: 10px 12px;
  color: var(--fg);
}

.toolbar-row {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}

.search-input-group {
  display: flex;
  gap: 8px;
  align-items: center;
  min-width: 300px;
  flex: 1;
}

.search-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  background: var(--card);
  color: var(--fg);
  transition: border-color .2s, box-shadow .2s;
  outline: none;
  max-width: 500px;
}
.search-input:focus-visible { outline: var(--ring); outline-offset: 2px; }
.search-input.error {
  border-color: color-mix(in oklab, #dc3545 70%, var(--border));
  box-shadow: 0 0 0 2px color-mix(in oklab, #dc3545 12%, transparent);
}

.search-btn {
  padding: 10px 16px;
  background: var(--brand);
  color: #00241a;
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: transform .05s ease-in-out, box-shadow .2s, background .15s;
  box-shadow: var(--shadow-sm);
}
.search-btn:hover { background: var(--brand-strong); }
.search-btn:active { transform: translateY(1px); }

.clear-btn {
  padding: 8px 12px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--fg);
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}
.clear-btn:hover { background: var(--hover); }

.toolbar-actions { display: flex; gap: 12px; align-items: center; }

.radius-control { display: flex; flex-direction: column; gap: 6px; }
.radius-control label { font-size: 12px; color: var(--muted); }
.radius-control.compact { min-width: 270px; }
.radius-slider { width: 100%; accent-color: var(--brand); }

.geo-btn {
  padding: 10px 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--fg);
}
.geo-btn:hover { background: var(--hover); }

.feedback { margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap; }
.chip {
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 999px;
  border: 1px solid var(--border-weak);
  background: var(--surface);
  color: var(--fg);
}
.chip-blue  { background: color-mix(in oklab, var(--brand) 12%, var(--surface)); color: var(--fg); }
.chip-green { background: color-mix(in oklab, var(--brand) 18%, var(--surface)); color: var(--fg); }
.chip-error { background: color-mix(in oklab, #b00020 18%, var(--surface)); color: var(--fg); }

.map-container { position: relative; width: 100%; flex: 1; }

.legend {
  position: absolute;
  left: 12px;
  bottom: 12px;
  z-index: 1000;
  background: var(--card);
  color: var(--fg);
  padding: 10px;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  width: 200px;
  border: 1px solid var(--border);
}
.legend h4 { margin: 0 0 8px 0; font-size: 14px; color: var(--fg); }
.legend-item { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; font-size: 12px; }
.legend-color { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
.legend-color.juvenile    { background: #5C8E2F; }
.legend-color.semi-mature { background: #A6A43A; }
.legend-color.mature      { background: #F3A24A; }
.legend-color.unknown     { background: #777777; }

.trees-sidebar {
  position: absolute;
  top: 0;
  right: 0;
  width: 260px;
  height: 100%;
  background: var(--card);
  border-left: 1px solid var(--border);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  color: var(--fg);
}
.sidebar-header {
  padding: 14px 12px;
  border-bottom: 1px solid var(--border-weak);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sidebar-header h3 { margin: 0; font-size: 16px; color: var(--fg); }
.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--muted);
}
.close-btn:hover { color: var(--fg); }

.trees-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
  scrollbar-gutter: stable;
}

.tree-card {
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  transition: transform .08s ease, box-shadow .2s, border-color .2s, background .2s;
  background: var(--card);
  color: var(--fg);
}
.tree-card:hover {
  background: var(--surface);
  border-color: var(--brand);
  transform: translateY(-1px);
}
.tree-card.active {
  background: color-mix(in oklab, var(--brand) 14%, var(--surface));
  border-color: var(--brand);
  box-shadow: var(--shadow-sm);
}

.tree-info h4 { margin: 0 0 4px 0; font-size: 14px; color: var(--fg); }
.scientific-name { margin: 0 0 8px 0; font-size: 12px; color: var(--muted); font-style: italic; }
.tree-details { display: flex; justify-content: space-between; align-items: center; font-size: 11px; }
.maturity {
  padding: 2px 6px;
  border-radius: 4px;
  color: #fff;
  font-weight: 500;
}
.maturity.juvenile    { background: #5C8E2F; }
.maturity.semi-mature { background: #A6A43A; }
.maturity.mature      { background: #F3A24A; }
.maturity.unknown     { background: #777777; }
.distance { color: var(--muted); }

.tree-extra-info { margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--border-weak); }
.info-row { display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 11px; }
.info-row .label { color: var(--muted); font-weight: 500; }
.info-row .value { color: var(--fg); text-align: right; max-width: 60%; word-break: break-word; }

.loading-overlay {
  position: absolute;
  inset: 0;
  background: color-mix(in oklab, var(--fg) 6%, transparent);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  color: var(--fg);
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-weak);
  border-top: 4px solid var(--brand);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

:deep(.center-marker-inner) { font-size: 20px; text-align: center; line-height: 1; }
:deep(.tree-popup) { min-width: 200px; background: var(--card); color: var(--fg); }
:deep(.tree-popup h4) { margin: 0 0 8px 0; color: var(--fg); }
:deep(.tree-popup p) { margin: 4px 0; font-size: 12px; color: var(--muted); }



:deep(.leaflet-popup-content-wrapper) {
  background: var(--card);
  color: var(--fg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-md);
  border-radius: 10px;
}

:deep(.leaflet-popup-content) {
  margin: 10px 12px;
  color: var(--fg);
}

:deep(.leaflet-popup-tip) {
  background: var(--card);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
}

:deep(.leaflet-container a.leaflet-popup-close-button) {
  color: var(--muted);
  font-weight: 600;
}
:deep(.leaflet-container a.leaflet-popup-close-button:hover) {
  color: var(--fg);
  background: var(--hover);
  border-radius: 6px;
}
:deep(.leaflet-popup-content h1),
:deep(.leaflet-popup-content h2),
:deep(.leaflet-popup-content h3),
:deep(.leaflet-popup-content h4) { color: var(--fg); margin-top: 0; }
:deep(.leaflet-popup-content p),
:deep(.leaflet-popup-content li),
:deep(.leaflet-popup-content span) { color: var(--fg); }
:deep(.leaflet-popup-content a) { color: var(--brand-strong); text-decoration: none; }
:deep(.leaflet-popup-content a:hover) { text-decoration: underline; }
</style>
