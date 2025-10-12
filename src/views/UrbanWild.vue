<script setup>
import { ref } from 'vue'
import UrbanMap from '@/views/UrbanMap.vue'

defineOptions({ name: 'UrbanWild' })

</script>

<template>
  <section class="container">
    <h2 class="title">Urban & Wild</h2>
    <p class="lead">
      Explore native and resilient species in urban and wild landscapes, supporting biodiversity and climate resilience.
    </p>
  </section>

  <!-- Map -->
  <section class="container">
    <div class="section-box">
      <h2>Tree Distribution Map</h2>
      <p>Click inside the CBD box or use search to explore trees in that area.</p>
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
</style>
