<template>
  <section class="section container">
    <div v-if="loading">Loading…</div>
    <p v-else-if="error" class="error">加载失败：{{ error }}</p>

    <article v-else-if="plant" class="detail">
      <div class="media">
        <img :src="coverUrl" :alt="plant.common_name" />
      </div>

      <div class="meta">
        <h1 class="title">{{ plant.common_name }}</h1>
        <p class="latin">{{ plant.scientific_name }}</p>
        <p v-if="renderOther(plant.other_name)" class="aka">aka: {{ renderOther(plant.other_name) }}</p>

        <div class="facts">
          <p v-if="plant.watering"><strong>Watering: </strong>{{ plant.watering }}</p>
          <p v-if="plant.plant_cycle"><strong>Cycle: </strong>{{ plant.plant_cycle }}</p>
          <p v-if="plant.growth_rate"><strong>Growth: </strong>{{ plant.growth_rate }}</p>
          <p v-if="plant.sun_expose"><strong>Sun: </strong>{{ renderOther(plant.sun_expose as any) }}</p>
        </div>

        <p v-if="plant.description" class="desc">
          {{ plant.description?.description || plant.description?.brief || plant.description?.summary || '' }}
        </p>

        <!-- ✅ 分布图 iframe -->
        <section v-if="plant.distribution_map?.distribution_map_html" class="block">
          <h3>Distribution Map</h3>
          <iframe
            class="distmap-frame"
            :srcdoc="plant.distribution_map.distribution_map_html"
            sandbox="allow-scripts allow-same-origin"
          ></iframe>
        </section>

        <RouterLink class="btn btn-ghost" to="/garden">Back</RouterLink>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getPlantById, type PlantDetail, type Plant } from '@/api/plants'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const plant = ref<PlantDetail | null>(null)

const preload = (route as any).state?.preload as Plant | undefined

const coverUrl = computed(() => {
  if (plant.value?.image_urls?.length) return plant.value.image_urls[0]
  return preload?.image_url || ''
})

function renderOther(v?: string[] | string) {
  return Array.isArray(v) ? v.join(', ') : (v || '')
}

onMounted(async () => {
  loading.value = true
  error.value = ''

  if (preload) {
    plant.value = {
      general_plant_id: preload.general_plant_id,
      common_name: preload.common_name,
      scientific_name: preload.scientific_name,
      other_name: preload.other_name,
      image_urls: preload.image_url ? [preload.image_url] : []
    } as PlantDetail
  }

  try {
    const idParam = route.params.id
    const id = typeof idParam === 'string' ? parseInt(idParam, 10) : Number(idParam)
    const data = await getPlantById(id)
    plant.value = data
  } catch (e: any) {
    if (!preload) error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail {
  display: grid;
  gap: 1.25rem;
  grid-template-columns: 1.1fr .9fr;
  align-items: start;
}
@media (max-width:900px){
  .detail { grid-template-columns:1fr }
}
.media img {
  width: 100%;
  border-radius: 12px;
  object-fit: cover;
}
.title { margin:.25rem 0 }
.latin { color: var(--muted); font-style: italic }
.aka { color: var(--muted); margin:.25rem 0 }
.desc { margin-top:.75rem; line-height:1.6 }
.error { color:#c00 }

/* ✅ 分布图 iframe 样式 */
.distmap-frame {
  width: 100%;
  height: 400px;
  border: none;
  border-radius: 8px;
  margin-top: 1rem;
}


</style>
