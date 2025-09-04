<template>
  <section class="section">
    <div class="container">
      <h2 class="title">Garden</h2>
      <p class="lead">
        Tools and tips for climate-adaptive home gardening — sunlight, soil, watering, composting, and more.
      </p>

      <div class="page">
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
          <button class="link" @click="clearPreview">移除</button>
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
                <!-- 11 个 filter 控件 -->
                <div class="field">
                  <label>Threatened Plants</label>
                  <div class="radios">
                    <label><input type="radio" value="yes" v-model="filters.threatened"> Yes</label>
                    <label><input type="radio" value="no"  v-model="filters.threatened"> No</label>
                    <label><input type="radio" value="all" v-model="filters.threatened"> All</label>
                  </div>
                </div>

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
                  <label>Rare</label>
                  <div class="radios">
                    <label><input type="radio" value="yes" v-model="filters.rare"> Yes</label>
                    <label><input type="radio" value="no"  v-model="filters.rare"> No</label>
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

        <!-- 植物卡 -->
        <div class="plants-grid" style="margin-top: 12px;">
  <template v-if="loading">
    <PlantCardSkeleton v-for="n in 8" :key="'s' + n" />
  </template>

  <p v-else-if="error" class="error">加载失败：{{ error }}</p>

  <!-- ✅ v-else 放在 template，内部再 v-for -->
  <template v-else>
    <RouterLink
      v-for="p in plants"
      :key="p.general_plant_id"
      :to="{ 
        name: 'PlantDetail', 
        params: { id: p.general_plant_id }, 
        state: { preload: p }   // 传给详情页做兜底
      }"
      style="text-decoration: none;"
    >
      <PlantCard :plant="p" />
    </RouterLink>
  </template>
</div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { searchPlants, type Plant } from '@/api/plants'
import PlantCard from '@/components/PlantCard.vue'
import PlantCardSkeleton from '@/components/PlantCardSkeleton.vue'
import { presignUpload } from '@/api/uploads'
import { apiPost } from '@/api/http'

const placeholder = 'Search For A Plant'
const query = ref('')
const open = ref(false)
const loading = ref(false)
const error = ref('')
const plants = ref<Plant[]>([])

/** 11 个 Filter（与后端映射在 searchPlants 里完成） */
const filters = reactive({
  threatened: '',
  edible: '',
  medicinal: '',
  fruits: '',
  indoors: '',
  rare: '',
  flowers: '',
  sun: '',
  watering: '',
  cycle: '',
  growth: ''
})

/** 统一搜索（关键词 + 过滤） */
async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await searchPlants({
      search: query.value,       // 允许为空；内部会把空变成 'a' 兜底，避免 400
      page: 1,
      page_size: 8,
      filters: { ...filters }
    })
    plants.value = res.items || []
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

/** 图片上传 & 识别 → 用识别名再触发一次 load() */
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

  previewName.value = file.name
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = URL.createObjectURL(file)

  loading.value = true
  error.value = ''
  try {
    const { putUrl, key } = await presignUpload({ filename: file.name, contentType: file.type })
    const up = await fetch(putUrl, { method: 'PUT', headers: { 'Content-Type': file.type }, body: file })
    if (!up.ok) throw new Error(`S3 upload failed: ${up.status}`)

    const { candidates } = await apiPost<{ candidates: { name: string; score: number }[] }>('/analyze', { key })
    if (!candidates?.length) {
      plants.value = []
      error.value = '未识别到可用名称'
      return
    }

    const picked = candidates.filter(c => c.score >= 0.75).map(c => c.name)
    const terms = picked.length ? picked : [candidates[0].name]
    query.value = terms.join(', ')
    await load()
  } catch (e: any) {
    error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}

/** 首次进入：展示 8 条（内部会把空搜索兜底成 'a'） */
onMounted(load)
</script>




<style scoped>
/* ====== 基础 ====== */
:root {
  --c-border: #e5e7eb;
  --c-muted: #6b7280;
  --c-text: #111827;
  --c-primary: #10b981;
  --shadow-sm: 0 1px 2px rgba(0,0,0,.06);
  --shadow-md: 0 4px 12px rgba(0,0,0,.08);
}
.page {
  max-width: 1120px;
  margin: 24px auto;
  padding: 0 16px;
  color: var(--c-text);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}

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
  border: 1px solid var(--c-border);
  padding: 0 112px 0 44px; 
  outline: none;
  box-shadow: var(--shadow-sm);
}
.searchbar__input:focus {
  border-color: var(--c-primary);
  box-shadow: 0 0 0 3px rgba(68, 123, 106, 0.2);
}
.searchbar__icon-left {
  position: absolute; inset: 0 auto 0 14px;
  display: grid; place-items: center;
  color: var(--c-muted); pointer-events: none;
}
.searchbar__icon-rights {
  position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
  display: flex; gap: 4px; align-items: center;
}

/* ====== 按钮 ====== */
.icon-btn {
  width: 36px; height: 36px; display: grid; place-items: center;
  border-radius: 50%;
  border: 1px solid transparent;
  cursor: pointer;
}
.icon-btn:hover { background: #f3f4f6; }
.icon-btn--active { box-shadow: 0 0 0 2px rgba(16,185,129,.5) inset; }

.btn {
  height: 48px; padding: 0 18px;
  border-radius: 10px; border: 1px solid transparent;
  background: var(--c-primary); color: #ffffff; cursor: pointer;
  box-shadow: var(--shadow-sm);
  background-color: rgb(113, 226, 226);
}
.btn:disabled { opacity: .6; cursor: not-allowed; }

/* ====== 预览 ====== */
.preview {
  display: flex; align-items: center; gap: 10px;
  margin: 8px 0 16px;
  color: var(--c-muted);
}
.preview img { width: 44px; height: 44px; object-fit: cover; border-radius: 8px; }
.preview__name { max-width: 40vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ====== 弹窗 ====== */
.modal-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,.4);
  display: grid; place-items: start center; padding-top: 48px; z-index: 50;
}
.modal {
  width: 840px;
  max-width: 95vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  background: #262525;
  border-radius: 16px;
  border: 1px solid var(--c-border);
  box-shadow: var(--shadow-md);
}
.modal__body { flex: 1; overflow-y: auto; padding: 20px 24px; }
.modal__head, .modal__foot {
  padding: 16px 24px; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid var(--c-border);
}
.modal__foot { border-top: 1px solid var(--c-border); border-bottom: none; }
.modal__title { font-size: 18px; font-weight: 600; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 22px 40px; }
.field label { font-weight: 600; display: block; margin-bottom: 6px; }
.radios { display: grid; gap: 6px; color: var(--c-text); }
.select { width: 100%; height: 40px; border: 1px solid var(--c-border); border-radius: 10px; padding: 0 12px; background: #342d2d; }
.link { color: var(--c-muted); background: none; border: none; cursor: pointer; }

/* ====== 卡片 ====== */
.plants-grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}
.plant{background:var(--card);box-shadow:var(--shadow);border-radius:14px;padding:.8rem}
.plant .thumb{aspect-ratio:4/3;border-radius:10px;border:2px dashed color-mix(in oklab, var(--fg) 25%, transparent);margin-bottom:.5rem}
.plant h4{margin:.25rem 0}
.plant .latin{color:var(--muted);font-size:.9rem}

.error{color:#c00;margin-top:8px}
</style>
