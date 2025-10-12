<template>
  <div class="tp-wrapper">
    <div class="map-wrap">
      <div id="tp-map" class="map"></div>
    </div>

    <aside class="side">
      <header class="side-header">
        <select v-model="selectedState" class="state-select" aria-label="Filter by state">
          <option value="__ALL__">All states</option>
          <option v-for="s in states" :key="s" :value="s">{{ s }}</option>
        </select>
        <div class="count">Found {{ filteredCards.length }} plants</div>
      </header>

      <section class="card-list" v-if="!loading">
        <article
          v-for="p in filteredCards"
          :key="p.id"
          class="plant-card"
          role="button"
          tabindex="0"
          @click="openDetail(p.id)"
          @keyup.enter="openDetail(p.id)"
        >
          <div class="thumb"></div>
          <div class="meta">
            <h3 class="common">{{ p.commonName || humanize(p.binomial) }}</h3>
            <div class="binomial">{{ humanize(p.binomial) }}</div>
            <div class="row">
              <span class="badge" :class="badgeClass(p.maxStatus)">{{ p.maxStatus || 'Unknown' }}</span>
              <span class="region">{{ p.state }}</span>
            </div>
          </div>
        </article>
        <div v-if="filteredCards.length === 0" class="empty">No plants for this state.</div>
      </section>

      <section v-else class="skeleton">
        <div class="sk-item" v-for="i in 6" :key="i"></div>
      </section>
    </aside>

    <!-- 详情弹窗 -->
    <transition name="fade">
      <div v-if="detail.show" class="modal-mask" @click.self="closeDetail">
        <div class="modal" role="dialog" aria-modal="true">
          <button class="modal-close" aria-label="Close" @click="closeDetail">×</button>

          <div v-if="detail.loading" class="modal-loading">
            <div class="spinner"></div>
            <div>Loading plant detail…</div>
          </div>

          <template v-else>
            <header class="modal-head">
              <div class="modal-title">
                <h2>{{ detailTitle }}</h2>
                <div class="sub">{{ humanize(detail.data?.binomial) }}</div>
                <div class="tags">
                  <span class="badge" :class="badgeClass(detail.data?.maxStatus)">
                    {{ detail.data?.maxStatus || 'Unknown' }}
                  </span>
                  <span class="chip" v-if="detail.data?.epbcStatus">EPBC: {{ detail.data.epbcStatus }}</span>
                  <span class="chip" v-if="detail.data?.iucnStatus">IUCN: {{ detail.data.iucnStatus }}</span>
                </div>
              </div>
            </header>

            <section class="modal-body">
              <div class="info-grid">
                <div class="info"><div class="label">State</div><div class="value">{{ detail.data?.state || '—' }}</div></div>
                <div class="info"><div class="label">Region</div><div class="value">{{ detail.data?.region || '—' }}</div></div>
                <div class="info"><div class="label">Latitude</div><div class="value">{{ coordOrDash('lat') }}</div></div>
                <div class="info"><div class="label">Longitude</div><div class="value">{{ coordOrDash('lng') }}</div></div>
              </div>

              <p class="desc" v-if="detail.data?.description" v-text="detail.data.description"></p>
              <p class="desc empty" v-else>No description provided.</p>

              <div class="btns">
                <button class="btn" @click="flyToPlant()">View on map</button>
                <button class="btn outline" @click="closeDetail">Close</button>
              </div>
            </section>
          </template>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getAllPlantsList, getPlantsMapData, getPlantDetail } from '@/api/tpmap';

const loading = ref(true);
const selectedState = ref('__ALL__');
const allPlants = ref([]);     // /plants 的完整 932 条
const mapPlants = ref([]);     // /getPlantsMapData 的点位（较少）
const states = ref([]);
let map, markersLayer, focusRing;

const detail = ref({
  show: false,
  loading: false,
  id: null,
  data: null,
  error: null
});

const humanize = (s) => (s || '').replaceAll('_', ' ');
const badgeClass = (status) => {
  const s = (status || '').toLowerCase();
  return {
    'badge--ce': s === 'critically endangered',
    'badge--en': s === 'endangered',
    'badge--vu': s === 'vulnerable',
  };
};
const statusColor = (status) => {
  switch ((status || '').toLowerCase()) {
    case 'critically endangered': return '#ff3b30';
    case 'endangered': return '#ff6b00';
    case 'vulnerable': return '#f3b300';
    default: return '#6b7280';
  }
};

/** 合并两路数据：优先使用 mapPlants（自带 markerColor / popupContent），
 *  其余用 allPlants 的坐标补齐，保证地图点与列表（~932）一致 */
const unionPoints = computed(() => {
  const byId = new Map();

  (mapPlants.value || []).forEach(p => {
    if (p?.latitude != null && p?.longitude != null) {
      byId.set(String(p.id), { ...p });
    }
  });

  (allPlants.value || []).forEach(p => {
    if (p?.latitude == null || p?.longitude == null) return;
    const key = String(p.id);
    if (!byId.has(key)) {
      byId.set(key, {
        ...p,
        markerColor: statusColor(p.maxStatus),
        popupContent: `
          <strong>${humanize(p.binomial)}</strong><br/>
          Status: ${p.maxStatus || ''}<br/>
          Region: ${p.region || ''}`
      });
    }
  });

  return Array.from(byId.values());
});

const filteredCards = computed(() => {
  if (selectedState.value === '__ALL__') return allPlants.value;
  return allPlants.value.filter(p => p.state === selectedState.value);
});
const filteredMapPoints = computed(() => {
  const pts = unionPoints.value;
  if (selectedState.value === '__ALL__') return pts;
  return pts.filter(p => p.state === selectedState.value);
});
const detailTitle = computed(() => {
  const cn = detail.value?.data?.commonName;
  const bn = humanize(detail.value?.data?.binomial || '');
  return cn || bn || 'Plant detail';
});

onMounted(async () => {
  try {
    const [listAll, mapRes] = await Promise.all([
      getAllPlantsList(),      // 自动 100/页循环到完
      getPlantsMapData()
    ]);

    // /plants 会有全部坐标；做非空判断即可
    allPlants.value = (listAll || []).filter(p => p.latitude != null && p.longitude != null);
    mapPlants.value = mapRes?.plants ?? [];

    // 州来自“合并后的点”，避免漏项
    const s = new Set(unionPoints.value.map(p => p.state).filter(Boolean));
    states.value = Array.from(s).sort();

    initMap();
    renderMarkers();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
});

watch(selectedState, () => renderMarkers());

function initMap() {
  map = L.map('tp-map', { zoomControl: true });
  map.setView([-25.2744, 133.7751], 4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);
  markersLayer = L.layerGroup().addTo(map);
  setTimeout(() => map.invalidateSize(), 150);
}

function renderMarkers() {
  if (!markersLayer) return;
  markersLayer.clearLayers();

  const pts = filteredMapPoints.value;

  // 为了减少完全重合点“看起来丢失”的问题，给相同坐标的点做轻微抖动（肉眼不可察）
  const sameCoordCounter = new Map();
  const jitter = (lat, lng) => {
    const key = `${lat},${lng}`;
    const count = (sameCoordCounter.get(key) || 0) + 1;
    sameCoordCounter.set(key, count);
    if (count === 1) return [lat, lng];
    const r = 0.02 * (Math.ceil(count / 8)) / 10; // ~几十米
    const angle = (count % 8) * (Math.PI / 4);
    return [lat + r * Math.cos(angle), lng + r * Math.sin(angle)];
  };

  pts.forEach(p => {
    const [lat, lng] = jitter(p.latitude, p.longitude);

    const marker = L.circleMarker([lat, lng], {
      radius: 6,
      weight: 2,
      color: '#fff',
      fillOpacity: 0.95,
      fillColor: p.markerColor || statusColor(p.maxStatus),
    });

    const popup =
      (p.popupContent ||
        `<strong>${humanize(p.binomial)}</strong><br/>Status: ${p.maxStatus || ''}<br/>Region: ${p.region || ''}`) +
      `<br/><button class="popup-btn" data-id="${p.id}" style="margin-top:6px;padding:6px 10px;border:none;border-radius:8px;background:#111;color:#fff;cursor:pointer;">详情</button>`;

    marker.bindPopup(popup);
    marker.on('popupopen', e => {
      const btn = e.popup.getElement().querySelector('.popup-btn');
      if (btn) btn.addEventListener('click', () => openDetail(p.id), { once: true });
    });
    marker.on('dblclick', () => openDetail(p.id));
    marker.addTo(markersLayer);
  });

  if (pts.length) {
    try {
      const group = L.featureGroup(markersLayer.getLayers());
      const b = group.getBounds().pad(0.2);
      if (b.isValid()) map.fitBounds(b, { maxZoom: 10 });
    } catch {}
  }
}

async function openDetail(id) {
  detail.value.show = true;
  detail.value.loading = true;
  detail.value.error = null;
  detail.value.id = id;
  detail.value.data = null;

  try {
    const res = await getPlantDetail(id);
    const plant = res?.plant ?? res?.data ?? res;

    const fromList =
      allPlants.value.find(x => String(x.id) === String(id)) ||
      unionPoints.value.find(x => String(x.id) === String(id));

    detail.value.data = { ...fromList, ...(plant || {}) };
    highlightOnMap(detail.value.data);
  } catch (e) {
    console.error(e);
    detail.value.error = 'Failed to load plant detail.';
  } finally {
    detail.value.loading = false;
  }
}

function closeDetail() {
  detail.value.show = false;
  removeHighlight();
}

function coordOrDash(type) {
  const d = detail.value.data || {};
  if (type === 'lat') return d.latitude != null ? d.latitude : '—';
  if (type === 'lng') return d.longitude != null ? d.longitude : '—';
  return '—';
}

function flyToPlant() {
  const d = detail.value.data;
  if (!d || d.latitude == null || d.longitude == null) return;
  map.flyTo([d.latitude, d.longitude], Math.max(map.getZoom(), 8), { duration: 0.6 });
}

function highlightOnMap(d) {
  removeHighlight();
  if (!d || d.latitude == null || d.longitude == null) return;
  focusRing = L.circle([d.latitude, d.longitude], {
    radius: 20000,
    color: '#111',
    weight: 1,
    fillColor: '#111',
    fillOpacity: 0.08
  }).addTo(map);
}

function removeHighlight() {
  if (focusRing) {
    focusRing.remove();
    focusRing = null;
  }
}
</script>

<style scoped>
.tp-wrapper{ display:grid; grid-template-columns: 1fr 380px; gap:16px; height:calc(100vh - 24px); padding:12px; }
.map-wrap{ background:#f3f4f6; border-radius:16px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,.06); }
.map{ width:100%; height:100%; min-height:540px; }

.side{ display:flex; flex-direction:column; background:#fff; border-radius:16px; box-shadow:0 2px 8px rgba(0,0,0,.06); overflow:hidden; }
.side-header{ display:flex; align-items:center; gap:10px; padding:12px; border-bottom:1px solid #eee; position:sticky; top:0; background:#fff; z-index:1;}
.state-select{ flex:1; height:40px; border:1px solid #e5e7eb; border-radius:12px; padding:0 12px; background:#fafafa; }
.count{ font-size:12px; color:#6b7280; white-space:nowrap; }
.card-list{ padding:8px 10px 14px 10px; overflow-y:auto; }
.empty{ color:#6b7280; font-size:13px; padding:12px; text-align:center; }

.plant-card{ display:grid; grid-template-columns:84px 1fr; gap:12px; padding:10px; border-radius:14px; border:1px solid #f0f1f3; margin-bottom:10px; cursor:pointer; transition:transform .08s ease, box-shadow .12s ease; background:#fff; }
.plant-card:hover{ transform: translateY(-1px); box-shadow:0 6px 18px rgba(0,0,0,.06); }
.thumb{ width:84px; height:84px; border-radius:12px; background:#f3f4f6; }
.meta{ display:flex; flex-direction:column; gap:6px; }
.common{ margin:0; font-size:16px; color:#111827; font-weight:700; }
.binomial{ font-size:12px; color:#6b7280; }
.row{ display:flex; align-items:center; gap:8px; }

.badge{ font-size:12px; padding:3px 8px; border-radius:12px; background:#e5e7eb; color:#111827; font-weight:600; }
.badge--ce{ background:#ffe6e6; color:#b30000; }
.badge--en{ background:#fff0e6; color:#b34700; }
.badge--vu{ background:#fff7da; color:#9a7b00; }
.region{ font-size:12px; color:#6b7280; }

.skeleton{ padding:12px; }
.sk-item{ height:88px; border-radius:14px; background:linear-gradient(90deg,#f3f4f6 25%, #eceef1 37%, #f3f4f6 63%); background-size:400% 100%; animation:shine 1.2s infinite; margin-bottom:10px; }
@keyframes shine{ 0%{background-position:100% 50%} 100%{background-position:0 50%} }

.modal-mask{ position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; padding:20px; z-index:999; }
.modal{ width:min(860px, 94vw); background:#fff; border-radius:16px; box-shadow:0 20px 60px rgba(0,0,0,.25); position:relative; }
.modal-close{ position:absolute; right:10px; top:8px; width:36px; height:36px; border:none; border-radius:10px; font-size:22px; line-height:1; background:#f3f4f6; color:#111; cursor:pointer; }
.modal-head{ display:flex; gap:16px; padding:18px 18px 6px 18px; border-bottom:1px solid #f1f1f3; }
.modal-title h2{ margin:0; font-size:20px; line-height:1.2; }
.sub{ font-size:13px; color:#6b7280; margin-top:4px; }
.tags{ margin-top:8px; display:flex; gap:8px; flex-wrap:wrap; }
.chip{ font-size:12px; padding:3px 8px; border-radius:12px; background:#f5f5f5; color:#374151; }

.modal-body{ padding:16px 18px 18px 18px; }
.info-grid{ display:grid; grid-template-columns:repeat(2,1fr); gap:12px; }
.info .label{ font-size:12px; color:#6b7280; }
.info .value{ font-size:14px; color:#111827; font-weight:600; }
.desc{ margin-top:12px; font-size:14px; line-height:1.6; color:#374151; white-space:pre-wrap; }
.desc.empty{ color:#9ca3af; }
.btns{ display:flex; gap:10px; margin-top:16px; }
.btn{ padding:8px 12px; border-radius:10px; border:none; background:#111; color:#fff; cursor:pointer; }
.btn.outline{ background:#fff; color:#111; border:1px solid #e5e7eb; }

.modal-loading{ display:flex; flex-direction:column; align-items:center; justify-content:center; gap:12px; padding:48px 18px; }
.spinner{ width:26px; height:26px; border-radius:50%; border:3px solid #e5e7eb; border-top-color:#111; animation:spin 0.9s linear infinite; }
@keyframes spin{ to{ transform: rotate(360deg); } }

.fade-enter-active, .fade-leave-active{ transition: opacity .15s ease; }
.fade-enter-from, .fade-leave-to{ opacity: 0; }

@media (max-width: 1100px){
  .tp-wrapper{ grid-template-columns: 1fr; height:auto; }
  .map{ min-height:420px; }
}
</style>
