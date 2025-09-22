<template>
  <div class="urban-map-container">
    <!-- Map Container -->
    <div ref="mapContainer" class="map-container"></div>
    
    <!-- Search Control Panel -->
    <div class="map-controls">
      <div class="search-panel">
        <div class="search-input-group">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search tree names, IDs or enter coordinates (e.g.: -37.81793,144.96478)"
            class="search-input"
            :class="{ 'error': searchError }"
            @keyup.enter="performSearch"
            @input="clearError"
          />
          <button @click="performSearch" class="search-btn">Search</button>
        </div>
        
        <!-- Search Type Hint -->
        <div v-if="searchType" class="search-type-hint">
          <span v-if="searchType === 'coordinates'" class="hint-coordinates">
            📍 Coordinate Search Mode
          </span>
          <span v-else-if="searchType === 'text'" class="hint-text">
            🔍 Text Search Mode
          </span>
        </div>
        
        <!-- Error Message -->
        <div v-if="searchError" class="search-error">
          ⚠️ {{ searchError }}
        </div>
        
        <div class="radius-control">
          <label>Search Radius: {{ radius }}m</label>
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
      </div>
      
      <!-- Legend -->
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
    </div>
    
    <!-- Trees List -->
    <div class="trees-sidebar" v-if="trees.length > 0">
      <div class="sidebar-header">
        <h3>Found {{ trees.length }} trees</h3>
        <button @click="closeSidebar" class="close-btn">×</button>
      </div>
      
      <div class="trees-list">
        <div
          v-for="tree in trees"
          :key="tree.com_id"
          class="tree-card"
          :class="{ active: selectedTreeId === tree.com_id }"
          @click="selectTree(tree)"
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
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Searching for trees...</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
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

    // Reactive data
    const trees = ref([])
    const loading = ref(false)
    const searchQuery = ref('')
    const radius = ref(100)
    const selectedTreeId = ref('')
    const currentCenter = ref([-37.81793, 144.96478])
    const searchError = ref('')
    const searchType = ref('') // 'coordinates' or 'text'

    // Maturity color mapping
    const maturityColors = {
      'Juvenile': '#5C8E2F',
      'Semi-Mature': '#A6A43A', 
      'Mature': '#F3A24A',
      'Unknown': '#777777'
    }

    // Clear error messages
    function clearError() {
      searchError.value = ''
      searchType.value = ''
    }

    // Coordinate parsing function
    function parseCoordinates(input) {
      if (!input || typeof input !== 'string') return null
      
      // Remove extra spaces
      const cleaned = input.trim()
      
      // Support multiple separators: comma, space, semicolon
      const separators = [',', ' ', ';', '\t']
      let parts = null
      
      for (const sep of separators) {
        if (cleaned.includes(sep)) {
          parts = cleaned.split(sep).map(p => p.trim()).filter(p => p)
          break
        }
      }
      
      // If no separator found, might be format error
      if (!parts || parts.length !== 2) {
        return null
      }
      
      const lat = parseFloat(parts[0])
      const lng = parseFloat(parts[1])
      
      // Validate coordinate ranges
      if (isNaN(lat) || isNaN(lng)) return null
      if (lat < -90 || lat > 90) return null
      if (lng < -180 || lng > 180) return null
      
      return { lat, lng }
    }

    // Initialize map
    onMounted(() => {
      initMap()
    })

    onUnmounted(() => {
      if (map.value) {
        map.value.remove()
      }
    })

    function initMap() {
      if (!mapContainer.value) return
      
      // Create map
      map.value = L.map(mapContainer.value, {
        center: currentCenter.value,
        zoom: 17,
        zoomControl: true
      })
      
      // Add tile layer
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
      }).addTo(map.value)
      
      // Create marker group
      markers.value = L.layerGroup().addTo(map.value)
      
      // Add center point marker
      const centerMarker = L.marker(currentCenter.value, {
        icon: L.divIcon({
          className: 'center-marker',
          html: '<div class="center-marker-inner">📍</div>',
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        })
      }).addTo(map.value)
      
      centerMarker.bindPopup('Search Center')
      
      // Save center marker reference for position updates
      window.centerMarker = centerMarker
      
      // Add search circle
      updateSearchCircle()
      
      // Listen for map click events
      map.value.on('click', (e) => {
        console.log('Map clicked:', e.latlng.lat, e.latlng.lng)
        currentCenter.value = [e.latlng.lat, e.latlng.lng]
        
        // Emit click event to parent component
        emit('map-click', {
          lat: e.latlng.lat,
          lon: e.latlng.lng,
          time: new Date().toLocaleTimeString()
        })
        
        updateSearchCircle()
        // Automatically search for plants near clicked location
        performSearch()
      })
      
      // Search for plants at default location on initial load
      setTimeout(() => {
        performSearch()
      }, 1000)
    }

    function updateSearchCircle() {
      if (!map.value) return
      
      // Remove old circle
      if (circleLayer.value) {
        map.value.removeLayer(circleLayer.value)
      }
      
      // Update center marker position
      if (window.centerMarker) {
        window.centerMarker.setLatLng(currentCenter.value)
      }
      
      // Add new search circle
      circleLayer.value = L.circle(currentCenter.value, {
        radius: radius.value,
        color: '#2c7be5',
        weight: 2,
        fill: false,
        dashArray: '5, 5'
      }).addTo(map.value)
    }

    async function performSearch() {
      if (loading.value) return
      
      // Clear previous errors and hints
      clearError()
      
      // If search box is empty, only search current location
      if (!searchQuery.value.trim()) {
        searchType.value = 'location'
        loading.value = true
        trees.value = []
        selectedTreeId.value = ''
        
        try {
          const params = {
            lat: currentCenter.value[0],
            lon: currentCenter.value[1],
            radius: radius.value,
            search: ''
          }
          
          const data = await searchTrees(params)
          
          if (data.success) {
            trees.value = data.trees || []
            displayTreesOnMap()
            emit('api-response', {
              center: data.center,
              total: data.total,
              time: new Date().toLocaleTimeString()
            })
          }
        } catch (error) {
          console.error('Error searching for trees:', error)
        } finally {
          loading.value = false
        }
        return
      }
      
      loading.value = true
      trees.value = []
      selectedTreeId.value = ''
      
      try {
        // Check if input is coordinate format
        const coordinates = parseCoordinates(searchQuery.value)
        
        if (coordinates) {
          // If coordinates, update map center and clear search box
          searchType.value = 'coordinates'
          currentCenter.value = [coordinates.lat, coordinates.lng]
          if (map.value) {
            map.value.setView(currentCenter.value, 17)
          }
          updateSearchCircle()
          searchQuery.value = '' // Clear search box
          console.log('Set map center to:', coordinates.lat, coordinates.lng)
        } else {
          // Check if looks like coordinates but format is wrong
          const hasNumbers = /\d/.test(searchQuery.value)
          const hasComma = searchQuery.value.includes(',')
          
          if (hasNumbers && hasComma) {
            searchError.value = 'Invalid coordinate format, please use: latitude,longitude (e.g.: -37.81793,144.96478)'
            loading.value = false
            return
          }
          
          searchType.value = 'text'
        }
        
        const params = {
          lat: currentCenter.value[0],
          lon: currentCenter.value[1],
          radius: radius.value,
          search: coordinates ? '' : searchQuery.value // If coordinate search, clear text search
        }
        
        const data = await searchTrees(params)
        
        if (data.success) {
          trees.value = data.trees || []
          console.log('Found trees count:', trees.value.length)
          displayTreesOnMap()
          
          // Emit API response event to parent component
          emit('api-response', {
            center: data.center,
            total: data.total,
            time: new Date().toLocaleTimeString()
          })
        } else {
          console.error('Search failed:', data.error)
          searchError.value = 'Search failed, please check input or try again later'
        }
      } catch (error) {
        console.error('Error searching for trees:', error)
        searchError.value = 'An error occurred during search, please try again later'
      } finally {
        loading.value = false
      }
    }

    function displayTreesOnMap() {
      if (!map.value || !markers.value) return
      
      // Clear existing markers
      markers.value.clearLayers()
      
      // Add tree markers
      trees.value.forEach(tree => {
        const color = maturityColors[tree.maturity_std] || '#777777'
        
        const marker = L.circleMarker([tree.latitude, tree.longitude], {
          radius: 6,
          color: color,
          weight: 2,
          fillColor: color,
          fillOpacity: 0.9
        })
        
        // Add click event
        marker.on('click', () => {
          selectTree(tree)
        })
        
        // Add hover effects
        marker.on('mouseover', () => {
          marker.setStyle({ weight: 4 })
        })
        
        marker.on('mouseout', () => {
          marker.setStyle({ weight: 2 })
        })
        
        // Bind popup
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
      })
    }

    function selectTree(tree) {
      selectedTreeId.value = tree.com_id
      
      // Highlight selected marker
      markers.value?.eachLayer((layer) => {
        if (layer instanceof L.CircleMarker) {
          const latlng = layer.getLatLng()
          if (Math.abs(latlng.lat - tree.latitude) < 0.0001 && 
              Math.abs(latlng.lng - tree.longitude) < 0.0001) {
            layer.setStyle({ weight: 5 })
            layer.openPopup()
          } else {
            layer.setStyle({ weight: 2 })
          }
        }
      })
      
      // Pan to selected tree
      if (map.value) {
        map.value.setView([tree.latitude, tree.longitude], Math.max(map.value.getZoom(), 18))
      }
    }

    function onRadiusChange() {
      updateSearchCircle()
      performSearch()
    }

    function closeSidebar() {
      trees.value = []
      selectedTreeId.value = ''
      if (markers.value) {
        markers.value.clearLayers()
      }
    }


    // Expose methods to parent component
    const setCenter = (lat, lon) => {
      currentCenter.value = [lat, lon]
      if (map.value) {
        map.value.setView(currentCenter.value, 17)
        updateSearchCircle()
      }
    }

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
      clearError
    }
  }
}
</script>

<style scoped>
.urban-map-container {
  position: relative;
  width: 100%;
  height: 500px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-controls {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1000;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-width: 300px;
}

.search-panel {
  margin-bottom: 15px;
}

.search-input-group {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-input.error {
  border-color: #dc3545;
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.1);
}

.search-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.search-btn:hover {
  background: #0056b3;
}

.search-type-hint {
  margin: 8px 0;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f8f9fa;
  border-left: 3px solid #007bff;
}

.hint-coordinates {
  color: #28a745;
  font-weight: 500;
}

.hint-text {
  color: #007bff;
  font-weight: 500;
}

.search-error {
  margin: 8px 0;
  font-size: 12px;
  padding: 6px 8px;
  border-radius: 4px;
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.radius-control {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.radius-control label {
  font-size: 12px;
  color: #666;
}

.radius-slider {
  width: 100%;
}

.legend {
  border-top: 1px solid #eee;
  padding-top: 10px;
}

.legend h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 12px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.legend-color.juvenile { background: #5C8E2F; }
.legend-color.semi-mature { background: #A6A43A; }
.legend-color.mature { background: #F3A24A; }
.legend-color.unknown { background: #777777; }

.trees-sidebar {
  position: absolute;
  top: 0;
  right: 0;
  width: 350px;
  height: 100%;
  background: white;
  border-left: 1px solid #ddd;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.trees-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.tree-card {
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tree-card:hover {
  background: #f8f9fa;
  border-color: #007bff;
}

.tree-card.active {
  background: #e3f2fd;
  border-color: #007bff;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.2);
}

.tree-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #333;
}

.scientific-name {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #666;
  font-style: italic;
}

.tree-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.maturity {
  padding: 2px 6px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
}

.maturity.juvenile { background: #5C8E2F; }
.maturity.semi-mature { background: #A6A43A; }
.maturity.mature { background: #F3A24A; }
.maturity.unknown { background: #777777; }

.distance {
  color: #666;
}

.tree-extra-info {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #eee;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 11px;
}

.info-row .label {
  color: #666;
  font-weight: 500;
}

.info-row .value {
  color: #333;
  text-align: right;
  max-width: 60%;
  word-break: break-word;
}


.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Center marker styles */
:deep(.center-marker-inner) {
  font-size: 20px;
  text-align: center;
  line-height: 1;
}

/* Popup styles */
:deep(.tree-popup) {
  min-width: 200px;
}

:deep(.tree-popup h4) {
  margin: 0 0 8px 0;
  color: #333;
}

:deep(.tree-popup p) {
  margin: 4px 0;
  font-size: 12px;
  color: #666;
}

</style>
