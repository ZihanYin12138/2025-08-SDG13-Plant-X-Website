<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import UrbanMap from '@/views/UrbanMap.vue'

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

  <section class="container">
      <h2 class="title">Urban & Wild</h2>
      <p class="lead">
        Explore native and resilient species in urban and wild landscapes, supporting biodiversity and climate resilience.
      </p>
  </section>


  <!-- Map Component -->
  <section class="container">
    <div class="section-box">
      <h2>Tree Distribution Map</h2>
      <p>Click anywhere on the map (Melbourne CBD Area) or use the search function to explore trees in that area.</p>
      <UrbanMap
        ref="mapRef"
        @map-click="handleMapClick"
        @api-response="handleApiResponse"
      />
    </div>
  </section>


</template>

<style scoped>
.section-box{
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  background: transparent;
}

.divider-red {
  border: 0;
  height: 3px;
  background: linear-gradient(90deg, #ff3b3b, #ff9a3b);
  margin: 0;
}
</style>
