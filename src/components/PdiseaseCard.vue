<!-- src/components/PdiseaseCard.vue -->
<template>
  <div class="disease-card" role="article">
    <div class="thumb" :style="thumbStyle"></div>
    <h4 class="title">{{ disease.name || disease.common_name || 'Unknown disease' }}</h4>
    <p class="latin">{{ disease.scientific_name || '' }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import placeholder from '@/assets/placeholder.jpg'

const props = defineProps({
  disease: { type: Object, required: true }
})

/** 取第一张可用图，没有就用占位图 */
const cover = computed(() => {
  const arr = Array.isArray(props.disease.images) ? props.disease.images : []
  const first = arr.find(u => typeof u === 'string' && u.trim().length)
  return first || placeholder
})

/** 用 background-image，避免 <img> 404 的破图图标 */
const thumbStyle = computed(() => ({
  backgroundImage: `url("${cover.value}")`,
  backgroundSize: 'cover',
  backgroundPosition: 'center'
}))
</script>

<style scoped>
.disease-card{
  display:block;
  background:var(--card);
  box-shadow:var(--shadow-sm);
  border-radius:14px;
  padding:.8rem;
  color:inherit;
  text-decoration:none;
  height: 300px;                    /* 和 Plant 卡片一致的高度 */
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease, background-color .18s ease;
}

/* 避免被任何全局 .btn / .searchbar__input 等样式污染 */
.disease-card :is(input, button, a){ all: revert-layer; }

.disease-card:hover{
  transform: translateY(-4px);
  box-shadow: 0 14px 28px rgba(2,6,23,.14);
  border-color: color-mix(in oklab, var(--brand) 45%, transparent);
}
.disease-card:focus-within{
  outline: var(--ring);
  outline-offset: 2px;
}

.thumb{
  margin-bottom:.5rem;
  border-radius:10px;
  overflow:hidden;
  aspect-ratio: 4 / 3;             /* 保证缩略图比例稳定 */
  background-color: var(--surface); /* 即使无图也占位 */
}

.title{ margin:.25rem 0; font-size: 1rem; line-height: 1.2; }
.latin{ color:var(--muted); font-size:.9rem; }

@media (prefers-reduced-motion: reduce){
  .disease-card { transition: none; }
}
</style>
