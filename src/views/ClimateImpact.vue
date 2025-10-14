<template>
  <section>
    <h2>Climate Impact on Threatened Plants</h2>
    <p>
      Use the map to select a state and explore its Threatened Species Index (TSX) over time.
      <br>Adjust the year slider to view changes from 2000–2027 — dotted lines show projections.
      <br>Switch between temperature, rainfall, and radiation to see how climate links to species trends.
      <br>Please wait a moment, map and chart is loading...
    </p>

    <section class="content-grid">
      <!-- Left: Leaflet interactive map -->
      <div class="panel map-panel">
        <div class="panel-head">
          <div class="panel-title">Australia</div>
          <div class="year-select">
            <label for="yearRange">Year: <b>{{ selectedYear }}</b></label>
            <input
              id="yearRange"
              type="range"
              :min="minYear"
              :max="maxYear"
              step="1"
              v-model.number="selectedYear"
            />
          </div>
        </div>

        <div class="map-wrap">
          <div v-if="mapError" class="error">{{ mapError }}</div>
          <div v-else ref="leafletRef" class="leaflet-map"></div>
        </div>

        <div class="legend">
          <span>Threatened Plant Index</span>
          <div class="legend-bar">
            <div class="legend-grad"></div>
            <div class="legend-ticks">
              <span>0.0</span>
              <span>0.5</span>
              <span>1.0</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Time Series -->
      <div class="panel chart-panel">
        <div class="panel-head">
          <div class="panel-title">
            {{ selectedState }}<br /><small>• Time Series</small>
          </div>

          <!-- Segmented button selector -->
          <div class="segmented">
            <span class="seg-label">Metric:</span>
            <div class="seg-group">
              <button
                v-for="(m, i) in metrics"
                :key="m.key"
                class="seg-btn"
                :class="{ active: metricIdx === i }"
                @click="metricIdx = i"
              >
                {{ m.short }}
              </button>
            </div>
          </div>
        </div>

        <div class="chart-wrap">
          <div v-if="seriesError" class="error">{{ seriesError }}</div>
          <div v-else ref="lineRef" class="echart"></div>
        </div>

        <div class="note">
          2000–2021 is the <b>historical data (solid line)</b>, <br />2022–2027 is the
          <b>forecast data (dashed line)</b>.
        </div>
      </div>
    </section>
  </section>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { fetchAusGeoJSON, fetchYearMapData, fetchStateTimeseries } from '@/api/climateimpact';

import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
echarts.use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const cssVar = (name, fallback = '') =>
  (getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback);

const minYear = 2000;
const maxYear = 2027;
const selectedYear = ref(2022);

const VALUE_STATES = new Set([
  'Australian Capital Territory',
  'New South Wales',
  'South Australia',
  'Victoria',
  'Western Australia'
]);

const visualMin = ref(0);
const visualMax = ref(1);

const metrics = [
  { key: 'annual_mean_temp', label: 'Mean Temperature', short: 'Mean Temp', unit: '°C' },
  { key: 'annual_precip_sum', label: 'Precipitation Sum', short: 'Precip Sum', unit: '' },
  { key: 'annual_radiation_sum', label: 'Radiation Sum', short: 'Radiation Sum', unit: '' }
];
const metricIdx = ref(0);
const currentMetric = () => metrics[metricIdx.value];

const selectedState = ref('National');
const lineRef = ref(null);
let lineChart = null;
const seriesError = ref('');
const tsCache = new Map();

const leafletRef = ref(null);
let map, canvasRenderer, geoLayer;
let currentYearData = {};
const mapError = ref('');

// ---- life cycle ----
onMounted(async () => {
  await nextTick();
  initMap();
  await loadGeoAndData();
  await nextTick();
  initChart();
  await updateChart();
  window.addEventListener('resize', resizeAll, { passive: true });
});
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeAll);
  map && map.remove();
  lineChart && lineChart.dispose();
});

// ---- Leaflet ----
function initMap() {
  map = L.map(leafletRef.value, {
    preferCanvas: true,
    zoomControl: true,
    attributionControl: false
  });
  canvasRenderer = L.canvas({ padding: 0.5 });
  canvasRenderer.addTo(map);
  map.setView([-25, 134], 10);
}

async function loadGeoAndData() {
  mapError.value = '';
  try {
    const [geo, yd] = await Promise.all([fetchAusGeoJSON({ sampleStep: 10, precision: 3 }), fetchYearMapData(selectedYear.value)]);
    currentYearData = yd;

    if (geoLayer) geoLayer.removeFrom(map);

    geoLayer = L.geoJSON(geo, {
      renderer: canvasRenderer,
      style: f => styleFor(f, yd),
      onEachFeature: (feature, layer) => {
        layer.options.smoothFactor = 1.2;
        layer.on({
          mouseover: e => highlightFeature(e),
          mouseout: e => resetHighlight(e),
          click: () => onFeatureClick(feature)
        });
      }
    }).addTo(map);

    try {
      map.fitBounds(geoLayer.getBounds(), { padding: [10, 10] });
    } catch {}
  } catch (e) {
    console.error(e);
    mapError.value = 'Map load fail，please try again.';
  }
}

function styleFor(feature, yearData) {
  const st = feature?.properties?.state || feature?.properties?.name || '';
  if (!VALUE_STATES.has(st)) {
    return { fillColor: '#E5E7EB', weight: 1, color: '#ffffff', opacity: 1, fillOpacity: 0.7 };
  }
  const v = yearData[st];
  return {
    fillColor: getColor(v, visualMin.value, visualMax.value),
    weight: 1,
    color: '#ffffff',
    opacity: 1,
    fillOpacity: 0.85
  };
}
function highlightFeature(e) {
  const layer = e.target;
  layer.setStyle({ weight: 2, color: '#2f7e61', fillOpacity: 0.95 });
  const st = layer.feature?.properties?.state || layer.feature?.properties?.name || '';
  let label = st;
  let val = '-';
  if (VALUE_STATES.has(st)) {
    const v = currentYearData[st];
    val = typeof v === 'number' ? v.toFixed(3) : 'N/A';
  } else {
    const nv = currentYearData['National'];
    val = typeof nv === 'number' ? nv.toFixed(3) : 'N/A';
    label += ' (showing National on click)';
  }
  layer.bindTooltip(`${label}<br/>Index: <b>${val}</b>`, { sticky: true }).openTooltip();
}
function resetHighlight(e) {
  geoLayer.resetStyle(e.target);
  e.target.closeTooltip();
}
async function onFeatureClick(feature) {
  const st = feature?.properties?.state || feature?.properties?.name || '';
  selectedState.value = VALUE_STATES.has(st) ? st : 'National';
  await updateChart();
}

function getColor(val, min, max) {
  let t = (Number(val) - min) / ((max - min) || 1);
  t = Math.max(0, Math.min(1, t));
  const c1 = [212, 233, 221];
  const c2 = [15, 81, 50];
  const mix = (a, b) => Math.round(a + (b - a) * t);
  return `rgb(${mix(c1[0], c2[0])}, ${mix(c1[1], c2[1])}, ${mix(c1[2], c2[2])})`;
}
async function refreshYear() {
  const yd = await fetchYearMapData(selectedYear.value);
  currentYearData = yd;
  geoLayer?.setStyle(f => styleFor(f, yd));
}

// ---- chart ----
async function initChart() {
  await nextTick();
  if (!lineRef.value || !(lineRef.value instanceof HTMLElement)) {
    throw new Error('Initialize failed: invalid dom (lineRef missing).');
  }
  if (!lineChart) lineChart = echarts.init(lineRef.value);
}

async function updateChart() {
  seriesError.value = '';
  const state = selectedState.value || 'National';
  try {
    if (!tsCache.has(state)) {
      const arr = await fetchStateTimeseries(state);
      tsCache.set(state, arr);
    }
  } catch (e) {
    if (state === 'National') {
      selectedState.value = 'Victoria';
      return updateChart();
    }
    seriesError.value = `Time series loading failed：${state}`;
    return;
  }

  const arr = tsCache.get(state) || [];
  const years = Array.from({ length: maxYear - minYear + 1 }, (_, i) => minYear + i);

  const idxMap = new Map(arr.map(d => [Number(d.year), Number(d.index_value)]));
  const metKey = currentMetric().key;
  const metMap = new Map(arr.map(d => [Number(d.year), Number(d[metKey])]));

  const histIdx = years.map(y => (y <= 2021 ? (idxMap.get(y) ?? null) : null));
  const predIdx = years.map(y => (y >= 2021 ? (idxMap.get(y) ?? null) : null));
  const histMet = years.map(y => (y <= 2024 ? (metMap.get(y) ?? null) : null));
  const predMet = years.map(y => (y >= 2024 ? (metMap.get(y) ?? null) : null));

  const metVals = arr.map(d => Number(d[metKey])).filter(v => !Number.isNaN(v));
  const tMin = metVals.length ? Math.floor(Math.min(...metVals) - 1) : 0;
  const tMax = metVals.length ? Math.ceil(Math.max(...metVals) + 1) : 10;

  const brand = cssVar('--brand', '#0f5132');
  const accent = cssVar('--accent', '#3a86ff');
  const card = cssVar('--card', '#fff');
  const fg = cssVar('--fg', '#111827');
  const border = cssVar('--border', '#E5E7EB');
  const muted = cssVar('--muted', '#6b7280');

  if (lineChart) lineChart.clear();
  lineChart.setOption({
    legend: { top: 0, data: ['Plant Index', currentMetric().label], textStyle: { color: fg } },
    grid: { left: 55, right: 55, top: 34, bottom: 40 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: card,
      borderColor: border,
      borderWidth: 1,
      textStyle: { color: fg },
      formatter: params => {
        const year = params?.[0]?.axisValueLabel ?? '';
        let idxVal = null;
        let metVal = null;
        for (const p of params) {
          if (p.seriesName === 'Plant Index' && p.data != null && idxVal == null) {
            idxVal = Number(p.data);
          }
          if (p.seriesName === currentMetric().label && p.data != null && metVal == null) {
            metVal = Number(p.data);
          }
        }
        const idx = idxVal == null ? '-' : idxVal.toFixed(3);
        const unit = currentMetric().unit;
        const met =
          metVal == null
            ? '-'
            : unit
            ? `${metVal.toFixed(2)}${unit}`
            : metVal.toFixed(2);

        return `<b>${state}</b> · ${year}<br/>Plant Index: <b>${idx}</b><br/>${currentMetric().label}: <b>${met}</b>`;
      }
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: years,
      axisLabel: { color: muted },
      axisLine: { lineStyle: { color: border } }
    },
    yAxis: [
      {
        type: 'value',
        name: 'Plant Index',
        min: 0,
        max: 1,
        axisLabel: { color: muted },
        splitLine: { lineStyle: { color: border } }
      },
      {
        type: 'value',
        name: currentMetric().unit
          ? `${currentMetric().label} (${currentMetric().unit})`
          : currentMetric().label,
        min: tMin,
        max: tMax,
        axisLabel: { color: muted },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        id: 'idx_hist',
        name: 'Plant Index',
        type: 'line',
        data: histIdx,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, type: 'solid', color: brand }
      },
      {
        id: 'idx_pred',
        name: 'Plant Index',
        type: 'line',
        data: predIdx,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, type: 'dashed', color: brand }
      },
      {
        id: `met_hist_${metKey}`,
        name: currentMetric().label,
        type: 'line',
        yAxisIndex: 1,
        data: histMet,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, type: 'solid', color: accent }
      },
      {
        id: `met_pred_${metKey}`,
        name: currentMetric().label,
        type: 'line',
        yAxisIndex: 1,
        data: predMet,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, type: 'dashed', color: accent }
      }
    ]
  });

  lineChart.resize();
}

function resizeAll() {
  lineChart && lineChart.resize();
}

// watch
watch(selectedYear, async () => { await refreshYear(); });
watch(metricIdx, async () => { await updateChart(); });
watch(selectedState, async () => { await updateChart(); });
</script>

<style scoped>
.climate-impact {
  padding: 24px 20px 40px;
  color: var(--fg);
  background: var(--surface);
}

.content-grid {
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  gap: 16px;
}

.panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: var(--shadow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  color: var(--fg);
  width: auto;
}

/* Leaflet */
.map-panel,
.leaflet-map { position: relative; z-index: 0; }
:deep(.leaflet-container) { z-index: 0; background: var(--card); color: var(--fg); }
:deep(.leaflet-pane),
:deep(.leaflet-tooltip-pane),
:deep(.leaflet-popup-pane),
:deep(.leaflet-overlay-pane),
:deep(.leaflet-marker-pane),
:deep(.leaflet-shadow-pane),
:deep(.leaflet-map-pane),
:deep(.leaflet-tile-pane) { z-index: 1 !important; }
:deep(.leaflet-top),
:deep(.leaflet-bottom),
:deep(.leaflet-control-container) { z-index: 1 !important; }
:deep(.leaflet-popup-content-wrapper){ background: var(--card); color: var(--fg); border:1px solid var(--border); box-shadow: var(--shadow-md); border-radius: 10px; }
:deep(.leaflet-popup-tip){ background: var(--card); border:1px solid var(--border); }

.panel-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px;
  background: color-mix(in oklab, var(--card) 92%, transparent);
  border-bottom: 1px solid var(--border);
}
.panel-title { font-weight: 700; font-size: 18px; }
.panel-title small { font-weight: 600; color: var(--muted); }

.year-select { display: flex; align-items: center; gap: 10px; color: var(--fg); }
.year-select input[type="range"] { width: 220px; accent-color: var(--brand); }

.segmented { display: flex; align-items: center; gap: 10px; color: var(--fg); }
.seg-label { font-weight: 600; margin-right: 2px; color: var(--muted); }
.seg-group { display: inline-flex; background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 2px; }
.seg-btn { border: 0; background: transparent; padding: 4px 10px; border-radius: 999px; cursor: pointer; font-size: 12px; color: var(--fg); }
.seg-btn.active { background: var(--brand); color: #00241a; }

.map-wrap { position: relative; }
.leaflet-map { width: 100%; height: 460px; }

.legend { display: grid; grid-template-columns: auto 1fr; gap: 8px 12px; padding: 0 14px 14px; align-items: center; color: var(--fg); }
.legend-bar { display: grid; gap: 6px; }
.legend-grad {
  height: 10px; border-radius: 6px;
  background: linear-gradient(90deg, color-mix(in oklab, var(--brand) 18%, var(--card)) 0%, var(--brand) 100%);
  border: 1px solid var(--border);
}
.legend-ticks { display: flex; justify-content: space-between; color: var(--muted); font-size: 12px; }

.chart-wrap { padding: 10px; }
.echart { width: 100%; height: 440px; }

.note { border-top: 1px solid var(--border); padding: 10px 14px; color: var(--muted); }

.error {
  margin: 10px; padding: 10px 12px;
  color: #9a3412; background: color-mix(in oklab, #fed7aa 65%, var(--card));
  border: 1px solid #fed7aa; border-radius: 8px;
}

@media (max-width: 1080px) {
  .content-grid { grid-template-columns: 1fr; }
  .leaflet-map, .echart { height: 360px; }
}
</style>
