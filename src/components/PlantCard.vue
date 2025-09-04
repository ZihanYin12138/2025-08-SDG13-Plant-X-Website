<template>
  <!-- 仅展示，不包含 RouterLink（外层由父级包） -->
  <div class="plant" role="article">
    <div class="thumb" :style="thumbStyle()"></div>
    <h4 class="title">{{ plant.common_name || 'Unknown' }}</h4>
    <p class="latin">{{ plant.scientific_name || '' }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import threatenedImg from '@/assets/placeholder.jpg'   // ← 与详情页同一张

type GeneralCard = {
  id_type?: 'general'
  general_plant_id?: number
  common_name?: string
  scientific_name?: string
  image_url?: string | null
  other_name?: string[] | string
}
type ThreatCard = {
  id_type?: 'threatened'
  threatened_plant_id?: number
  common_name?: string
  scientific_name?: string
  image_url?: string | null
}
type Plant = GeneralCard | ThreatCard
const props = defineProps<{ plant: Plant }>()

const coverUrl = computed(() => {
  const isThreatened = (props.plant as any)?.id_type === 'threatened'
  if (isThreatened) return threatenedImg
  const u = (props.plant as any)?.image_url
  return (u && String(u).trim()) || threatenedImg    // general：正常用后端图
})

function thumbStyle() {
  const bg = coverUrl.value
    ? `url('${coverUrl.value}')`
    : 'linear-gradient(135deg, color-mix(in oklab, var(--fg) 8%, transparent), color-mix(in oklab, var(--fg) 16%, transparent))'
  return {
    backgroundImage: bg,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    aspectRatio: '4 / 3',
    borderRadius: '10px',
  } as const
}
</script>

<style scoped>
.plant{
  display:block;
  background:var(--card);
  box-shadow:var(--shadow-sm);
  border-radius:14px;
  padding:.8rem;
  color:inherit;
  text-decoration:none;
  height: 300px;
}
.title{ margin:.25rem 0; font-size: 1rem; line-height: 1.2; }
.latin{ color:var(--muted); font-size:.9rem; }
.thumb{ margin-bottom:.5rem; }
</style>
