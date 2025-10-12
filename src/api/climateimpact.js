// src/api/climateimpact.js
const BASE = 'http://plantx-alb-1374376113.us-east-1.elb.amazonaws.com';

/** ① 澳洲各州 GeoJSON（合并自 geojson.js） */
export async function fetchAusGeoJSON() {
  const res = await fetch(`${BASE}/api/map/geojson`, { method: 'GET' });
  if (!res.ok) throw new Error('Failed to load Australia GeoJSON');
  const geo = await res.json();

  // 规范化：给 feature.properties.name 赋值，便于与指标表匹配
  if (geo && Array.isArray(geo.features)) {
    geo.features.forEach(f => {
      const p = f.properties || {};
      const name =
        p.name ||
        p.STATE_NAME ||
        p.STE_NAME16 ||
        p.ste_name ||
        p.State ||
        p.state_name ||
        '';
      if (!f.properties) f.properties = {};
      f.properties.name = name;
    });
  }
  return geo;
}

/** ② 年份 -> 各州 Threatened Plant Index（choropleth 用） */
export async function fetchYearMapData(year = 2022) {
  const res = await fetch(`${BASE}/api/map/data/${year}`, { method: 'GET' });
  if (!res.ok) throw new Error(`Failed to load map data for year ${year}`);
  return res.json(); // { "Victoria": 0.14, "New South Wales": 0.399, ... }
}

/** ③ 某州时间序列（包含 index_value、annual_mean_temp 等） */
export async function fetchStateTimeseries(stateName) {
  const safeName = encodeURIComponent(stateName);
  const res = await fetch(`${BASE}/api/chart/data/${safeName}`, { method: 'GET' });
  if (!res.ok) throw new Error(`Failed to load timeseries for ${stateName}`);
  return res.json(); // [{ year, index_value, annual_mean_temp, value_type, ... }, ...]
}
