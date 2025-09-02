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
          @keyup.enter="onSearch"/>
        
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
      </div>

      <button class="btn" @click="open = true">Filter</button>
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

    
  </div>

</div>

</section>

<section id="plants" class="section container">
    <div class="result">
        <div class="pcard">
            <div class="pimg">

            </div>
            <h1>

            </h1>
            <p>

            </p>
            <div class="picon">

            </div>
        </div>
    </div>
</section>

</template>



<script setup>
import { ref, reactive, onMounted } from 'vue'

/** ====== 可配常量（你也可以抽到 /src/constants/ 下） ====== */
const placeholder = 'Search For A Plant'

/** ====== 状态 ====== */
const query = ref('')
const open  = ref(false)
const filters = reactive({
  Threatened:'', edible:'', medicinal:'', fruits:'',
  indoors:'', rare:'', flowers:'',
  sun:'', cycle:'', watering:'', growth:''
})


const listening = ref(false)
const speechSupported = typeof window !== 'undefined' && 'webkitSpeechRecognition' in window
let recognizer = null

onMounted(() => {
  if (!speechSupported) return
  const SR = window.webkitSpeechRecognition
  const rec = new SR()
  rec.continuous = false
  rec.interimResults = false
  rec.lang = 'zh-CN'
  rec.onresult = (e) => {
    const t = Array.from(e.results).map(r => r[0].transcript).join(' ')
    query.value = (query.value ? query.value + ' ' : '') + t
  }
  rec.onstart = () => listening.value = true
  rec.onend   = () => listening.value = false
  recognizer = rec
})
const startVoice = () => recognizer && recognizer.start()

/** ====== 图片上传（预览 + 占位上传接口） ====== */
const previewUrl = ref('')
const previewName = ref('')
const onImageChange = async (ev) => {
  const f = ev.target.files?.[0]
  if (!f) return
  previewName.value = f.name
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = URL.createObjectURL(f)

  // 如果需要以图搜图，解注释以下示例：
  // const fd = new FormData()
  // fd.append('image', f)
  // const res = await fetch('/api/search/image', { method:'POST', body: fd })
  // const data = await res.json()
  // TODO: 使用 data 刷新结果或回填 query
}
const clearPreview = () => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
  previewName.value = ''
}

/** ====== 查询触发（和后端对接） ====== */
const buildParams = () => {
  const params = { query: query.value, ...filters }
  // 把 undefined/null 归一为空字符串
  Object.keys(params).forEach(k => params[k] = params[k] ?? '')
  return new URLSearchParams(params)
}

const onSearch = async () => {
  const qs = buildParams().toString()
  console.log('GET /api/plants?' + qs)
  // const res = await fetch('/api/plants?' + qs)
  // const data = await res.json()
  // TODO: 渲染 data.items
}

const resetFilters = () => {
  Object.keys(filters).forEach(k => filters[k] = '')
}
const applyFilters = () => {
  open.value = false
  onSearch()
}
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
  background: var(--c-primary); color: #fff; cursor: pointer;
  box-shadow: var(--shadow-sm);
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


</style>