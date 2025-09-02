<template>
  <article class="plant" @click="$emit('click', plant)">
    <div class="thumb" :style="thumbStyle(plant.image_url)" :aria-label="`${plant.common_name} image`"></div>
    <h4 class="title">{{ plant.common_name }}</h4>
    <p class="latin">{{ plant.scientific_name }}</p>
    <p v-if="aka" class="aka">aka: {{ aka }}</p>
  </article>
</template>

<script setup lang="ts">
type Plant = {
  id: number
  common_name: string
  scientific_name: string
  other_name?: string[] | string
  image_url: string
}
const props = defineProps<{ plant: Plant }>()
const aka = Array.isArray(props.plant.other_name)
  ? props.plant.other_name.join(', ')
  : (props.plant.other_name || '')

function thumbStyle(url: string) {
  return {
    backgroundImage: `url('${url}')`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    aspectRatio: '4 / 3',
    borderRadius: '8px'
  } as any
}
</script>

<style scoped>
.plant { display: grid; gap: .25rem; cursor: pointer; }
.thumb { width: 100%; background: #eee; }
.title { margin: .25rem 0 0; }
.latin { color: #666; font-style: italic; }
.aka { color: #777; font-size: .9rem; }
</style>
