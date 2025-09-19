<!-- src/views/GardenPage.vue -->
<template>
  <!-- 顶部简介 -->
  <section class="container">
    <h2 class="title">Garden</h2>
    <p class="lead">
      Tools and tips for climate-adaptive home gardening — sunlight, soil, watering, composting, and more.
    </p>
  </section>

  <!-- ========== 植物搜索与识别（透明描边框） ========== -->
  <section class="container">
    <div class="section-box" aria-label="Plant Search & Recognition">
      <h2>Plant search and recognization</h2>
      <p>Search for a plants or Upload a image to identify a plant.</p>

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
            <button
              v-if="speechSupported"
              class="icon-btn"
              :class="{ 'icon-btn--active': listening }"
              :title="listening ? 'Listening…' : 'Voice Recognition'"
              @click="startVoice"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Z"/>
                <path d="M19 11a7 7 0 0 1-14 0" fill="none" stroke="currentColor" stroke-width="1.5"/>
                <path d="M12 18v3" fill="none" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </button>

            <button class="icon-btn" title="Upload image" @click="uploadOpen = true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12h14" />
              </svg>
            </button>
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

      <!-- 上传弹窗（点击遮罩关闭 + ESC 关闭） -->
      <div
        v-if="uploadOpen"
        class="modal-mask"
        @keydown.esc="uploadOpen = false"
        @click.self="uploadOpen = false"
      >
        <div class="modal upload-modal" role="dialog" aria-modal="true">
          <div class="modal__head">
            <div class="modal__title">Upload an image</div>
            <button class="modal__close" @click="uploadOpen = false">✕</button>
          </div>

          <div class="modal__body">
            <div class="dropzone" :class="{ 'is-dragover': dragActive }"
              @dragenter.prevent="dragActive = true"
              @dragover.prevent="dragActive = true"
              @dragleave.prevent="dragActive = false"
              @drop.prevent="onDrop">
              <div class="dz-inner">
                <div class="dz-icon" aria-hidden="true">🖼️</div>
                <div class="dz-title">Drag & drop image here</div>
                <div class="dz-sub">or</div>
                <div class="dz-actions">
                  <button class="btn" @click="pickFile">Choose image</button>
                  <input ref="fileInput" type="file" accept="image/*" hidden @change="onFileInputChange" />
                </div>
                <p class="dz-tip">JPEG/PNG · Max 3MB</p>
                <p v-if="uploadError" class="error" role="alert">{{ uploadError }}</p>
              </div>
            </div>
          </div>

          <div class="modal__foot">
            <span class="muted">Your image will be analyzed to suggest matching plants.</span>
            <div>
              <button class="btn" @click="uploadOpen = false">Close</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Filter 弹窗（点击遮罩关闭 + ESC 关闭） -->
      <div
        v-if="open"
        class="modal-mask"
        @keydown.esc="open = false"
        @click.self="open = false"
      >
        <div class="modal" role="dialog" aria-modal="true">
          <div class="modal__head">
            <div class="modal__title">Filter</div>
            <button class="modal__close" @click="open = false">✕</button>
          </div>

          <div class="modal__body">
            <div class="grid-2">
              <div class="field">
                <label>Threatened Plants</label>
                <div class="radios">
                  <label>
                    <input type="radio" value="yes" v-model="filters.threatened" @click="toggleRadio('threatened','yes')">
                    Yes, I want to help with threatened !
                  </label>
                  <label>
                    <input type="radio" value="no" v-model="filters.threatened" @click="toggleRadio('threatened','no')">
                    No, I want to see all general plants !
                  </label>
                </div>
              </div>

              <div class="field" v-if="threatenedOn">
                <label>&nbsp;</label>
                <p class="muted">Showing threatened plants only</p>
              </div>
              <div class="field" v-else></div>

              <template v-if="!threatenedOn">
                <div class="field">
                  <label>Edible</label>
                  <div class="radios">
                    <label><input type="radio" value="yes" v-model="filters.edible" @click="toggleRadio('edible','yes')"> Yes</label>
                    <label><input type="radio" value="no" v-model="filters.edible" @click="toggleRadio('edible','no')"> No</label>
                  </div>
                </div>

                <div class="field">
                  <label>Medicinal</label>
                  <div class="radios">
                    <label><input type="radio" value="yes" v-model="filters.medicinal" @click="toggleRadio('medicinal','yes')"> Yes</label>
                    <label><input type="radio" value="no" v-model="filters.medicinal" @click="toggleRadio('medicinal','no')"> No</label>
                  </div>
                </div>

                <div class="field">
                  <label>Fruits</label>
                  <div class="radios">
                    <label><input type="radio" value="yes" v-model="filters.fruits" @click="toggleRadio('fruits','yes')"> Yes</label>
                    <label><input type="radio" value="no" v-model="filters.fruits" @click="toggleRadio('fruits','no')"> No</label>
                  </div>
                </div>

                <div class="field">
                  <label>Indoors</label>
                  <div class="radios">
                    <label><input type="radio" value="yes" v-model="filters.indoors" @click="toggleRadio('indoors','yes')"> Yes</label>
                    <label><input type="radio" value="no" v-model="filters.indoors" @click="toggleRadio('indoors','no')"> No</label>
                  </div>
                </div>

                <div class="field">
                  <label>Flowers</label>
                  <div class="radios">
                    <label><input type="radio" value="yes" v-model="filters.flowers" @click="toggleRadio('flowers','yes')"> Yes</label>
                    <label><input type="radio" value="no" v-model="filters.flowers" @click="toggleRadio('flowers','no')"> No</label>
                  </div>
                </div>

                <div class="field">
                  <label>Poisonous</label>
                  <div class="radios">
                    <label><input type="radio" value="yes" v-model="filters.poisonous" @click="toggleRadio('poisonous','yes')"> Yes</label>
                    <label><input type="radio" value="no" v-model="filters.poisonous" @click="toggleRadio('poisonous','no')"> No</label>
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
              </template>
            </div>
          </div>

          <div class="modal__foot">
            <button class="link" @click="resetAndReload">Reset</button>
            <div>
              <button class="btn" @click="applyFilters">Apply Filter</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 列表 + 统计 + 分页（植物） -->
      <section>
        <div class="list-toolbar" v-if="totalKnown">
          <div class="results-meta">
            Showing {{ startIndex }}–{{ endIndex }} of {{ total }} results
          </div>
        </div>

        <div class="plants-grid">
          <template v-if="loading">
            <PlantCardSkeleton v-for="n in PAGE_SIZE" :key="'s' + n" />
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

        <div class="list-toolbar bottom" v-if="totalKnown && totalPages>1">
          <div class="pager">
            <button class="btn-ghost sm" :disabled="page<=1" @click="prevPage">‹ Prev</button>
            <span class="pager-num">Page</span>
            <input class="pager-input" type="number" :min="1" :max="totalPages" v-model.number="pageInput" @keyup.enter="goToPage(pageInput)" />
            <span>/ {{ totalPages }}</span>
            <button class="btn-ghost sm" :disabled="page>=totalPages" @click="nextPage">Next ›</button>
          </div>
        </div>
      </section>
    </div>
  </section>

  <!-- 分隔线（上下留少量空隙） -->
  <hr class="divider-red" aria-hidden="true" />

  <!-- ========== 植物疾病（透明描边框） ========== -->
  <section id="diseases" class="container">
    <div class="section-box" aria-label="Plant Disease Search & Recognition">
      <h2>Plant Disease search and recognization</h2>
      <p>Search for a plant disease or Upload a image to identify a disease.</p>

      <!-- 疾病搜索 -->
      <div class="searchbar">
        <div class="searchbar__box">
          <input
            class="searchbar__input"
            :placeholder="diseasePlaceholder"
            v-model="diseaseQ"
            @keyup.enter="onDiseaseSearch"
          />
          <span class="searchbar__icon-left">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="7" />
              <path d="M20 20l-3.5-3.5" />
            </svg>
          </span>
          <div class="searchbar__icon-rights">
            <button
              v-if="speechSupported"
              class="icon-btn"
              :class="{ 'icon-btn--active': diseaseListening }"
              :title="diseaseListening ? 'Listening…' : 'Voice Recognition'"
              @click="startDiseaseVoice"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Z"/>
                <path d="M19 11a7 7 0 0 1-14 0" fill="none" stroke="currentColor" stroke-width="1.5"/>
                <path d="M12 18v3" fill="none" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </button>

            <button class="icon-btn" title="Upload image" @click="dUploadOpen = true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12h14" />
              </svg>
            </button>
          </div>
        </div>

        <button class="btn" @click="onDiseaseSearch">Search</button>
      </div>

      <!-- 疾病上传弹窗（点击遮罩关闭 + ESC 关闭） -->
      <div
        v-if="dUploadOpen"
        class="modal-mask"
        @keydown.esc="dUploadOpen = false"
        @click.self="dUploadOpen = false"
      >
        <div class="modal upload-modal" role="dialog" aria-modal="true">
          <div class="modal__head">
            <div class="modal__title">Upload an image</div>
            <button class="modal__close" @click="dUploadOpen = false">✕</button>
          </div>

          <div class="modal__body">
            <div class="dropzone" :class="{ 'is-dragover': dDragActive }"
              @dragenter.prevent="dDragActive = true"
              @dragover.prevent="dDragActive = true"
              @dragleave.prevent="dDragActive = false"
              @drop.prevent="onDiseaseDrop">
              <div class="dz-inner">
                <div class="dz-icon" aria-hidden="true">🖼️</div>
                <div class="dz-title">Drag & drop image here</div>
                <div class="dz-sub">or</div>
                <div class="dz-actions">
                  <button class="btn" @click="pickDiseaseFile">Choose image</button>
                  <input ref="dFileInput" type="file" accept="image/*" hidden @change="onDiseaseFileInputChange" />
                </div>
                <p class="dz-tip">JPEG/PNG · Max 3MB</p>
                <p v-if="dUploadError" class="error" role="alert">{{ dUploadError }}</p>
              </div>
            </div>
          </div>

          <div class="modal__foot">
            <span class="muted">Your image will be analyzed to suggest matching diseases.</span>
            <div>
              <button class="btn" @click="dUploadOpen = false">Close</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 数量信息（支持总数已知/未知） -->
      <div class="list-toolbar" v-if="diseaseItems.length || diseasePage>1">
        <div class="results-meta">
          Showing {{ dStart }}–{{ dEnd }} of {{ dTotalKnown ? dTotal : '…' }} results
        </div>
      </div>

      <!-- 无匹配提示（图片识别返回空时） -->
      <p v-if="dNoImageMatches" class="info" role="status">
        No matching diseases were found for this image. Try another photo (clear, single subject), or search by name/keyword.
      </p>

      <!-- 预览 -->
      <div v-if="dPreviewUrl" class="preview">
        <img :src="dPreviewUrl" alt="preview" />
        <span class="preview__name">{{ dPreviewName }}</span>
        <button class="link" @click="clearDiseasePreview">Remove</button>
      </div>

      <!-- 疾病结果列表 -->
      <div class="plants-grid">
        <template v-if="diseaseLoading">
          <PlantCardSkeleton v-for="n in D_PAGE_SIZE" :key="'ds' + n" />
        </template>

        <p v-else-if="diseaseError" class="error">Load Failed: {{ diseaseError }}</p>

        <template v-else>
          <RouterLink
            v-for="d in diseaseItems"
            :key="d.id"
            :to="{ name: 'DiseaseDetail', params: { id: d.id }, state: { preload: d } }"
            style="text-decoration: none;"
          >
            <PdiseaseCard :disease="d" />
          </RouterLink>
        </template>
      </div>

      <!-- 疾病分页（unknown total 时也显示，按钮按 hasPrev/hasNext 控制） -->
      <div
        class="list-toolbar bottom"
        v-if="!diseaseLoading && (diseaseHasPrev || diseaseHasNext || dTotalPages>1)"
      >
        <div class="pager">
          <button class="btn-ghost sm" :disabled="!diseaseHasPrev" @click="dPrev">‹ Prev</button>
          <span class="pager-num">Page</span>
          <input
            class="pager-input"
            type="number"
            :min="1"
            :max="dTotalKnown ? dTotalPages : 9999"
            v-model.number="diseasePageInput"
            @keyup.enter="dGoTo(diseasePageInput)"
          />
          <span v-if="dTotalKnown">/ {{ dTotalPages }}</span>
          <button class="btn-ghost sm" :disabled="!diseaseHasNext" @click="dNext">Next ›</button>
        </div>
      </div>

      <div v-if="!diseaseLoading && !diseaseError && diseaseItems.length === 0" class="muted" style="margin-top:.5rem;">
        Try keywords like <em>rust, blight, canker</em>…
      </div>
    </div>
  </section>

  <!-- 全屏 Loading（分别用于植物识别和疾病识别） -->
  <div v-if="recognizing || dRecognizing" class="page-loading" role="alert" aria-live="polite">
    <div class="spinner" aria-hidden="true"></div>
    <div class="loading-text">{{ recognizing ? 'Analyzing plant image…' : 'Analyzing disease image…' }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import {
  searchPlants,
  getPlantById,
  type PlantDetail,
  type PlantCardItem
} from '@/api/plants'
import PlantCard from '@/components/PlantCard.vue'
import PlantCardSkeleton from '@/components/CardSkeleton.vue'
import { uploadImage, predictByS3Key } from '@/api/uploads'

/** 疾病 API（搜索/详情） & 卡片；疾病上传识别 API */
import { searchDiseases, getDiseaseById } from '@/api/pdisease'
import { uploadDiseaseImage, predictDiseaseByS3Key } from '@/api/DiseaseUpload'
import PdiseaseCard from '@/components/PdiseaseCard.vue'

/** ================= 植物区 ================= */
const PAGE_SIZE = 8
const MAX_MB = 3
const placeholder = 'Search For A Plant'
const query = ref('')
const open = ref(false)

const uploadOpen = ref(false)
const dragActive = ref(false)
const uploadError = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

/** 植物识别 Loading（覆盖全屏） */
const recognizing = ref(false)

const loading = ref(false)
const error = ref('')

const page = ref(1)
const total = ref(0)
const pageInput = ref(1)

const plants = ref<PlantCardItem[]>([])

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

const threatenedOn = computed(() => filters.threatened === 'yes')
function toggleRadio<K extends keyof typeof filters>(field: K, val: string) {
  if ((filters as any)[field] === val) (filters as any)[field] = ''
  else (filters as any)[field] = val
}
function clearNonThreatenedFilters() {
  filters.edible = ''
  filters.medicinal = ''
  filters.fruits = ''
  filters.indoors = ''
  filters.poisonous = ''
  filters.flowers = ''
  filters.sun = ''
  filters.watering = ''
  filters.cycle = ''
  filters.growth = ''
}
watch(threatenedOn, (on) => { if (on) { clearNonThreatenedFilters(); goToPage(1) } })

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))
const totalKnown = computed(() => total.value > 0)
const startIndex = computed(() => total.value ? (page.value - 1) * PAGE_SIZE + 1 : 0)
const endIndex = computed(() => total.value ? Math.min(total.value, page.value * PAGE_SIZE) : plants.value.length)

const safePlants = computed(() =>
  (plants.value || []).filter(p =>
    p && (
      (p.id_type === 'general' && Number.isFinite((p as any).general_plant_id)) ||
      (p.id_type === 'threatened' && Number.isFinite((p as any).threatened_plant_id))
    )
  )
)

function normalizePreload(p: any) {
  return {
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
      query: { type: 'threatened' },
      state: { preload: normalizePreload(p) }
    }
  }
  if (p?.id_type === 'general' && Number.isFinite(p.general_plant_id)) {
    return {
      name: 'PlantDetail',
      params: { id: p.general_plant_id },
      query: { type: 'general' },
      state: { preload: normalizePreload(p) }
    }
  }
  return { path: '/' }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await searchPlants({
      search: query.value,
      page: page.value,
      page_size: PAGE_SIZE,
      filters: { ...filters }
    })
    total.value = Number(res.total ?? 0)
    plants.value = res.items || []
    pageInput.value = page.value
  } catch (e: any) {
    error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}
function goToPage(p: number) {
  const tp = totalPages.value
  const target = Math.min(Math.max(1, Number(p) || 1), tp)
  if (target !== page.value) { page.value = target; load() }
  else { pageInput.value = page.value }
}
function nextPage() { goToPage(page.value + 1) }
function prevPage() { goToPage(page.value - 1) }

const onSearch = () => { goToPage(1); load() }
const applyFilters = () => { open.value = false; goToPage(1); load() }
const resetFilters = () => { Object.keys(filters).forEach(k => (filters as any)[k] = '') }
const resetAndReload = () => { resetFilters(); goToPage(1); load() }

/** 植物图片上传识别 */
const previewUrl = ref(''); const previewName = ref('')
function pickFile() { uploadError.value = ''; fileInput.value?.click() }
function onFileInputChange(ev: Event) {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  processFile(file)
}
function onDrop(e: DragEvent) {
  dragActive.value = false
  uploadError.value = ''
  const files = e.dataTransfer?.files
  if (!files || !files.length) return
  processFile(files[0])
}
async function processFile(file: File) {
  uploadError.value = ''
  if (!file.type.startsWith('image/')) {
    uploadError.value = 'Please upload an image file.'
    return
  }
  const max = MAX_MB * 1024 * 1024
  if (file.size > max) {
    uploadError.value = `File too large. Max ${MAX_MB}MB.`
    return
  }

  // 预览
  previewName.value = file.name
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = URL.createObjectURL(file)
  uploadOpen.value = false

  // —— 开始识别：显示全屏 Loading
  recognizing.value = true
  loading.value = true
  error.value = ''
  try {
    const up = await uploadImage(file)
    const pred = await predictByS3Key(up.key, PAGE_SIZE)
    const ids = (pred.results || [])
      .filter((r: any) => r && typeof r.plant_id === 'number')
      .map((r: any) => r.plant_id)

    if (!ids.length) {
      plants.value = []
      total.value = 0
      error.value = '未识别到可用候选'
      return
    }

    const details = await Promise.all(
      ids.slice(0, PAGE_SIZE).map((id: number) => getPlantById(id).catch(() => null))
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

    total.value = plants.value.length
    page.value = 1
    pageInput.value = 1
    query.value = `#${ids.join(',')}`
  } catch (e: any) {
    error.value = e.message || String(e)
  } finally {
    loading.value = false
    recognizing.value = false
  }
}
function clearPreview() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
  previewName.value = ''
}

/** 植物语音 */
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

/** 初次进入：第 1 页 */
onMounted(() => { goToPage(1); load() })

/** ================= 疾病区 ================= */
const D_PAGE_SIZE = 8
const diseasePlaceholder = 'Search For A Disease'
const diseaseQ = ref('')

const diseaseLoading = ref(false)
const diseaseError = ref('')
const diseaseItems = ref<any[]>([])

const diseasePage = ref(1)
const diseasePageInput = ref(1)

/** 疾病识别 Loading（覆盖全屏） */
const dRecognizing = ref(false)

/** “无匹配”温和提示（仅图片识别空结果时显示） */
const dNoImageMatches = ref(false)

/** 真实总数（若后端返回），否则使用软总数兜底以便 UI 可用 */
const dTotal = ref<number | null>(null)
const dTotalKnown = computed(() => typeof dTotal.value === 'number' && dTotal.value >= 0)

/** 统计条起止值：仅根据当前页条数推导 */
const dStart = computed(() =>
  diseaseItems.value.length ? (diseasePage.value - 1) * D_PAGE_SIZE + 1 : 0
)
const dEnd = computed(() =>
  diseaseItems.value.length ? (diseasePage.value - 1) * D_PAGE_SIZE + diseaseItems.value.length : 0
)

/** 页数与上下页的可用性 */
const dTotalPages = computed(() =>
  dTotalKnown.value ? Math.max(1, Math.ceil((dTotal.value as number) / D_PAGE_SIZE))
                    : Math.max(1, diseasePage.value)
)
const diseaseHasPrev = computed(() => diseasePage.value > 1)
const diseaseHasNext = computed(() =>
  dTotalKnown.value ? diseasePage.value < dTotalPages.value
                    : diseaseItems.value.length === D_PAGE_SIZE
)

/** 疾病搜索（保持你之前逻辑不变：支持后端 total；无 total 时也兜底） */
async function runDiseaseSearch(page = 1) {
  diseaseLoading.value = true
  diseaseError.value = ''
  dNoImageMatches.value = false
  try {
    const res: any = await searchDiseases(diseaseQ.value, { page, pageSize: D_PAGE_SIZE })
    diseaseItems.value = res.items || []

    // 真实 total（尽量读取多种字段），否则用软总数兜底
    const t = Number(res?.total ?? res?.count ?? res?.total_count)
    if (Number.isFinite(t) && t >= 0) {
      dTotal.value = t
    } else {
      dTotal.value = (page - 1) * D_PAGE_SIZE + diseaseItems.value.length
    }

    diseasePage.value = page
    diseasePageInput.value = page
  } catch (e: any) {
    diseaseError.value = e?.message || String(e)
  } finally {
    diseaseLoading.value = false
  }
}

/** 点击“Search/回车”从第1页查 */
function onDiseaseSearch() {
  diseasePage.value = 1
  runDiseaseSearch(1)
}

/** 分页跳转：总是触发查询；未知 total 时放宽上界 */
function dGoTo(p: number) {
  const target = Math.max(1, Number(p) || 1)
  diseasePageInput.value = target
  runDiseaseSearch(target)
}
function dPrev() { if (diseaseHasPrev.value) dGoTo(diseasePage.value - 1) }
function dNext() { if (diseaseHasNext.value) dGoTo(diseasePage.value + 1) }

/** 疾病语音（英文更利于识别常见病名） */
const diseaseListening = ref(false)
let dRecognizer: any = null
onMounted(() => {
  if (!speechSupported) return
  const SR = (window as any).webkitSpeechRecognition
  const rec = new SR()
  rec.continuous = false
  rec.interimResults = false
  rec.lang = 'en-US'
  rec.onresult = (e: any) => {
    const t = Array.from(e.results).map((r: any) => r[0].transcript).join(' ')
    diseaseQ.value = (diseaseQ.value ? diseaseQ.value + ' ' : '') + t
  }
  rec.onstart = () => (diseaseListening.value = true)
  rec.onend = () => (diseaseListening.value = false)
  dRecognizer = rec
})
const startDiseaseVoice = () => dRecognizer && dRecognizer.start()

/** 疾病图片上传识别（只改上传流程；搜索 & 预加载保持不变） */
const dUploadOpen = ref(false)
const dDragActive = ref(false)
const dUploadError = ref('')
const dFileInput = ref<HTMLInputElement | null>(null)
const dPreviewUrl = ref(''); const dPreviewName = ref('')
function pickDiseaseFile(){ dUploadError.value=''; dFileInput.value?.click() }
function onDiseaseFileInputChange(ev:Event){ const input = ev.target as HTMLInputElement; const file = input.files?.[0]; if (!file) return; processDiseaseFile(file) }
function onDiseaseDrop(e:DragEvent){ dDragActive.value=false; dUploadError.value=''; const files=e.dataTransfer?.files; if (!files?.length) return; processDiseaseFile(files[0]) }

async function processDiseaseFile(file:File){
  dUploadError.value = ''
  if (!file.type.startsWith('image/')){ dUploadError.value='Please upload an image file.'; return }
  const max = MAX_MB*1024*1024
  if (file.size>max){ dUploadError.value=`File too large. Max ${MAX_MB}MB.`; return }

  // 预览
  dPreviewName.value=file.name
  if (dPreviewUrl.value) URL.revokeObjectURL(dPreviewUrl.value)
  dPreviewUrl.value=URL.createObjectURL(file)
  dUploadOpen.value=false

  // —— 疾病识别：显示全屏 Loading
  dRecognizing.value = true
  diseaseLoading.value = true
  diseaseError.value = ''
  dNoImageMatches.value = false
  try{
    // 1) 上传图片（后端：/plantx/upload-D）
    const up = await uploadDiseaseImage(file)

    // 2) 识别并返回 disease_id 列表（后端：/plantx/disease-query）
    const pred = await predictDiseaseByS3Key(up.key, D_PAGE_SIZE)
    const ids: number[] = (pred.results || [])
      .map((r:any)=> r?.plant_disease_id ?? r?.disease_id?? r?.predicted_id)
      .filter((id:any)=> typeof id === 'number')

    if (!ids.length){
      // 无匹配：不当成错误，给友好提示 & 清空结果
      diseaseItems.value = []
      dTotal.value = 0
      diseasePage.value = 1
      diseasePageInput.value = 1
      dNoImageMatches.value = true
      return
    }

    // 3) 用 id 拉取详情（沿用你现有 pdisease 的 getDiseaseById 方案）
    const details = await Promise.all(
      ids.slice(0, D_PAGE_SIZE).map((id:number)=> getDiseaseById(id).catch(()=>null))
    )

    diseaseItems.value = details.filter(Boolean) as any[]
    diseasePage.value = 1
    diseasePageInput.value = 1
    // 识别列表的总数 = 当前得到的匹配数（用于统计/分页）
    dTotal.value = diseaseItems.value.length

    // 滚动到疾病区
    const el = document.getElementById('diseases')
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }catch(e:any){
    diseaseError.value = e?.message || String(e)
  }finally{
    diseaseLoading.value = false
    dRecognizing.value = false
  }
}
function clearDiseasePreview(){ if (dPreviewUrl.value) URL.revokeObjectURL(dPreviewUrl.value); dPreviewUrl.value=''; dPreviewName.value='' }

/** 初次进入：展示第一页（pdisease 内部会处理空查询） */
onMounted(() => { runDiseaseSearch(1) })
</script>

<style scoped>
/* —— 区块外框（透明背景，仅描边） —— */
.section-box{
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  background: transparent; /* 透明，不着色 */
}

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
.searchbar__input:focus-visible { outline: var(--ring); box-shadow: none; }
.searchbar__icon-left {
  position: absolute; inset: 0 auto 0 14px;
  display: grid; place-items: center;
  color: var(--muted); pointer-events: none;
}
.searchbar__icon-rights {
  position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
  display: flex; gap: 4px; align-items: center;
}

/* ====== 按钮 ====== */
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

/* ====== 弹窗（与你原风格一致） ====== */
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
.upload-modal .modal__body { padding: 28px; }
.modal__body { flex: 1; overflow-y: auto; padding: 20px 24px; }
.modal__head, .modal__foot {
  padding: 16px 24px; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid var(--border);
}
.modal__foot { border-top: 1px solid var(--border); border-bottom: none; }
.modal__title { font-size: 18px; font-weight: 600; }
.modal__close{
  width: 32px; height: 32px; border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--card); color: var(--fg); cursor: pointer;
}

/* ====== 上传区域 ====== */
.dropzone{
  border: 2px dashed color-mix(in oklab, var(--fg) 30%, transparent);
  border-radius: 14px;
  background: var(--surface);
  padding: 26px;
  transition: .15s ease;
}
.dropzone.is-dragover{
  background: color-mix(in oklab, var(--brand) 10%, var(--surface));
  border-color: var(--brand);
  box-shadow: 0 0 0 4px color-mix(in oklab, var(--brand) 15%, transparent) inset;
}
.dz-inner{ text-align: center; }
.dz-icon{ font-size: 34px; margin-bottom: .25rem; }
.dz-title{ font-weight: 700; margin-bottom: .25rem; }
.dz-sub{ color: var(--muted); margin-bottom: .5rem; }
.dz-actions{ display:flex; justify-content:center; gap:.5rem; margin-bottom:.25rem; }
.dz-tip{ color: var(--muted); font-size: .9rem; margin: 0; }

/* ====== 表单 ====== */
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

/* ====== 列表工具栏 / 统计 / 分页 ====== */
.list-toolbar{
  display:flex; align-items:center; justify-content:space-between;
  gap:.75rem; margin: .5rem 0 1rem;
}
.list-toolbar.bottom{
  margin-top: 1rem;
  justify-content: center; /* 底部分页居中 */
}
.results-meta{ color: var(--muted); }
.pager{ display:flex; align-items:center; gap:.5rem; }
.pager .btn-ghost.sm{
  padding: .35rem .6rem;
  border-radius: 999px;
  border: 1px solid color-mix(in oklab, var(--fg) 20%, transparent);
  background: transparent;
  color: var(--fg);
}
.pager .btn-ghost.sm:disabled{ opacity:.5; cursor:not-allowed; }
.pager-input{
  width: 3.5rem;
  height: 32px;
  padding: 0 .5rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--fg);
}
.pager-num{ color: var(--muted); }

/* ====== 卡片网格（植物 & 疾病复用） ====== */
.plants-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(4, 1fr);
}
@media (max-width: 768px) { .plants-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .plants-grid { grid-template-columns: 1fr; } }

/* 错误信息 & 分隔线 */
.error{ color:#c00; margin-top:8px }
.divider-red {
  border: 0;
  height: 3px;
  background: linear-gradient(90deg, #ff3b3b, #ff9a3b);
  margin: 8px 0; /* 上下各留一点点间隔 */
}

/* 识别无匹配提示 */
.info{
  margin: 6px 0 10px;
  padding: 8px 12px;
  border: 1px dashed color-mix(in oklab, var(--fg) 30%, transparent);
  border-radius: 10px;
  color: var(--muted);
}

/* 亮色主题下 radio 的样式保持一致 */
:root[data-theme="light"] .radios input[type="radio"],
:root:not([data-theme="dark"]) .radios input[type="radio"]{
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  margin-right: .5rem;
  cursor: pointer;
  background: #e9e9e9;
  border: 2px solid color-mix(in oklab, var(--fg) 35%, var(--bg) 65%);
  transition: background-color .15s ease, border-color .15s ease, box-shadow .15s ease;
}
:root[data-theme="light"] .radios input[type="radio"]:checked,
:root:not([data-theme="dark"]) .radios input[type="radio"]:checked{
  background: rgb(144, 190, 247);
  border-color: var(--fg);
}

/* ====== 全屏 Loading（识别中） ====== */
.page-loading{
  position: fixed; inset: 0;
  background: color-mix(in oklab, var(--bg) 70%, transparent);
  backdrop-filter: blur(1.5px);
  display: grid; place-items: center; z-index: 80;
}
.spinner{
  width: 44px; height: 44px; border-radius: 50%;
  border: 4px solid color-mix(in oklab, var(--fg) 15%, transparent);
  border-top-color: var(--fg);
  animation: spin 1s linear infinite;
}
.loading-text{
  margin-top: .6rem; color: var(--fg); font-weight: 600; text-align: center;
}
@keyframes spin{ to{ transform: rotate(360deg) } }
</style>
