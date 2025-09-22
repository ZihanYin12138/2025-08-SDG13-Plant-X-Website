<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import UrbanMap from '@/components/UrbanMap.vue'

export default {
  name: 'UrbanWild',
  components: {
    UrbanMap
  },
  setup() {
    const $route = useRoute()
    const mapRef = ref(null)

    const testResults = ref('')
    const isTesting = ref(false)
    
    // Coordinate debug data
    const clickCoords = ref({
      lat: null,
      lon: null,
      time: null
    })
    
    const apiResponse = ref({
      center: null,
      total: 0,
      time: null
    })


    // API testing functions
    async function testGET() {
      isTesting.value = true
      testResults.value = 'Testing GET request...\n'
      
      try {
        const response = await fetch('https://ky21h193r2.execute-api.us-east-1.amazonaws.com/test/TreeLocator?com_id=1049657', {
          method: 'GET',
          headers: {
            'Accept': 'application/json'
          }
        })
        
        const data = await response.json()
        testResults.value += `GET request successful!\nStatus code: ${response.status}\nResponse: ${JSON.stringify(data, null, 2)}\n\n`
      } catch (error) {
        testResults.value += `GET request failed: ${error.message}\n\n`
      } finally {
        isTesting.value = false
      }
    }

    async function testPOST() {
      isTesting.value = true
      testResults.value += 'Testing POST request...\n'
      
      try {
        const response = await fetch('https://ky21h193r2.execute-api.us-east-1.amazonaws.com/test/TreeLocator', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            lat: -37.81793,
            lon: 144.96478,
            radius: 100,
            search: "eucalyptus"
          })
        })
        
        const data = await response.json()
        testResults.value += `POST request successful!\nStatus code: ${response.status}\nResponse: ${JSON.stringify(data, null, 2)}\n\n`
      } catch (error) {
        testResults.value += `POST request failed: ${error.message}\n\n`
      } finally {
        isTesting.value = false
      }
    }

    async function testOPTIONS() {
      isTesting.value = true
      testResults.value += 'Testing OPTIONS request...\n'
      
      try {
        const response = await fetch('https://ky21h193r2.execute-api.us-east-1.amazonaws.com/test/TreeLocator', {
          method: 'OPTIONS',
          headers: {
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
          }
        })
        
        const headers = {}
        response.headers.forEach((value, key) => {
          headers[key] = value
        })
        
        testResults.value += `OPTIONS request successful!\nStatus code: ${response.status}\nCORS headers: ${JSON.stringify(headers, null, 2)}\n\n`
      } catch (error) {
        testResults.value += `OPTIONS request failed: ${error.message}\n\n`
      } finally {
        isTesting.value = false
      }
    }

    function clearResults() {
      testResults.value = ''
    }

    function testNavigation() {
      console.log('Testing navigation functionality')
      console.log('Current route:', $route.value)
      console.log('Current URL:', window.location.href)
      alert('Navigation working properly! Current path: ' + window.location.pathname)
    }

    // Handle map click events
    function handleMapClick(coords) {
      clickCoords.value = coords
      console.log('Received map click coordinates:', coords)
    }

    // Handle API response events
    function handleApiResponse(response) {
      apiResponse.value = response
      console.log('Received API response:', response)
    }

    onMounted(() => {
      console.log('UrbanWild component mounted')
      console.log('Current URL:', window.location.href)
      console.log('Current path:', window.location.pathname)
    })

    return {
      mapRef,
      testResults,
      isTesting,
      testGET,
      testPOST,
      testOPTIONS,
      clearResults,
      testNavigation,
      clickCoords,
      apiResponse,
      handleMapClick,
      handleApiResponse
    }
  }
}
</script>

<template>
  <section class="section">
    <div class="container">
      <h2 class="title">Urban & Wild</h2>
      <p class="lead">Explore native and resilient species in urban and wild landscapes, supporting biodiversity and climate resilience.</p>
      <p style="color: #28a745; font-weight: bold;">✅ Page loaded successfully! If you see this message, routing is working properly.</p>
      <p style="color: #007bff; font-weight: bold;">🔧 Debug info: Current URL = {{ $route.fullPath }}</p>
      <button @click="testNavigation" style="background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 0;">
        Test Navigation
      </button>
      
      <!-- Coordinate Debug Info -->
      <div class="coords-debug-container">
        <div>
          <h3>📍 Click Coordinates</h3>
          <div class="coords-info">
            <div><strong>Latitude:</strong> {{ clickCoords.lat || 'Not clicked' }}</div>
            <div><strong>Longitude:</strong> {{ clickCoords.lon || 'Not clicked' }}</div>
            <div><strong>Time:</strong> {{ clickCoords.time || 'Not clicked' }}</div>
          </div>
        </div>
        
        <div>
          <h3>🌳 API Response Coordinates</h3>
          <div class="coords-info">
            <div><strong>Search Center:</strong> {{ apiResponse.center ? `${apiResponse.center.lat}, ${apiResponse.center.lon}` : 'No data' }}</div>
            <div><strong>Search Radius:</strong> {{ apiResponse.center ? `${apiResponse.center.radius}m` : 'No data' }}</div>
            <div><strong>Plants Found:</strong> {{ apiResponse.total || 0 }} trees</div>
            <div><strong>Last Updated:</strong> {{ apiResponse.time || 'No data' }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>


  <!-- API Testing Area -->
  <section class="container">
    <div class="section-box">
      <h2>API Testing Tool</h2>
      <p>Test TreeLocator API GET, POST and OPTIONS requests to verify CORS configuration.</p>
      
      <div class="test-controls">
        <div class="test-buttons">
          <button @click="testGET" :disabled="isTesting" class="test-btn get-btn">
            {{ isTesting ? 'Testing...' : 'Test GET Request' }}
          </button>
          <button @click="testPOST" :disabled="isTesting" class="test-btn post-btn">
            {{ isTesting ? 'Testing...' : 'Test POST Request' }}
          </button>
          <button @click="testOPTIONS" :disabled="isTesting" class="test-btn options-btn">
            {{ isTesting ? 'Testing...' : 'Test OPTIONS Request' }}
          </button>
          <button @click="clearResults" class="test-btn clear-btn">
            Clear Results
          </button>
        </div>
        
        <div class="test-results" v-if="testResults">
          <h3>Test Results:</h3>
          <pre class="results-text">{{ testResults }}</pre>
        </div>
      </div>
    </div>
  </section>

  <!-- Map Component -->
  <section class="container">
    <div class="section-box">
      <h2>Tree Distribution Map</h2>
      <p>Click anywhere on the map or use the search function to explore trees in that area.</p>
      
      <UrbanMap 
        ref="mapRef" 
        @map-click="handleMapClick"
        @api-response="handleApiResponse"
      />
    </div>
  </section>
</template>

<style scoped>
/* Section box styles */
.section-box {
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 20px;
  background: transparent;
  margin-bottom: 20px;
}

.title {
  margin: 0 0 0.5rem;
  color: var(--fg);
}

.lead {
  color: var(--muted);
  margin-bottom: 2rem;
}


/* API testing styles */
.test-controls {
  margin-top: 20px;
}

.test-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.test-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  min-width: 120px;
}

.test-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.get-btn {
  background: #28a745;
  color: white;
}

.get-btn:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-1px);
}

.post-btn {
  background: #007bff;
  color: white;
}

.post-btn:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-1px);
}

.options-btn {
  background: #ffc107;
  color: #212529;
}

.options-btn:hover:not(:disabled) {
  background: #e0a800;
  transform: translateY(-1px);
}

.clear-btn {
  background: #6c757d;
  color: white;
}

.clear-btn:hover:not(:disabled) {
  background: #545b62;
  transform: translateY(-1px);
}

.test-results {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.test-results h3 {
  margin: 0 0 12px 0;
  color: var(--fg);
  font-size: 16px;
}

.results-text {
  background: #212529;
  color: #e9ecef;
  padding: 12px;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  max-height: 400px;
  overflow-y: auto;
}

/* Coordinate debug container styles */
.coords-debug-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin: 20px 0;
}

.coords-debug-container > div {
  border-radius: 8px;
  padding: 15px;
  background: #f8f9fa;
}

.coords-debug-container > div:first-child {
  border: 2px solid #007bff;
}

.coords-debug-container > div:first-child h3 {
  margin: 0 0 10px 0;
  color: #007bff;
}

.coords-debug-container > div:last-child {
  border: 2px solid #28a745;
}

.coords-debug-container > div:last-child h3 {
  margin: 0 0 10px 0;
  color: #28a745;
}

.coords-debug-container .coords-info {
  font-family: monospace;
  font-size: 14px;
  line-height: 1.4;
}

/* Responsive design */
@media (max-width: 768px) {
  .test-buttons {
    flex-direction: column;
  }
  
  .test-btn {
    width: 100%;
  }
  
  .coords-debug-container {
    grid-template-columns: 1fr;
    gap: 15px;
  }
}
</style>
