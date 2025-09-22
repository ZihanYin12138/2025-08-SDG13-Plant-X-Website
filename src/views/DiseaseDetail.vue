<!-- src/views/DiseaseDetail.vue -->
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDiseaseById } from '@/api/pdisease'
import fallbackImg from '@/assets/placeholder.jpg'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref('')
const disease = ref(null)

/** 预载（来自列表 RouterLink 的 state: { preload }） */
const preload = (() => {
  const s = (route).state?.preload ?? (window?.history?.state)?.preload
  return s
})()
if (preload) {
  disease.value = preload
  loading.value = false
}

const PLACEHOLDER_IMG =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="600">
      <rect fill="#f3f4f6" width="100%" height="100%"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            fill="#9ca3af" font-family="system-ui" font-size="24">No image</text>
    </svg>`
  )

/** 名称与图片（字段兼容） */
const displayName = computed(() => disease.value?.name || disease.value?.common_name || '')
const sciName = computed(() => disease.value?.scientific_name || '')

const allImages = computed(() => {
  const d = disease.value || {}
  const a = Array.isArray(d.images) ? d.images : []
  const b = Array.isArray(d.regular_url_images) ? d.regular_url_images : []
  const merged = [...a, ...b].filter(Boolean)
  return merged.length ? Array.from(new Set(merged)) : []
})

const coverUrl = ref('')
const setCover = (src) => { coverUrl.value = src || fallbackImg || PLACEHOLDER_IMG }
watch(allImages, (imgs) => setCover(imgs[0]), { immediate: true })

/** 兼容/抽取文段 */
const toText = (v) => Array.isArray(v) ? v.filter(Boolean).join(', ') : (v || '')

/** 从数组 description[] 中，找到 “概览/机理” 文段（没有 symptoms 时用于右侧显示） */
const overviewText = computed(() => {
  const d = disease.value || {}
  if (Array.isArray(d.description) && d.description.length) {
    // 优先标题里含有 "What is" 的条目，否则取第一条
    const hit = d.description.find(s => /what\s+is/i.test(s?.subtitle || '')) || d.description[0]
    return hit?.description || ''
  }
  return ''
})

/** Symptoms：若无字段，则右侧用 Overview 占位，避免空白 */
const symptomsText = computed(() => {
  const d = disease.value || {}
  if (d.symptoms) return d.symptoms
  // 一些数据源会把 “症状” 混在 description 里，这里不强行猜测；用 overview 作为替代展示
  return overviewText.value
})

/** Diagnosis：优先 diagnosis 字段；否则从 description[] 里找 “How … occur/does …” 的条目 */
const diagnosisText = computed(() => {
  const d = disease.value || {}
  if (d.diagnosis) return d.diagnosis
  if (Array.isArray(d.description)) {
    const hit = d.description.find(s =>
      /how\b.*(occur|does|do)/i.test(s?.subtitle || '')
    )
    if (hit?.description) return hit.description
  }
  return ''
})

/** Solutions：拆分为管理类 & 化学类两个盒子；并兼容 legacy 字段 */
const solutionArray = computed(() => {
  const d = disease.value || {}
  return Array.isArray(d.solution) ? d.solution : []
})
const mgmtKeywords = [
  'cultural', 'practice', 'management', 'improve', 'drainage', 'avoid watering at night',
  'resistant', 'nitrogen', 'biofumigant', 'prune', 'air circulation', 'monitor', 'remove'
]
const chemKeywords = [
  'chemical', 'fungicide', 'antibiotic', 'bactericide', 'copper', 'chlorothalonil',
  'mancozeb', 'myclobutanil', 'azoxystrobin', 'mefenoxam', 'propiconazole', 'thiophanate'
]

function isChemEntry(s) {
  const t = (s?.subtitle || '').toLowerCase()
  const b = (s?.description || '').toLowerCase()
  return chemKeywords.some(k => t.includes(k) || b.includes(k))
}

const treatmentMgmtText = computed(() => {
  const d = disease.value || {}
  let blocks = []
  if (solutionArray.value.length) {
    const mgmt = solutionArray.value.filter(s => !isChemEntry(s))
    blocks = mgmt.map(s => `• ${s.subtitle || ''}\n${s.description || ''}`.trim())
  } else if (d.treatment) {
    blocks = [d.treatment]
  }
  if (d.prevention) {
    blocks.push(d.prevention) // 预防也归到管理类里一起显示
  }
  return blocks.filter(Boolean).join('\n\n')
})

const chemicalTreatText = computed(() => {
  const d = disease.value || {}
  if (solutionArray.value.length) {
    const chem = solutionArray.value.filter(isChemEntry)
    if (chem.length) {
      return chem.map(s => `• ${s.subtitle || ''}\n${s.description || ''}`.trim()).join('\n\n')
    }
  }
  // 兼容一些“化学/药剂”风格的小标题
  if (/antibiotic|bactericide|copper|fungicide/i.test(d.treatment || '')) {
    return d.treatment
  }
  return ''
})

/** 返回列表（回到 Garden 的 diseases 区域） */
function backToList() {
  router.push({ name: 'Garden', query: { tab: 'disease' } })
}

/** 加载详情 */
onMounted(async () => {
  try {
    const idParam = route.params.id
    const id = typeof idParam === 'string' ? idParam : String(idParam)
    const fresh = await getDiseaseById(id)
    disease.value = fresh
    error.value = ''
    // 刷新首图
    setCover(allImages.value[0])
  } catch (e) {
    if (!preload) error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="section container">
    <!-- 面包屑 -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <RouterLink class="breadcrumb__link" :to="{ name: 'Garden', query: { tab: 'disease' } }">Diseases</RouterLink>
      <span class="breadcrumb__sep">›</span>
      <span class="breadcrumb__current">{{ displayName || '...' }}</span>
    </nav>

    <div v-if="!preload && loading">Loading…</div>
    <p v-else-if="!preload && error" class="error">Load fail：{{ error }}</p>

    <article v-else-if="disease" class="detail">
      <!-- 上半区：左图 / 右侧 Symptoms -->
      <div class="top-grid">
        <!-- 左侧：原始比例的图片 + 全部缩略图 -->
        <aside class="media">
          <div class="hero-img-wrap">
            <img :src="coverUrl || PLACEHOLDER_IMG" :alt="displayName || 'Disease photo'" />
          </div>

          <div v-if="allImages.length > 1" class="thumbs">
            <div class="thumbs__rail">
              <img
                v-for="(src, i) in allImages.slice(1)"
                :key="i"
                :src="src"
                :alt="`${displayName} ${i+2}`"
                @click="setCover(src)"
              />
            </div>
          </div>
        </aside>

        <!-- 右侧：名称 + 学名（无卡片） + Symptoms 文本 -->
        <section class="side">
          <h1 class="title">{{ displayName }}</h1>
          <p v-if="sciName" class="latin">{{ sciName }}</p>

          <div class="card">
            <h3>{{ disease?.symptoms ? 'Symptoms' : 'Overview' }}</h3>
            <p class="preline" v-if="symptomsText">{{ symptomsText }}</p>
            <p v-else class="muted">No data.</p>
          </div>
        </section>
      </div>

      <!-- 下半区：独立卡片（诊断 / 管理治疗 / 化学治疗） -->
      <section v-if="diagnosisText" class="card">
        <h3 class="card__title">Diagnosis / Identification</h3>
        <p class="preline">{{ diagnosisText }}</p>
      </section>

      <section v-if="treatmentMgmtText" class="card">
        <h3 class="card__title">Treatment / Management</h3>
        <p class="preline">{{ treatmentMgmtText }}</p>
      </section>

    </article>
  </section>

  <div class="center">
    <button class="btn" @click="backToList">← Back to Diseases</button>
  </div>
</template>

<style scoped>
/* 面包屑 */
.breadcrumb {
  display: flex; align-items: center; gap: .5rem;
  margin: 4px 0 12px; font-size: 14px;
}
.breadcrumb__link { color: var(--fg); font-weight: 700; text-decoration: none; }
.breadcrumb__link:hover { text-decoration: underline; }
.breadcrumb__sep { color: var(--muted); }
.breadcrumb__current { color: var(--fg); }

/* 上半区两栏 */
.top-grid{
  display:grid;
  gap:1rem;
  grid-template-columns: 0.8fr 1fr;
  align-items:start;
}
@media (max-width: 980px){ .top-grid{ grid-template-columns:1fr } }

/* 左侧媒体：图片按原本大小（保持比例），不裁切不限制高度 */
.hero-img-wrap img{
  display:block;
  max-width: 100%;
  height: auto;        /* ✅ 原始比例，不裁切 */
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  box-shadow: var(--shadow-sm);
}

/* 缩略图横向滚动，显示全部 */
.thumbs {
  margin-top: .6rem;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--card);
  box-shadow: var(--shadow-sm);
  padding: .4rem;
  overflow: hidden;
}
.thumbs__rail{
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 140px;
  gap: .5rem;
  overflow-x: auto;
  padding-bottom: .2rem;
  scrollbar-width: thin;
}
.thumbs__rail img{
  width: 100%;
  height: auto;
  aspect-ratio: 4/3;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid var(--border);
  transition: transform .15s ease;
}
.thumbs__rail img:hover { transform: translateY(-2px); }

/* 右侧信息：不加外框，仅块级标题+正文 */
.side .title{ margin:.25rem 0 }
.latin{ color:var(--muted); font-style:italic; margin: 4px 0 8px; }
.blk{ margin-top: .6rem; }
.blk h3{ margin: 0 0 .35rem; }

/* 下方独立卡片 */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: var(--shadow-sm);
  margin-top: 12px;
}
.card__title { margin: 0 0 6px; }

/* 文本保留换行与项目符号 */
.preline { white-space: pre-line; }
.muted { color: var(--muted); }

.error{ color:#c00; }

.center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50px;
}
</style>
