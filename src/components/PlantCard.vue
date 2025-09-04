<template>
  <RouterLink
    class="plant"
    :to="{ name: 'PlantDetail', params: { id: plant.general_plant_id }, state: { preload: plant } }"
  >
    <div class="thumb" :style="thumbStyle(plant.image_url)" />
    <h4 class="title">{{ plant.common_name }}</h4>
    <p class="latin">{{ plant.scientific_name }}</p>
  </RouterLink>
</template>

<script setup lang="ts">
type Plant = {
  general_plant_id: number
  common_name: string
  scientific_name: string
  image_url: string
  other_name?: string[] | string
}
defineProps<{ plant: Plant }>()

function thumbStyle(url: string) {
  return {
    backgroundImage: `url('${url}')`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    aspectRatio: '4/3',
    borderRadius: '10px',
  } as any
}
</script>

<style scoped>
.plant{display:block;background:var(--card);box-shadow:var(--shadow);border-radius:14px;padding:.8rem;color:inherit;text-decoration:none}
.title{margin:.25rem 0}
.latin{color:var(--muted);font-size:.9rem}
.thumb{margin-bottom:.5rem}
</style>
