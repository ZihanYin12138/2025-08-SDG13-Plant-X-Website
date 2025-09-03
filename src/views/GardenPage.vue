

<template>
<section class="section">
<div class="container">
<h2 class="title">Garden</h2>
<p class="lead">
    Tools and tips for climate-adaptive home gardening — sunlight, soil, watering, composting, and more.
</p>


  <div class="page">
    
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
            <circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>
          </svg>
        </span>
        
        <div class="searchbar__icon-rights">
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

          <label class="icon-btn" title="上传图片">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            <input type="file" accept="image/*" hidden @change="onImageChange" />
          </label>
        </div>

        <ul v-if="showSuggest" class="suggest-list">
            <li v-for="s in suggestions" :key="s" @click="selectSuggestion(s)">
            {{ s }}
          </li>
        </ul>
      </div>

      <button class="btn" @click="open = true" >Filter</button>
    </div>

    <!-- pre view -->
    <div v-if="previewUrl" class="preview">
      <img :src="previewUrl" alt="preview" />
      <span class="preview__name">{{ previewName }}</span>
      <button class="link" @click="clearPreview">移除</button>
    </div>

    <!-- popup -->
    <div v-if="open" class="modal-mask" @keydown.esc="open=false">
      <div class="modal" role="dialog" aria-modal="true">
        <div class="modal__head">
          <div class="modal__title">Filter</div>
          <button class="modal__close" @click="open=false">✕</button>
        </div>

        <div class="modal__body">
          <div class="grid-2">
            
            <div class="field">
              <label>Threatened Plants</label>
              <div class="radios">
                <label><input type="radio" value="yes" v-model="filters.poisonous"> Yes, I want to help with threatened Plants !</label>
                <label><input type="radio" value="no" v-model="filters.poisonous"> No, I want to see general plants !</label>
                <label><input type="radio" value="all"  v-model="filters.poisonous"> All</label>
              </div>
            </div>

            <div class="field">

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
                <option value="sun-part shade">Sun-Part Shade</option>
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
                <option value="slow">High</option>
                <option value="moderate">Moderate</option>
                <option value="fast">Low</option>
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
    
    <!--植物卡-->
    <div class="plants-grid" style="margin-top: 12px;">
        <template v-if="loading">
          <PlantCardSkeleton v-for="n in 8" :key="'s'+n" />
        </template>

        <p v-else-if="error" class="error">加载失败：{{ error }}</p>

        <PlantCard v-else v-for="p in plants" :key="p.id" :plant="p" />
    </div>
    
  </div>

</div>

</section>


<!--
<section class="container">
    <header class="toolbar">
      <input
        v-model="search"
        class="input"
        type="search"
        placeholder="Search common / scientific / other name"
        @input="onSearchInput"
      />

      
      <div class="bools">
        <label><input type="checkbox" v-model="filters.if_threatened" /> Threatened</label>
        <label><input type="checkbox" v-model="filters.if_edible" /> Edible</label>
        <label><input type="checkbox" v-model="filters.if_indoors" /> Indoors</label>
        <label><input type="checkbox" v-model="filters.if_medicinal" /> Medicinal</label>
        <label><input type="checkbox" v-model="filters.if_poisonous" /> Poisonous</label>
        <label><input type="checkbox" v-model="filters.if_fruits" /> Fruits</label>
        <label><input type="checkbox" v-model="filters.if_flowers" /> Flowers</label>
      </div>

      
      <select v-model="watering" class="select">
        <option value="">Watering (any)</option>
        <option value="low">Low</option>
        <option value="average">Average</option>
        <option value="frequent">Frequent</option>
      </select>

      <select v-model="plant_cycle" class="select">
        <option value="">Plant cycle (any)</option>
        <option value="annual">Annual</option>
        <option value="perennial">Perennial</option>
        <option value="biennial">Biennial</option>
      </select>

      <select v-model="growth_rate" class="select">
        <option value="">Growth (any)</option>
        <option value="slow">Slow</option>
        <option value="medium">Medium</option>
        <option value="fast">Fast</option>
      </select>

      
      <div class="chipbox">
        <span class="chip" :class="{on:sunExposeSet.has('low')}" @click="toggleSun('low')">Low sun</span>
        <span class="chip" :class="{on:sunExposeSet.has('medium')}" @click="toggleSun('medium')">Medium</span>
        <span class="chip" :class="{on:sunExposeSet.has('high')}" @click="toggleSun('high')">High</span>
      </div>

      <select v-model.number="pageSize" class="select">
        <option :value="24">24 / page</option>
        <option :value="48">48 / page</option>
        <option :value="96">96 / page</option>
      </select>
    </header>

    <div class="plants-grid">
      <template v-if="loading">
        <article v-for="n in pageSize" :key="'s'+n" class="plant skeleton">
          <div class="thumb"></div><h4>&nbsp;</h4><p class="latin">&nbsp;</p>
        </article>
      </template>

      <p v-else-if="error" class="error">加载失败：{{ error }}</p>

      <article v-else v-for="p in items" :key="p.id" class="plant">
        <div class="thumb" :style="thumbStyle(p.image_url)" :aria-label="`${p.common_name} image`"></div>
        <h4 class="title">{{ p.common_name }}</h4>
        <p class="latin">{{ p.scientific_name }}</p>
        <p v-if="renderOther(p.other_name)" class="aka">aka: {{ renderOther(p.other_name) }}</p>
      </article>
    </div>

    <footer class="pager" v-if="total > pageSize">
      <button class="btn" :disabled="page===1" @click="page--">上一页</button>
      <span>{{ page }} / {{ Math.ceil(total / pageSize) }}</span>
      <button class="btn" :disabled="page>=Math.ceil(total/pageSize)" @click="page++">下一页</button>
    </footer>


</section>
-->
</template>



<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { fetchPlants, type Plant } from '@/api/plants'
import PlantCard from '@/components/PlantCard.vue'
import PlantCardSkeleton from '@/components/PlantCardSkeleton.vue'
import { presignUpload } from '@/api/uploads'


/** ====== 基础状态 ====== */
const placeholder = 'Search For A Plant'
const query = ref('')          // 搜索关键词
const open  = ref(false)       // 过滤弹窗
const loading = ref(false)
const error = ref('')
const plants = ref<Plant[]>([])  // ← 模板里使用的 plants 列表

/** ====== 你的过滤控件（保持模板不动） ======
  注意：模板里用的是 poisonous/edible/... 这些 key
  我们在 buildApiParams() 里把它们映射到后端需要的字段名
*/
const filters = reactive({
  // 单选：'yes' | 'no' | 'all' | ''
  poisonous: '',   // 实际业务：Threatened（你写反了名字，但我们用映射修正）
  edible: '',
  medicinal: '',
  fruits: '',
  indoors: '',
  rare: '',
  flowers: '',
  // 下拉
  sun: '',         // 'full shade' | 'sun-part shade' | 'full sun'
  watering: '',    // 'frequent' | 'average' | 'minimal'
  cycle: '',       // 'annual' | 'perennial' | 'biennial'
  growth: ''       // 'slow' | 'moderate' | 'fast'
})

/** ====== 语音搜索（保持你原逻辑） ====== */
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

/** ====搜索框提示 ===== */
const suggestions = ref<string[]>([])
const showSuggest = ref(false)
let suggestTimer: number | null = null

async function fetchSuggestions(q: string) {
  if (!q.trim()) {
    suggestions.value = []
    showSuggest.value = false
    return
  }
  try {
    // 调用后端接口
    const res = await apiGet<{ suggestions: string[] }>('/plants/suggest', { query: q })
    suggestions.value = res.suggestions
    showSuggest.value = res.suggestions.length > 0
  } catch (e) {
    console.error(e)
    suggestions.value = []
    showSuggest.value = false
  }
}

// 输入时，防抖调用
function onInput() {
  if (suggestTimer) clearTimeout(suggestTimer)
  suggestTimer = window.setTimeout(() => {
    fetchSuggestions(query.value)
  }, 300) // 300ms 防抖
}

// 用户选中某个建议
function selectSuggestion(s: string) {
  query.value = s
  showSuggest.value = false
  // 可以立刻搜索
  onSearch()
}



/** ====== 图片预览（保持你原逻辑） ====== */
const previewUrl = ref('')
const previewName = ref('')
const onImageChange = async (ev: Event) => {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  // 预览（你原来的逻辑）
  previewName.value = file.name
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = URL.createObjectURL(file)

  try {
    // 1) 向后端要预签名 URL
    const { putUrl, key } = await presignUpload({ filename: file.name, contentType: file.type })

    // 2) 直传到 S3（PUT）
    const putRes = await fetch(putUrl, {
      method: 'PUT',
      headers: { 'Content-Type': file.type },
      body: file
    })
    if (!putRes.ok) throw new Error(`S3 upload failed: ${putRes.status}`)

    // 3) 通知后端：图片已在 S3，开始以图搜图/识别/打标签等
    // 示例（按你的业务改 endpoint）：
    await fetch(`${import.meta.env.VITE_API_BASE}/image-search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key })
    })

    // 4) 触发刷新（如果以图搜图能返回候选，直接更新 plants）
    // const result = await res.json(); plants.value = result.items

  } catch (e: any) {
    console.error(e)
    alert(e.message || '上传失败')
  } finally {
    // 可选：input.value = '' 以便同一张图可再次选择
  }
}
const clearPreview = () => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
  previewName.value = ''
}

/** ====== 工具：把 'yes'/'no'/'all' 映射成后端布尔/undefined ====== */
function ynToBool(v: string): boolean | undefined {
  if (v === 'yes') return true
  if (v === 'no') return false
  return undefined // 'all' 或 '' 都不传该过滤
}

/** ====== 把页面过滤映射为 /plants 的查询参数 ====== */
function buildApiParams() {
  return {
    search: query.value || undefined,
    // 把你页面的 key → 映射成后端需要的 key
    filters: {
      if_threatened: ynToBool(filters.poisonous), // Threatened（你 UI 上的 label）
      if_edible:     ynToBool(filters.edible),
      if_medicinal:  ynToBool(filters.medicinal),
      if_fruits:     ynToBool(filters.fruits),
      if_indoors:    ynToBool(filters.indoors),
      if_flowers:    ynToBool(filters.flowers),
      // 其余枚举型
      sun_expose: filters.sun ? [filters.sun] : undefined,  // 后端是数组：传单个也包成数组
      watering:   filters.watering || undefined,
      plant_cycle:filters.cycle || undefined,
      growth_rate:filters.growth || undefined
    },
    page: 1,
    page_size: 8   // 你这里弹窗中展示 8 个，如需分页可再加控件
  }
}

onMounted(load)


/** ====== 发起请求并渲染 ====== */
let ctrl: AbortController | null = null
async function load() {
  loading.value = true
  error.value = ''
  ctrl?.abort()
  ctrl = new AbortController()
  try {
    const params = buildApiParams()
    const res = await fetchPlants(params as any) // fetchPlants 已在 src/api/plants.ts 定义
    plants.value = res.items
  } catch (e: any) {
    if (e.name !== 'AbortError') error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}

/** ====== 事件：搜索、应用、重置 ====== */
const onSearch = () => load()

const resetFilters = () => {
  Object.keys(filters).forEach((k) => (filters as any)[k] = '')
}

const applyFilters = () => {
  open.value = false
  load()
}

/** ====== 首次进入先拉一波 ====== */
onMounted(load)

/** 
import { ref, reactive, watch } from 'vue'
import { fetchPlants, type Plant, type PlantFilters } from '@/api/plants'

const items = ref<Plant[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(24)
const search = ref('')

const filters = reactive<PlantFilters>({
  if_threatened: false,
  if_edible: false,
  if_indoors: false,
  if_medicinal: false,
  if_poisonous: false,
  if_fruits: false,
  if_flowers: false,
  sun_expose: []
})
const watering = ref<string>('')     // 单选
const plant_cycle = ref<string>('')  // 单选
const growth_rate = ref<string>('')  // 单选

const sunExposeSet = reactive(new Set<string>())

function toggleSun(v: string) {
  sunExposeSet.has(v) ? sunExposeSet.delete(v) : sunExposeSet.add(v)
  filters.sun_expose = Array.from(sunExposeSet)
  page.value = 1
  load()
}

function renderOther(val: string[] | string) {
  return Array.isArray(val) ? val.join(', ') : val
}

const loading = ref(false)
const error = ref('')
let debounceTimer: number | null = null
let ctrl: AbortController | null = null

function onSearchInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = window.setTimeout(() => {
    page.value = 1
    load()
  }, 350)
}

function thumbStyle(url: string) {
  return { backgroundImage: `url('${url}')`, backgroundSize: 'cover', backgroundPosition: 'center', aspectRatio: '4/3', borderRadius: '8px' } as any
}

async function load() {
  loading.value = true
  error.value = ''
  if (ctrl) ctrl.abort()
  ctrl = new AbortController()
  try {
    const res = await fetchPlants({
      search: search.value,
      page: page.value,
      page_size: pageSize.value,
      filters: {
        ...filters,
        watering: watering.value || undefined,
        plant_cycle: plant_cycle.value || undefined,
        growth_rate: growth_rate.value || undefined
      }
    })
    items.value = res.items
    total.value = res.total
  } catch (e: any) {
    if (e.name !== 'AbortError') error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}

// 分页/每页变化即刻刷新
watch([page, pageSize], load, { immediate: true })
// 单选下拉变化即刻刷新
watch([watering, plant_cycle, growth_rate], () => { page.value = 1; load() })
**/
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

.modal__body {
  flex: 1;                  
  overflow-y: auto;         
  padding: 20px 24px;
}


.modal__body::-webkit-scrollbar {
  width: 8px;
}
.modal__body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}
.modal__body::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.35);
}

.modal__head, .modal__foot {
  padding: 16px 24px; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid var(--c-border);
}
.modal__foot { border-top: 1px solid var(--c-border); border-bottom: none; }
.modal__title { font-size: 18px; font-weight: 600; }
.modal__close { background: none; border: none; color: var(--c-muted); cursor: pointer; }
.modal__body { padding: 20px 24px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 22px 40px; }
.field label { font-weight: 600; display: block; margin-bottom: 6px; }
.radios { display: grid; gap: 6px; color: var(--c-text); }
.select { width: 100%; height: 40px; border: 1px solid var(--c-border); border-radius: 10px; padding: 0 12px; background: #342d2d; }
.link { color: var(--c-muted); background: none; border: none; cursor: pointer; }


.plants-grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}
.plant{background:var(--card);box-shadow:var(--shadow);border-radius:14px;padding:.8rem}
.plant .thumb{aspect-ratio:4/3;border-radius:10px;border:2px dashed color-mix(in oklab, var(--fg) 25%, transparent);margin-bottom:.5rem}
.plant h4{margin:.25rem 0}
.plant .latin{color:var(--muted);font-size:.9rem}


/** 
.container { display: grid; gap: 1rem; padding: 1rem 0; }
.toolbar { display: grid; grid-template-columns: 1fr; gap: .5rem; align-items: center; }
@media (min-width: 860px) {
  .toolbar { grid-template-columns: 1fr auto auto auto auto 1fr; align-items: center; }
}
.input, .select { padding: .5rem .6rem; border: 1px solid #ddd; border-radius: 8px; }
.bools { display: flex; flex-wrap: wrap; gap: .75rem; align-items: center; }
.chipbox { display: flex; gap: .5rem; flex-wrap: wrap; }
.chip { padding: .25rem .5rem; border: 1px solid #ddd; border-radius: 999px; cursor: pointer; user-select: none; }
.chip.on { background: #222; color: #fff; border-color: #222; }

.plants-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.plant { display: grid; gap: .25rem; }
.thumb { width: 100%; background: #eee; }
.title { margin: .25rem 0 0; }
.latin { color: #666; font-style: italic; }
.aka { color: #777; font-size: .9rem; }
.error { color: #c00; }
.pager { display: flex; gap: .75rem; align-items: center; justify-content: center; padding: .75rem 0; }
.skeleton .thumb { background: #f1f1f1; height: 0; padding-bottom: 75%; }
.skeleton h4, .skeleton .latin { height: 12px; background: #f6f6f6; border-radius: 6px; }
**/
</style>