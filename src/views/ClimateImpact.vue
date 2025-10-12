<template>
  <div class="climate-impact">
    <header class="page-head">
      <h1>Climate Impact on Threatened Plants</h1>
      <p class="subtitle">悬浮高亮、点击选择州；右侧可叠加多个州查看趋势（Index 与 Temperature）。</p>
    </header>

    <section class="content-grid">
      <!-- 左：Leaflet 交互地图 -->
      <div class="panel map-panel">
        <div class="panel-head">
          <div class="panel-title">Australia</div>
          <div class="year-select">
            <label for="yearRange">Year: <b>{{ selectedYear }}</b></label>
            <input id="yearRange" type="range" :min="minYear" :max="maxYear" step="1" v-model.number="selectedYear" />
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
              <span>{{ visualMin.toFixed(1) }}</span>
              <span>{{ ((visualMin+visualMax)/2).toFixed(1) }}</span>
              <span>{{ visualMax.toFixed(1) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右：多州时间序列（Index + Temperature） -->
      <div class="panel chart-panel">
        <div class="panel-head">
          <div class="panel-title">Time Series</div>
          <div class="checks">
            <span class="fixed">National（默认）</span>
            <label v-for="s in selectableStates" :key="s" class="chk">
              <input type="checkbox" :value="s" v-model="pickedStates" />
              <span>{{ s }}</span>
            </label>
          </div>
        </div>

        <div class="chart-wrap">
          <div v-if="seriesError" class="error">{{ seriesError }}</div>
          <div v-else ref="lineRef" class="echart"></div>
        </div>

        <div class="note">
          2000–2021 为 <b>历史数据（实线）</b>，2022–2027 为 <b>预测数据（虚线）</b>。右轴为温度（°C）。
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { fetchAusGeoJSON, fetchYearMapData, fetchStateTimeseries } from '@/api/climateimpact';

// 右侧折线用 ECharts
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
echarts.use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

// ---------- 业务状态 ----------
const minYear = 2000;
const maxYear = 2027;
const selectedYear = ref(2022);

const leafletRef = ref(null);
let map, canvasRenderer, geoLayer;
let currentYearData = {};
const mapError = ref('');
const visualMin = ref(0);
const visualMax = ref(1);

// 勾选的 5 个州 + 必选 National
const selectableStates = [
  'Australian Capital Territory',
  'New South Wales',
  'South Australia',
  'Victoria',
  'Western Australia'
];
const pickedStates = ref([]); // 用户勾选（默认空）
const mustHave = 'National';

// 折线图
const lineRef = ref(null);
let lineChart = null;
const seriesError = ref('');
const tsCache = new Map();

// 颜色表（同一州：Index 与 Temp 用同色，不同透明度）
const colorMap = {
  National: '#0f5132',
  'Australian Capital Territory': '#1d8a7a',
  'New South Wales': '#3a86ff',
  'South Australia': '#ff006e',
  Victoria: '#8338ec',
  'Western Australia': '#fb5607'
};

// ---------- 生命周期 ----------
onMounted(async () => {
  await nextTick();
  initMap();
  await loadGeoAndData();
  initChart();
  await updateChart(); // 默认 National
  window.addEventListener('resize', resizeAll, { passive: true });
});
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeAll);
  map && map.remove();
  lineChart && lineChart.dispose();
});

// ---------- Leaflet 地图 ----------
function initMap() {
  map = L.map(leafletRef.value, {
    preferCanvas: true,           // 大体量优化：Canvas
    zoomControl: true,
    attributionControl: false
  });
  canvasRenderer = L.canvas({ padding: 0.5 });
  map.setView([-25, 134], 4);
}

async function loadGeoAndData() {
  mapError.value = '';
  try {
    const [geo, yd] = await Promise.all([fetchAusGeoJSON(), fetchYearMapData(selectedYear.value)]);
    currentYearData = yd;
    computeVisualRange(yd);

    if (geoLayer) geoLayer.removeFrom(map);

    geoLayer = L.geoJSON(geo, {
      renderer: canvasRenderer,
      style: f => styleFor(f, yd),
      onEachFeature: (feature, layer) => {
        layer.options.smoothFactor = 1.2; // 大体量优化：抽稀绘制
        layer.on({
          mouseover: e => highlightFeature(e),
          mouseout: e => resetHighlight(e),
          click: e => toggleStateFromMap(e, feature)
        });
      }
    }).addTo(map);

    try { map.fitBounds(geoLayer.getBounds(), { padding: [10, 10] }); } catch {}
  } catch (e) {
    console.error(e);
    mapError.value = '地图数据加载失败，请稍后再试。';
  }
}

function styleFor(feature, yearData) {
  const name = feature?.properties?.name || '';
  const v = typeof yearData[name] === 'number' ? yearData[name] : null;
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
  const name = layer.feature?.properties?.name || '';
  const v = currentYearData[name];
  const val = (typeof v === 'number') ? v.toFixed(3) : 'N/A';
  layer.bindTooltip(`${name}<br/>Index: <b>${val}</b>`, { sticky: true }).openTooltip(e.latlng);
}
function resetHighlight(e) {
  geoLayer.resetStyle(e.target);
  e.target.closeTooltip();
}
function toggleStateFromMap(e, feature) {
  const name = feature?.properties?.name || '';
  if (!selectableStates.includes(name)) return; // 仅对 5 州起作用
  const i = pickedStates.value.indexOf(name);
  if (i === -1) pickedStates.value.push(name);
  else pickedStates.value.splice(i, 1);
}

function computeVisualRange(yearData) {
  const entries = Object.entries(yearData || {}).filter(([k]) => k !== 'National');
  const vals = entries.map(([, v]) => Number(v)).filter(v => !Number.isNaN(v));
  visualMin.value = vals.length ? Math.min(...vals) : 0;
  visualMax.value = vals.length ? Math.max(...vals) : 1;
}
function getColor(val, min, max) {
  if (val == null || Number.isNaN(val)) return '#E5E7EB';
  const t = Math.max(0, Math.min(1, (val - min) / ((max - min) || 1)));
  const c1 = [212, 233, 221]; // #d4e9dd
  const c2 = [15, 81, 50];    // #0f5132
  const mix = (a,b) => Math.round(a + (b - a) * t);
  return `rgb(${mix(c1[0], c2[0])}, ${mix(c1[1], c2[1])}, ${mix(c1[2], c2[2])})`;
}
async function refreshYear() {
  const yd = await fetchYearMapData(selectedYear.value);
  currentYearData = yd;
  computeVisualRange(yd);
  geoLayer?.setStyle(f => styleFor(f, yd)); // 仅刷新颜色
}

// ---------- 折线图（Index + Temperature） ----------
function initChart() {
  lineChart = echarts.init(lineRef.value);
}

function hexToRgba(hex, alpha = 1) {
  const h = hex.replace('#','');
  const parse = (s) => parseInt(s,16);
  const r = h.length === 3 ? parse(h[0]+h[0]) : parse(h.slice(0,2));
  const g = h.length === 3 ? parse(h[1]+h[1]) : parse(h.slice(2,4));
  const b = h.length === 3 ? parse(h[2]+h[2]) : parse(h.slice(4,6));
  return `rgba(${r},${g},${b},${alpha})`;
}

async function updateChart() {
  seriesError.value = '';
  try {
    const states = [mustHave, ...pickedStates.value];

    // 缓存拉取
    await Promise.all(states.map(async s => {
      if (!tsCache.has(s)) {
        const arr = await fetchStateTimeseries(s);
        tsCache.set(s, arr);
      }
    }));

    const years = Array.from({ length: maxYear - minYear + 1 }, (_, i) => minYear + i);

    const series = [];
    const allTemps = []; // 计算温度轴范围

    states.forEach(state => {
      const arr = tsCache.get(state) || [];
      const idxMap = new Map(arr.map(d => [Number(d.year), Number(d.index_value)]));
      const tMap   = new Map(arr.map(d => [Number(d.year), Number(d.annual_mean_temp)]));

      const color = colorMap[state] || '#2f7e61';
      const tempColor = hexToRgba(color, 0.75);

      const histIndex = years.map(y => (y <= 2021 ? (idxMap.get(y) ?? null) : null));
      const predIndex = years.map(y => (y >  2021 ? (idxMap.get(y) ?? null) : null));
      const histTemp  = years.map(y => { const v = (y <= 2021 ? (tMap.get(y) ?? null) : null); if(v!=null) allTemps.push(v); return v; });
      const predTemp  = years.map(y => { const v = (y >  2021 ? (tMap.get(y) ?? null) : null); if(v!=null) allTemps.push(v); return v; });

      // Index（实线/虚线）
      series.push({
        name: `${state} • Index`,
        type: 'line',
        data: histIndex,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, type: 'solid', color },
        emphasis: { focus: 'series' }
      });
      series.push({
        name: `${state} • Index`,
        type: 'line',
        data: predIndex,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, type: 'dashed', color },
        emphasis: { focus: 'series' }
      });

      // Temperature（右轴，实线/虚线）
      series.push({
        name: `${state} • Temp`,
        type: 'line',
        yAxisIndex: 1,
        data: histTemp,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, type: 'solid', color: tempColor, opacity: 0.95 },
        emphasis: { focus: 'series' }
      });
      series.push({
        name: `${state} • Temp`,
        type: 'line',
        yAxisIndex: 1,
        data: predTemp,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, type: 'dashed', color: tempColor, opacity: 0.95 },
        emphasis: { focus: 'series' }
      });
    });

    const tMin = allTemps.length ? Math.floor(Math.min(...allTemps) - 1) : 10;
    const tMax = allTemps.length ? Math.ceil(Math.max(...allTemps) + 1) : 35;

    lineChart.setOption({
      legend: { type: 'scroll', top: 0, textStyle: { color: '#264b3b' } },
      grid: { left: 55, right: 55, top: 34, bottom: 40 },
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#fff',
        borderColor: '#E5E7EB',
        borderWidth: 1,
        textStyle: { color: '#111827' },
        formatter: params => {
          const year = params?.[0]?.axisValueLabel ?? '';
          const grouped = new Map();
          params.forEach(p => {
            const [state, metric] = (p.seriesName || '').split(' • ');
            if (!grouped.has(state)) grouped.set(state, { idx: null, temp: null });
            if (metric === 'Index') grouped.get(state).idx = p.data;
            else if (metric === 'Temp') grouped.get(state).temp = p.data;
          });
          const lines = [];
          grouped.forEach((v, k) => {
            const idx = v.idx == null ? '-' : Number(v.idx).toFixed(3);
            const tp  = v.temp == null ? '-' : Number(v.temp).toFixed(2) + '°C';
            lines.push(`${k}: Index <b>${idx}</b> · Temp <b>${tp}</b>`);
          });
          return `<b>${year}</b><br/>` + lines.join('<br/>');
        }
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: years,
        axisLabel: { color: '#374151' },
        axisLine: { lineStyle: { color: '#9CA3AF' } }
      },
      yAxis: [
        {
          type: 'value',
          name: 'Plant Index',
          min: 0,
          max: 1.2,
          axisLabel: { color: '#374151' },
          splitLine: { lineStyle: { color: '#E5E7EB' } }
        },
        {
          type: 'value',
          name: 'Mean Temp (°C)',
          min: tMin,
          max: tMax,
          axisLabel: { color: '#374151' },
          splitLine: { show: false }
        }
      ],
      series
    });
  } catch (e) {
    console.error(e);
    seriesError.value = '时间序列加载失败，请稍后再试。';
  }
}

function resizeAll() { lineChart && lineChart.resize(); }

// 监听：年份、勾选项
watch(selectedYear, async () => { await refreshYear(); });
watch(pickedStates, async () => { await updateChart(); }, { deep: true });
</script>

<style scoped>
.climate-impact { padding: 24px 20px 40px; color: #0b3b2d; background: #f3f7f4; }
.page-head h1 { margin: 0 0 6px; font-size: 28px; line-height: 1.2; }
.subtitle { margin: 0 0 18px; color: #325b47; }

.content-grid { display: grid; grid-template-columns: 1.15fr 1fr; gap: 16px; }

.panel { background: #fff; border: 1px solid #e4efe8; border-radius: 14px; box-shadow: 0 1px 2px rgba(16,24,40,.04); overflow: hidden; display: flex; flex-direction: column; }

.panel-head { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; background: #f6faf7; border-bottom: 1px solid #e4efe8; }
.panel-title { font-weight: 600; font-size: 18px; }

.year-select { display: flex; align-items: center; gap: 10px; color: #264b3b; }
.year-select input[type="range"] { width: 200px; }

.map-wrap { position: relative; }
.leaflet-map { width: 100%; height: 460px; }
.leaflet-container { background: #f8faf9; }

.legend { display: grid; grid-template-columns: auto 1fr; gap: 8px 12px; padding: 0 14px 14px; align-items: center; }
.legend-bar { display: grid; gap: 6px; }
.legend-grad { height: 10px; border-radius: 6px; background: linear-gradient(90deg, #d4e9dd 0%, #0f5132 100%); border: 1px solid #e4efe8; }
.legend-ticks { display: flex; justify-content: space-between; color: #6b8a7d; font-size: 12px; }

.chart-panel .checks { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; color: #325b47; }
.chart-panel .checks .fixed { margin-right: 6px; font-weight: 600; }
.chk { display: inline-flex; align-items: center; gap: 6px; user-select: none; }
.chk input { accent-color: #2f7e61; }

.chart-wrap { padding: 10px; }
.echart { width: 100%; height: 440px; }

.note { border-top: 1px solid #e4efe8; padding: 10px 14px; color: #264b3b; }

.error { margin: 10px; padding: 10px 12px; color: #9a3412; background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; }

@media (max-width: 1080px) {
  .content-grid { grid-template-columns: 1fr; }
  .leaflet-map, .echart { height: 360px; }
}
</style>
