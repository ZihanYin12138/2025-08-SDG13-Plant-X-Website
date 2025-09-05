<!-- src/views/GardenPage.vue -->
<template>
  <section class="container">
    <h2 class="title">Garden</h2>
    <p class="lead">
      Tools and tips for climate-adaptive home gardening — sunlight, soil, watering, composting, and more.
    </p>
    <p>
      Plant recognization though + button at right side of search Box. Size of Image upload can not larger than 3MB.
    </p>
  </section>


  <section class="container">
    <!-- 搜索栏 -->
    <div class="searchbar">
      <div class="searchbar__box">
        <input
          class="searchbar__input"
          :placeholder="placeholder"
          v-model="query"
          @keyup.enter="onSearch"
        />

        <span class="searchbar__icon-left">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="7" />
            <path d="M20 20l-3.5-3.5" />
          </svg>
        </span>

        <div class="searchbar__icon-rights">
          <!-- 语音按钮 -->
          <button
            v-if="speechSupported"
            class="icon-btn"
            :class="{ 'icon-btn--active': listening }"
            :title="listening ? '正在聆听…' : '语音搜索'"
            @click="startVoice"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Z"/>
              <path d="M19 11a7 7 0 0 1-14 0" fill="none" stroke="currentColor" stroke-width="1.5"/>
              <path d="M12 18v3" fill="none" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </button>

          <!-- 上传图片 -->
          <label class="icon-btn" title="上传图片">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14" />
            </svg>
            <input type="file" accept="image/*" hidden @change="onImageChange" />
          </label>
        </div>
      </div>

      <button class="btn" @click="open = true">Filter</button>
    </div>

    <!-- 图片预览 -->
    <div v-if="previewUrl" class="preview">
      <img :src="previewUrl" alt="preview" />
      <span class="preview__name">{{ previewName }}</span>
      <button class="link" @click="clearPreview">Remove</button>
    </div>

    <!-- 弹窗 Filter -->
    <div v-if="open" class="modal-mask" @keydown.esc="open = false">
      <div class="modal" role="dialog" aria-modal="true">
        <div class="modal__head">
          <div class="modal__title">Filter</div>
          <button class="modal__close" @click="open = false">✕</button>
        </div>

        <div class="modal__body">
          <div class="grid-2">
            <!-- 过滤项：保持与后端一致（已移除 rare） -->
            <div class="field">
              <label>Threatened Plants</label>
              <div class="radios">
                <label><input type="radio" value="yes" v-model="filters.threatened"> Yes, I want to help with threatened !</label>
                <label><input type="radio" value="no"  v-model="filters.threatened"> No, I want to see general plants !</label>
              </div>
            </div>

            <div class="field"></div>

            <div class="field">
              <label>Edible</label>
              <div class="radios">
                <label><input type="radio" value="yes" v-model="filters.edible"> Yes</label>
                <label><input type="radio" value="no"  v-model="filters.edible"> No</label>
              </div>
            </div>

            <div class="field">
              <label>Medicinal</label>
              <div class="radios">
                <label><input type="radio" value="yes" v-model="filters.medicinal"> Yes</label>
                <label><input type="radio" value="no"  v-model="filters.medicinal"> No</label>
              </div>
            </div>

            <div class="field">
              <label>Fruits</label>
              <div class="radios">
                <label><input type="radio" value="yes" v-model="filters.fruits"> Yes</label>
                <label><input type="radio" value="no"  v-model="filters.fruits"> No</label>
              </div>
            </div>

            <div class="field">
              <label>Indoors</label>
              <div class="radios">
                <label><input type="radio" value="yes" v-model="filters.indoors"> Yes</label>
                <label><input type="radio" value="no"  v-model="filters.indoors"> No</label>
              </div>
            </div>

            <div class="field">
              <label>Flowers</label>
              <div class="radios">
                <label><input type="radio" value="yes" v-model="filters.flowers"> Yes</label>
                <label><input type="radio" value="no"  v-model="filters.flowers"> No</label>
              </div>
            </div>

            <div class="field">
              <label>Poisonous</label>
              <div class="radios">
                <label><input type="radio" value="yes" v-model="filters.poisonous"> Yes</label>
                <label><input type="radio" value="no"  v-model="filters.poisonous"> No</label>
              </div>
            </div>

            <div class="field">
              <label>Sun Exposure</label>
              <select class="select" v-model="filters.sun">
                <option value="">Choose</option>
                <option value="full shade">Full Shade</option>
                <option value="part shade">Part Shade</option>
                <option value="full sun">Full Sun</option>
              </select>
            </div>

            <div class="field">
              <label>Watering</label>
              <select class="select" v-model="filters.watering">
                <option value="">Choose</option>
                <option value="frequent">Frequent</option>
                <option value="average">Average</option>
                <option value="minimal">Minimal</option>
              </select>
            </div>

            <div class="field">
              <label>Plant Cycle</label>
              <select class="select" v-model="filters.cycle">
                <option value="">Select</option>
                <option value="annual">Annual</option>
                <option value="perennial">Perennial</option>
                <option value="biennial">Biennial</option>
              </select>
            </div>

            <div class="field">
              <label>Growth Rate</label>
              <select class="select" v-model="filters.growth">
                <option value="">Choose</option>
                <option value="slow">Slow</option>
                <option value="moderate">Moderate</option>
                <option value="fast">Fast</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal__foot">
          <button class="link" @click="resetFilters">Reset</button>
          <div>
            <button class="btn" @click="applyFilters">Apply Filter</button>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- 植物卡 -->
  <!-- 植物卡 -->
<section class="container">
  <div class="plants-grid">
    <template v-if="loading">
      <PlantCardSkeleton v-for="n in 8" :key="'s' + n" />
    </template>

    <p v-else-if="error" class="error">fail to load：{{ error }}</p>

    <template v-else>
      <RouterLink
        v-for="p in safePlants"
        :key="p.id_type === 'general' ? `g-${p.general_plant_id}` : `t-${p.threatened_plant_id}`"
        :to="toFor(p)"                         
        style="text-decoration: none;"
      >
        <PlantCard :plant="p" />
      </RouterLink>
    </template>
  </div>
</section>

</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import {
  searchPlants,
  getPlantById,
  type PlantDetail,
  type PlantCardItem
} from '@/api/plants'
import PlantCard from '@/components/PlantCard.vue'
import PlantCardSkeleton from '@/components/PlantCardSkeleton.vue'
import { uploadImage, predictByS3Key } from '@/api/uploads'

const MAX_CARDS = 8

const placeholder = 'Search For A Plant'
const query = ref('')
const open = ref(false)
const loading = ref(false)
const error = ref('')

/** 后端可能返回两种卡片形态（general/threatened） */
const plants = ref<PlantCardItem[]>([])

/** 过滤项（移除 rare，保持与后端映射一致） */
const filters = reactive({
  threatened: '',
  edible: '',
  medicinal: '',
  fruits: '',
  indoors: '',
  poisonous: '',
  flowers: '',
  sun: '',
  watering: '',
  cycle: '',
  growth: ''
})

function normalizePreload(p: any) {
  return {
    // 两种类型的关键字段都带上，详情页会择需使用
    general_plant_id: p.general_plant_id ?? undefined,
    threatened_plant_id: p.threatened_plant_id ?? undefined,
    common_name: p.common_name || '',
    scientific_name: p.scientific_name || '',
    image_url: p.image_url || '',
    other_name: p.other_name || []
  }
}

function toFor(p: any) {
  if (p?.id_type === 'threatened' && Number.isFinite(p.threatened_plant_id)) {
    return {
      name: 'PlantDetail',
      params: { id: p.threatened_plant_id },
      query: { type: 'threatened' },          // ★ 告诉详情页这是 threatened
      state: { preload: normalizePreload(p) }  // ★ 传预加载数据，秒开
    }
  }
  if (p?.id_type === 'general' && Number.isFinite(p.general_plant_id)) {
    return {
      name: 'PlantDetail',
      params: { id: p.general_plant_id },
      query: { type: 'general' },             // ★ 告诉详情页这是 general
      state: { preload: normalizePreload(p) }  // ★ 同样传预加载
    }
  }
  // 兜底，避免 :to 为空
  return { path: '/' }
}

/** 仅渲染有有效 ID 的卡片，避免报 “Missing required param id” */
const safePlants = computed(() =>
  (plants.value || []).filter(p =>
    p && (
      (p.id_type === 'general' && Number.isFinite((p as any).general_plant_id)) ||
      (p.id_type === 'threatened' && Number.isFinite((p as any).threatened_plant_id))
    )
  ).slice(0, MAX_CARDS)
)

/** 统一搜索（关键词 + 过滤） */
async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await searchPlants({
      search: query.value,
      page: 1,
      page_size: MAX_CARDS,
      filters: { ...filters }
    })
    plants.value = (res.items || []).slice(0, MAX_CARDS)
  } catch (e: any) {
    error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}
const onSearch = () => load()
const resetFilters = () => { Object.keys(filters).forEach(k => (filters as any)[k] = '') }
const applyFilters = () => { open.value = false; load() }

/** 语音识别 */
const listening = ref(false)
const speechSupported = typeof window !== 'undefined' && 'webkitSpeechRecognition' in window
let recognizer: any = null
onMounted(() => {
  if (!speechSupported) return
  const SR = (window as any).webkitSpeechRecognition
  const rec = new SR()
  rec.continuous = false
  rec.interimResults = false
  rec.lang = 'zh-CN'
  rec.onresult = (e: any) => {
    const t = Array.from(e.results).map((r: any) => r[0].transcript).join(' ')
    query.value = (query.value ? query.value + ' ' : '') + t
  }
  rec.onstart = () => (listening.value = true)
  rec.onend = () => (listening.value = false)
  recognizer = rec
})
const startVoice = () => recognizer && recognizer.start()

/** 图片上传 & 识别 → 用识别结果刷新列表 */
const previewUrl = ref('')
const previewName = ref('')
const clearPreview = () => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
  previewName.value = ''
}

const onImageChange = async (ev: Event) => {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  // 预览
  previewName.value = file.name
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = URL.createObjectURL(file)

  loading.value = true
  error.value = ''

  try {
    const up = await uploadImage(file)
    const key = up.key

    const pred = await predictByS3Key(key, 8)
    const ids = (pred.results || [])
      .filter(r => r && typeof r.plant_id === 'number')
      .map(r => r.plant_id)

    if (!ids.length) {
      plants.value = []
      error.value = '未识别到可用候选'
      return
    }

    const details = await Promise.all(
      ids.slice(0, MAX_CARDS).map(id => getPlantById(id).catch(() => null))
    ) as (PlantDetail | null)[]

    plants.value = details
      .filter((d): d is PlantDetail => !!d)
      .map(d => ({
        id_type: 'general',
        general_plant_id: d.general_plant_id,
        common_name: d.common_name,
        scientific_name: d.scientific_name,
        image_url: (d.image_urls && d.image_urls[0]) || ''
      }))

    query.value = `#${ids.join(',')}`
  } catch (e: any) {
    error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}

/** 首次进入：展示 8 条 */
onMounted(load)
</script>

<style scoped>
/* —— 页面块 —— */
.title { margin: 0 0 .5rem; }
.lead { color: var(--muted); }

/* ====== 搜索条 ====== */
.searchbar {
  position: relative;
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}
.searchbar__box { position: relative; flex: 1; }

.searchbar__input {
  width: 100%;
  height: 48px;
  box-sizing: border-box;
  border-radius: 999px;
  border: 2px solid var(--border);
  padding: 0 112px 0 44px;
  outline: none;
  box-shadow: var(--shadow-sm);
  background: var(--card);
  color: var(--fg);
}
.searchbar__input:focus-visible {
  outline: var(--ring);
  box-shadow: none;
}
.searchbar__icon-left {
  position: absolute; inset: 0 auto 0 14px;
  display: grid; place-items: center;
  color: var(--muted); pointer-events: none;
}
.searchbar__icon-rights {
  position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
  display: flex; gap: 4px; align-items: center;
}

/* ====== 按钮（本页的 Filter/图标按钮） ====== */
.icon-btn {
  width: 36px; height: 36px; display: grid; place-items: center;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--fg);
  cursor: pointer;
}
.icon-btn:hover { background: var(--hover); }
.icon-btn--active { box-shadow: 0 0 0 2px color-mix(in oklab, var(--brand) 50%, transparent) inset; }

/* 若你继续使用“Filter”这个 .btn（不改模板类名），让它跟随主题 */
.btn {
  height: 48px; padding: 0 18px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--fg);
  cursor: pointer;
  box-shadow: var(--shadow-sm);
}
.btn:disabled { opacity: .6; cursor: not-allowed; }
.btn:hover { background: var(--hover); }

/* ====== 预览 ====== */
.preview {
  display: flex; align-items: center; gap: 10px;
  margin: 8px 0 16px;
  color: var(--muted);
}
.preview img { width: 44px; height: 44px; object-fit: cover; border-radius: 8px; }
.preview__name { max-width: 40vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.link { color: var(--muted); background: none; border: none; cursor: pointer; }

/* ====== 弹窗 ====== */
.modal-mask {
  position: fixed; inset: 0;
  background: var(--backdrop);
  display: grid; place-items: start center; padding-top: 48px; z-index: 50;
}
.modal {
  width: 840px; max-width: 95vw; max-height: 80vh;
  display: flex; flex-direction: column;
  background: var(--card);
  border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-md);
}
.modal__body { flex: 1; overflow-y: auto; padding: 20px 24px; }
.modal__head, .modal__foot {
  padding: 16px 24px; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid var(--border);
}
.modal__foot { border-top: 1px solid var(--border); border-bottom: none; }
.modal__title { font-size: 18px; font-weight: 600; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 22px 40px; }
.field label { font-weight: 600; display: block; margin-bottom: 6px; }
.radios { display: grid; gap: 6px; color: var(--fg); }
.select {
  width: 100%; height: 40px;
  border: 1px solid var(--border);
  border-radius: 10px; padding: 0 12px;
  background: var(--surface);
  color: var(--fg);
}

/* ====== 卡片网格 ====== */
.plants-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(4, 1fr);
}
@media (max-width: 768px) { .plants-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .plants-grid { grid-template-columns: 1fr; } }

/* 错误信息 */
.error{ color:#c00; margin-top:8px }
</style>
