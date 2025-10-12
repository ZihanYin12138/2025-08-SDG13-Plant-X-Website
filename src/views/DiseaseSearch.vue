<!-- src/views/DiseaseSearch.vue -->
<template>
  <!-- ========== Plant Disease ========== -->
  <section id="diseases" class="container">
    <div class="section-box" aria-label="Plant Disease Search & Recognition">
      <h2>Plant Disease search and recognization</h2>
      <p>Click "🎤" to enter the disease name by voice. &nbsp Click "➕" to upload a picture to identify plant disease.
        <br>Please note: If the website encounters an error, please try again !
      </p>

      <!-- Disease search -->
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

      <!-- Quantity information -->
      <div class="list-toolbar" v-if="diseaseItems.length || diseasePage>1">
        <div class="results-meta">
          Showing {{ dStart }}–{{ dEnd }} of {{ dTotalKnown ? dTotal : '…' }} results
        </div>
      </div>

      <!-- No match prompt -->
      <p v-if="dNoImageMatches" class="info" role="status">
        No matching diseases were found for this image. Try another photo (clear, single subject), or search by name/keyword.
      </p>

      <!-- Preview -->
      <div v-if="dPreviewUrl" class="preview">

        <img :src="dPreviewUrl" alt="preview" />

        <div class="preview__right">
          <div class="preview__top">
            <span class="preview__name">{{ dPreviewName }}</span>
            <button class="link" @click="clearDiseasePreview">Remove</button>
          </div>
          </div>

          <!-- Prediction results -->
          <div class="predbox">
            <p class="pred-name">Prediction results</p>
            <p>The following are the three most likely diseases and <br> their corresponding probabilities ("Healthy" is also included)</p>
          <ul v-if="dPreds.length" class="pred-list">
            <li v-for="p in dPreds" :key="p.id" class="pred-item">
              <span class="pred-name">{{ p.name || ('#' + p.id) }}</span>
              <span class="pred-score">{{ formatProb(p.score) }}</span>
            </li>
          </ul>
          </div>

      </div>

      <!-- Disease upload modal -->
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

      <!-- Disease results list -->
      <div class="plants-grid">
        <template v-if="diseaseLoading">
          <PlantCardSkeleton v-for="n in D_PAGE_SIZE" :key="'ds' + n" />
        </template>

        <p v-else-if="diseaseError" class="error">Load Failed: {{ diseaseError }}</p>

        <template v-else>
          <RouterLink
            v-for="d in diseaseItems"
            :key="d.id"
            :to="{ name: 'DiseaseDetail', params: { id: d.id }, state: { preload: d }, query: { from: 'search' } }"
            style="text-decoration: none;"
          >
            <PdiseaseCard :disease="d" />
          </RouterLink>
        </template>
      </div>

      <!-- Disease pagination -->
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

  <!-- Full screen Loading (disease recognition) -->
  <div v-if="dRecognizing" class="page-loading" role="alert" aria-live="polite">
    <div class="spinner" aria-hidden="true"></div>
    <div class="loading-text">Analyzing disease image…</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { searchDiseases, getDiseaseById } from '@/api/pdisease'
import { uploadDiseaseImage, predictDiseaseByS3Key } from '@/api/DiseaseUpload'
import PdiseaseCard from '@/components/PdiseaseCard.vue'
import PlantCardSkeleton from '@/components/CardSkeleton.vue'

const route = useRoute()
const router = useRouter()

/** Constants */
const D_PAGE_SIZE = 8
const diseasePlaceholder = 'Search For A Disease'
const MAX_MB = 3
/** Special ID to name mapping (backend 0 represents healthy) */
const SPECIAL_DISEASE_LABELS: Record<number, string> = { 0: 'Healthy' }

/** Query and list */
const diseaseQ = ref('')
const diseaseLoading = ref(false)
const diseaseError = ref('')
const diseaseItems = ref<any[]>([])
const diseasePage = ref(1)
const diseasePageInput = ref(1)

/** Recognition and "no match" prompt */
const dRecognizing = ref(false)
const dNoImageMatches = ref(false)

/** Prediction sidebar */
const dPreds = ref<Array<{ id: number; name?: string; score: number | null }>>([])
function formatProb(s: number | null) {
  if (s == null || Number.isNaN(s)) return '—'
  const pct = s <= 1 ? s * 100 : s
  return `${pct.toFixed(1)}%`
}

/** Real total (if backend returns), otherwise soft total */
const dTotal = ref<number | null>(null)
const dTotalKnown = computed(() => typeof dTotal.value === 'number' && dTotal.value >= 0)

/** Statistics range */
const dStart = computed(() =>
  diseaseItems.value.length ? (diseasePage.value - 1) * D_PAGE_SIZE + 1 : 0
)
const dEnd = computed(() =>
  diseaseItems.value.length ? (diseasePage.value - 1) * D_PAGE_SIZE + diseaseItems.value.length : 0
)

/** Page count and prev/next page availability */
const dTotalPages = computed(() =>
  dTotalKnown.value ? Math.max(1, Math.ceil((dTotal.value as number) / D_PAGE_SIZE))
                    : Math.max(1, diseasePage.value)
)
const diseaseHasPrev = computed(() => diseasePage.value > 1)
const diseaseHasNext = computed(() =>
  dTotalKnown.value ? diseasePage.value < dTotalPages.value
                    : diseaseItems.value.length === D_PAGE_SIZE
)

/** ---------- URL 同步（仅使用 d_* 键，互不干扰） ---------- */
function writeDiseaseQuery() {
  const next = {
    ...route.query,
    d_q: diseaseQ.value || undefined,
    d_page: diseasePage.value > 1 ? String(diseasePage.value) : undefined,
    tab: 'disease'
  }
  router.replace({ query: next })
}
function readDiseaseQuery() {
  const q = route.query
  diseaseQ.value = String(q.d_q ?? '')
  diseasePage.value = Math.max(1, Number(q.d_page ?? 1))
}

/** Search entry */
async function runDiseaseSearch(page = 1) {
  diseaseLoading.value = true
  diseaseError.value = ''
  dNoImageMatches.value = false
  try {
    const res: any = await searchDiseases(diseaseQ.value, { page, pageSize: D_PAGE_SIZE })
    diseaseItems.value = res.items || []

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
function onDiseaseSearch() { diseasePage.value = 1; writeDiseaseQuery(); runDiseaseSearch(1) }
function dGoTo(p: number) {
  const target = Math.max(1, Number(p) || 1)
  diseasePageInput.value = target
  diseasePage.value = target
  writeDiseaseQuery()
  runDiseaseSearch(target)
}
function dPrev() { if (diseaseHasPrev.value) dGoTo(diseasePage.value - 1) }
function dNext() { if (diseaseHasNext.value) dGoTo(diseasePage.value + 1) }

/** Voice recognition */
const diseaseListening = ref(false)
const speechSupported = typeof window !== 'undefined' && 'webkitSpeechRecognition' in window
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

/** Upload recognition */
const dUploadOpen = ref(false)
const dDragActive = ref(false)
const dUploadError = ref('')
const dFileInput = ref<HTMLInputElement | null>(null)
const dPreviewUrl = ref(''); const dPreviewName = ref('')

function pickDiseaseFile(){ dUploadError.value=''; dFileInput.value?.click() }
function onDiseaseFileInputChange(ev:Event){
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  processDiseaseFile(file)
}
function onDiseaseDrop(e:DragEvent){
  dDragActive.value=false
  dUploadError.value=''
  const files = e.dataTransfer?.files
  if (!files?.length) return
  processDiseaseFile(files[0])
}

async function processDiseaseFile(file:File){
  dUploadError.value = ''
  if (!file.type.startsWith('image/')){ dUploadError.value='Please upload an image file.'; return }
  const max = MAX_MB*1024*1024
  if (file.size>max){ dUploadError.value=`File too large. Max ${MAX_MB}MB.`; return }

  // Preview
  dPreviewName.value=file.name
  if (dPreviewUrl.value) URL.revokeObjectURL(dPreviewUrl.value)
  dPreviewUrl.value=URL.createObjectURL(file)
  dUploadOpen.value=false

  // Clear old predictions
  dPreds.value = []

  // —— Disease recognition
  dRecognizing.value = true
  diseaseLoading.value = true
  diseaseError.value = ''
  dNoImageMatches.value = false
  try{
    const up = await uploadDiseaseImage(file)
    const pred = await predictDiseaseByS3Key(up.key, D_PAGE_SIZE)

    const rawPreds = (pred.results || [])
      .map((r:any) => {
        const id =
          r?.plant_disease_id ??
          r?.disease_id ??
          r?.predicted_id
        const score = (typeof r?.score === 'number') ? r.score : null
        return (typeof id === 'number') ? { id, score } : null
      })
      .filter(Boolean) as Array<{id:number; score:number|null}>

    const ids: number[] = rawPreds.map(p => p.id).filter(id => id !== 0)

    if (!ids.length){
      const nameMap = new Map<number, string>()
      Object.entries(SPECIAL_DISEASE_LABELS).forEach(([k, v]) => nameMap.set(Number(k), v))

      dPreds.value = rawPreds
        .map(p => ({ ...p, name: nameMap.get(p.id) || ('#' + p.id) }))
        .sort((a, b) => {
          const sa = (a.score == null ? -1 : a.score)
          const sb = (b.score == null ? -1 : b.score)
          return sb - sa
        })

      diseaseItems.value = []
      dTotal.value = 0
      diseasePage.value = 1
      diseasePageInput.value = 1
      dNoImageMatches.value = rawPreds.length === 0
      writeDiseaseQuery()
      return
    }

    const details = await Promise.all(
      ids.slice(0, D_PAGE_SIZE).map((id:number)=> getDiseaseById(id).catch(()=>null))
    )
    diseaseItems.value = details.filter(Boolean) as any[]
    diseasePage.value = 1
    diseasePageInput.value = 1
    dTotal.value = diseaseItems.value.length
    writeDiseaseQuery()

    // Align predictions with detail names
    const nameMap = new Map<number, string>()
    Object.entries(SPECIAL_DISEASE_LABELS).forEach(([k, v]) => nameMap.set(Number(k), v))
    for (const d of diseaseItems.value) {
      nameMap.set(Number(d.id), d.name || d.scientific_name || String(d.id))
    }
    dPreds.value = rawPreds
      .map(p => ({ ...p, name: nameMap.get(p.id) || ('#' + p.id) }))
      .sort((a, b) => {
        const sa = (a.score == null ? -1 : a.score)
        const sb = (b.score == null ? -1 : b.score)
        return sb - sa
      })

    const el = document.getElementById('diseases')
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }catch(e:any){
    diseaseError.value = e?.message || String(e)
    dPreds.value = []
  }finally{
    diseaseLoading.value = false
    dRecognizing.value = false
  }
}
function clearDiseasePreview(){
  if (dPreviewUrl.value) URL.revokeObjectURL(dPreviewUrl.value)
  dPreviewUrl.value=''
  dPreviewName.value=''
  dPreds.value = []
}

/** Initial entry: 读取 d_*，然后加载 */
onMounted(() => {
  if (route.query.tab !== 'disease') {
    router.replace({ query: { ...route.query, tab: 'disease' } })
  }
  readDiseaseQuery()
  diseasePageInput.value = diseasePage.value
  runDiseaseSearch(diseasePage.value)
})

/** Clean up local URLs */
onBeforeUnmount(() => {
  if (dPreviewUrl.value) URL.revokeObjectURL(dPreviewUrl.value)
})
</script>

<style scoped>
/* —— Block outline —— */
.section-box{
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  background: transparent;
}

/* ====== Search bar ====== */
.searchbar { position: relative; display: flex; gap: 12px; align-items: center; margin-bottom: 16px; }
.searchbar__box { position: relative; flex: 1; }
.searchbar__input {
  width: 100%; height: 48px; box-sizing: border-box; border-radius: 999px; border: 2px solid var(--border);
  padding: 0 112px 0 44px; outline: none; box-shadow: var(--shadow-sm); background: var(--card); color: var(--fg);
}
.searchbar__input:focus-visible { outline: var(--ring); box-shadow: none; }
.searchbar__icon-left { position: absolute; inset: 0 auto 0 14px; display: grid; place-items: center; color: var(--muted); pointer-events: none; }
.searchbar__icon-rights { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); display: flex; gap: 4px; align-items: center; }

/* ====== Buttons ====== */
.icon-btn { width: 36px; height: 36px; display: grid; place-items: center; border-radius: 50%; border: 1px solid var(--border); background: var(--card); color: var(--fg); cursor: pointer; }
.icon-btn:hover { background: var(--hover); }
.icon-btn--active { box-shadow: 0 0 0 2px color-mix(in oklab, var(--brand) 50%, transparent) inset; }

.btn { height: 48px; padding: 0 18px; border-radius: 10px; border: 1px solid var(--border); background: var(--card); color: var(--fg); cursor: pointer; box-shadow: var(--shadow-sm); }
.btn:disabled { opacity: .6; cursor: not-allowed; }
.btn:hover { background: var(--hover); }

/* ====== Preview ====== */
.preview {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin: 8px 0 16px;
  color: var(--muted);
}
.preview img { width: 100px; height: 100px; object-fit: cover; border-radius: 8px; }
.preview__right { flex: 1; min-width: 0; }
.preview__top { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.preview__name { max-width: 40vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.link { color: var(--muted); background: none; border: none; cursor: pointer; }

.pred-list {
  margin: 0;
  padding: 6px 8px;
  list-style: none;
  border: 1px dashed color-mix(in oklab, var(--fg) 30%, transparent);
  border-radius: 8px;
  background: var(--surface);
  display: flex;
  gap: 8px;
  width: 100%;
}
.pred-item { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; }
.pred-name { color: var(--fg); font-weight: 600; margin-right: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pred-score { color: var(--muted); font-variant-numeric: tabular-nums; }

/* ====== Modal ====== */
.modal-mask { position: fixed; inset: 0; background: var(--backdrop); display: grid; place-items: start center; padding-top: 48px; z-index: 50; }
.modal {
  width: 840px; max-width: 95vw; max-height: 80vh; display: flex; flex-direction: column; background: var(--card);
  border-radius: 16px; border: 1px solid var(--border); box-shadow: var(--shadow-md);
}
.upload-modal .modal__body { padding: 28px; }
.modal__body { flex: 1; overflow-y: auto; padding: 20px 24px; }
.modal__head, .modal__foot { padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
.modal__foot { border-top: 1px solid var(--border); border-bottom: none; }
.modal__title { font-size: 18px; font-weight: 600; }
.modal__close{ width: 32px; height: 32px; border-radius: 50%; border: 1px solid var(--border); background: var(--card); color: var(--fg); cursor: pointer; }

/* ====== Upload area ====== */
.dropzone{
  border: 2px dashed color-mix(in oklab, var(--fg) 30%, transparent);
  border-radius: 14px; background: var(--surface);
  padding: 26px; transition: .15s ease;
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

/* ====== List toolbar / statistics / pagination ====== */
.list-toolbar{ display:flex; align-items:center; justify-content:space-between; gap:.75rem; margin: .5rem 0 1rem; }
.list-toolbar.bottom{ margin-top: 1rem; justify-content: center; }
.results-meta{ color: var(--muted); }
.pager{ display:flex; align-items:center; gap:.5rem; }
.pager .btn-ghost.sm{
  padding: .35rem .6rem; border-radius: 999px; border: 1px solid color-mix(in oklab, var(--fg) 20%, transparent); background: transparent; color: var(--fg);
}
.pager .btn-ghost.sm:disabled{ opacity:.5; cursor:not-allowed; }
.pager-input{ width: 3.5rem; height: 32px; padding: 0 .5rem; border-radius: 8px; border: 1px solid var(--border); background: var(--card); color: var(--fg); }
.pager-num{ color: var(--muted); }

/* ====== Card grid (diseases) ====== */
.plants-grid { display: grid; gap: 1rem; grid-template-columns: repeat(4, 1fr); }
@media (max-width: 768px) { .plants-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .plants-grid { grid-template-columns: 1fr; } }

/* Tips and errors */
.muted{ color: var(--muted); }
.info{
  margin: 6px 0 10px; padding: 8px 12px;
  border: 1px dashed color-mix(in oklab, var(--fg) 30%, transparent);
  border-radius: 10px; color: var(--muted);
}
.error{ color:#c00; margin-top:8px }

/* ====== Full screen Loading (recognizing) ====== */
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
.loading-text{ margin-top: .6rem; color: var(--fg); font-weight: 600; text-align: center; }
@keyframes spin{ to{ transform: rotate(360deg) } }
</style>
