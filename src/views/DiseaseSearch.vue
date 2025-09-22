<!-- src/views/DiseaseSearch.vue -->
<template>
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

  <!-- 全屏 Loading（疾病识别） -->
  <div v-if="dRecognizing" class="page-loading" role="alert" aria-live="polite">
    <div class="spinner" aria-hidden="true"></div>
    <div class="loading-text">Analyzing disease image…</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { searchDiseases, getDiseaseById } from '@/api/pdisease'
import { uploadDiseaseImage, predictDiseaseByS3Key } from '@/api/DiseaseUpload'
import PdiseaseCard from '@/components/PdiseaseCard.vue'
import PlantCardSkeleton from '@/components/CardSkeleton.vue'

/** 常量 */
const D_PAGE_SIZE = 8
const diseasePlaceholder = 'Search For A Disease'
const MAX_MB = 3

/** 查询与列表 */
const diseaseQ = ref('')
const diseaseLoading = ref(false)
const diseaseError = ref('')
const diseaseItems = ref<any[]>([])
const diseasePage = ref(1)
const diseasePageInput = ref(1)

/** 识别与“无匹配”提示 */
const dRecognizing = ref(false)
const dNoImageMatches = ref(false)

/** 真实总数（若后端返回），否则用软总数兜底 */
const dTotal = ref<number | null>(null)
const dTotalKnown = computed(() => typeof dTotal.value === 'number' && dTotal.value >= 0)

/** 统计区间（仅根据当前页条数推导） */
const dStart = computed(() =>
  diseaseItems.value.length ? (diseasePage.value - 1) * D_PAGE_SIZE + 1 : 0
)
const dEnd = computed(() =>
  diseaseItems.value.length ? (diseasePage.value - 1) * D_PAGE_SIZE + diseaseItems.value.length : 0
)

/** 页数与上下页可用性 */
const dTotalPages = computed(() =>
  dTotalKnown.value ? Math.max(1, Math.ceil((dTotal.value as number) / D_PAGE_SIZE))
                    : Math.max(1, diseasePage.value)
)
const diseaseHasPrev = computed(() => diseasePage.value > 1)
const diseaseHasNext = computed(() =>
  dTotalKnown.value ? diseasePage.value < dTotalPages.value
                    : diseaseItems.value.length === D_PAGE_SIZE
)

/** 搜索入口 */
async function runDiseaseSearch(page = 1) {
  diseaseLoading.value = true
  diseaseError.value = ''
  dNoImageMatches.value = false
  try {
    const res: any = await searchDiseases(diseaseQ.value, { page, pageSize: D_PAGE_SIZE })
    diseaseItems.value = res.items || []

    // total: 兼容多字段；否则用软总数兜底
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
function onDiseaseSearch() { diseasePage.value = 1; runDiseaseSearch(1) }
function dGoTo(p: number) { const target = Math.max(1, Number(p) || 1); diseasePageInput.value = target; runDiseaseSearch(target) }
function dPrev() { if (diseaseHasPrev.value) dGoTo(diseasePage.value - 1) }
function dNext() { if (diseaseHasNext.value) dGoTo(diseasePage.value + 1) }

/** 语音（英文更利于识别常见病名） */
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

/** 上传识别 */
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
    // 1) 上传
    const up = await uploadDiseaseImage(file)
    // 2) 识别得到 id 列表
    const pred = await predictDiseaseByS3Key(up.key, D_PAGE_SIZE)
    const ids: number[] = (pred.results || [])
      .map((r:any)=> r?.plant_disease_id ?? r?.disease_id ?? r?.predicted_id)
      .filter((id:any)=> typeof id === 'number')

    if (!ids.length){
      diseaseItems.value = []
      dTotal.value = 0
      diseasePage.value = 1
      diseasePageInput.value = 1
      dNoImageMatches.value = true
      return
    }

    // 3) 拉取详情
    const details = await Promise.all(
      ids.slice(0, D_PAGE_SIZE).map((id:number)=> getDiseaseById(id).catch(()=>null))
    )
    diseaseItems.value = details.filter(Boolean) as any[]
    diseasePage.value = 1
    diseasePageInput.value = 1
    dTotal.value = diseaseItems.value.length

    // 回到疾病块顶部
    const el = document.getElementById('diseases')
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }catch(e:any){
    diseaseError.value = e?.message || String(e)
  }finally{
    diseaseLoading.value = false
    dRecognizing.value = false
  }
}
function clearDiseasePreview(){
  if (dPreviewUrl.value) URL.revokeObjectURL(dPreviewUrl.value)
  dPreviewUrl.value=''
  dPreviewName.value=''
}

/** 初次进入：展示第一页（pdisease 内部会处理空查询） */
onMounted(() => { runDiseaseSearch(1) })

/** 清理本地 URL 以防内存泄漏 */
onBeforeUnmount(() => {
  if (dPreviewUrl.value) URL.revokeObjectURL(dPreviewUrl.value)
})
</script>

<style scoped>
/* —— 区块外框（透明背景，仅描边） —— */
.section-box{
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  background: transparent;
}

/* ====== 搜索条 ====== */
.searchbar { position: relative; display: flex; gap: 12px; align-items: center; margin-bottom: 16px; }
.searchbar__box { position: relative; flex: 1; }
.searchbar__input {
  width: 100%; height: 48px; box-sizing: border-box; border-radius: 999px; border: 2px solid var(--border);
  padding: 0 112px 0 44px; outline: none; box-shadow: var(--shadow-sm); background: var(--card); color: var(--fg);
}
.searchbar__input:focus-visible { outline: var(--ring); box-shadow: none; }
.searchbar__icon-left { position: absolute; inset: 0 auto 0 14px; display: grid; place-items: center; color: var(--muted); pointer-events: none; }
.searchbar__icon-rights { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); display: flex; gap: 4px; align-items: center; }

/* ====== 按钮 ====== */
.icon-btn { width: 36px; height: 36px; display: grid; place-items: center; border-radius: 50%; border: 1px solid var(--border); background: var(--card); color: var(--fg); cursor: pointer; }
.icon-btn:hover { background: var(--hover); }
.icon-btn--active { box-shadow: 0 0 0 2px color-mix(in oklab, var(--brand) 50%, transparent) inset; }

.btn { height: 48px; padding: 0 18px; border-radius: 10px; border: 1px solid var(--border); background: var(--card); color: var(--fg); cursor: pointer; box-shadow: var(--shadow-sm); }
.btn:disabled { opacity: .6; cursor: not-allowed; }
.btn:hover { background: var(--hover); }

/* ====== 预览 ====== */
.preview { display: flex; align-items: center; gap: 10px; margin: 8px 0 16px; color: var(--muted); }
.preview img { width: 44px; height: 44px; object-fit: cover; border-radius: 8px; }
.preview__name { max-width: 40vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.link { color: var(--muted); background: none; border: none; cursor: pointer; }

/* ====== 弹窗 ====== */
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

/* ====== 上传区域 ====== */
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

/* ====== 列表工具栏 / 统计 / 分页 ====== */
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

/* ====== 卡片网格（疾病） ====== */
.plants-grid { display: grid; gap: 1rem; grid-template-columns: repeat(4, 1fr); }
@media (max-width: 768px) { .plants-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .plants-grid { grid-template-columns: 1fr; } }

/* 提示与错误 */
.muted{ color: var(--muted); }
.info{
  margin: 6px 0 10px; padding: 8px 12px;
  border: 1px dashed color-mix(in oklab, var(--fg) 30%, transparent);
  border-radius: 10px; color: var(--muted);
}
.error{ color:#c00; margin-top:8px }

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
.loading-text{ margin-top: .6rem; color: var(--fg); font-weight: 600; text-align: center; }
@keyframes spin{ to{ transform: rotate(360deg) } }
</style>
