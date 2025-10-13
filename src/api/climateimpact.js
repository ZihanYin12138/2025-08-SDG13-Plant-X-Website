// src/api/climateimpact.js
const BASE = 'http://plantx-alb-1374376113.us-east-1.elb.amazonaws.com';

// Recursively flip coordinates
function swapXY(coords) {
  if (!coords) return coords;
  if (typeof coords[0] === 'number' && typeof coords[1] === 'number') {
    return [coords[1], coords[0]];
  }
  return coords.map(c => swapXY(c));
}
// check whether flipping is needed
function needSwap(geo) {
  try {
    const f = geo.features?.[0];
    if (!f) return false;
    const c =
      f.geometry.type === 'Polygon'
        ? f.geometry.coordinates?.[0]?.[0]
        : f.geometry.type === 'MultiPolygon'
        ? f.geometry.coordinates?.[0]?.[0]?.[0]
        : null;
    if (!Array.isArray(c) || c.length < 2) return false;
    return Math.abs(c[1]) > 90;
  } catch { return false; }
}

export async function fetchAusGeoJSON() {
  const res = await fetch(`${BASE}/api/map/geojson`, { method: 'GET' });
  if (!res.ok) throw new Error('Failed to load Australia GeoJSON');
  const geo = await res.json();

  // Unify the state name field
  if (geo && Array.isArray(geo.features)) {
    geo.features.forEach(f => {
      const p = f.properties || {};
      const state = p.state || p.STATE_NAME || p.name || '';
      f.properties = { ...p, state, name: state };
    });
  }

  // Automatically flip when coordinates are reversed
  if (needSwap(geo)) {
    geo.features.forEach(f => {
      const g = f.geometry || {};
      if (g.type === 'Polygon' || g.type === 'MultiPolygon') {
        g.coordinates = swapXY(g.coordinates);
      }
    });
  }
  return geo;
}

export async function fetchYearMapData(year = 2022) {
  const res = await fetch(`${BASE}/api/map/data/${year}`, { method: 'GET' });
  if (!res.ok) throw new Error(`Failed to load map data for year ${year}`);
  return res.json();
}

export async function fetchStateTimeseries(stateName) {
  const safe = encodeURIComponent(stateName);
  const res = await fetch(`${BASE}/api/chart/data/${safe}`, { method: 'GET' });
  if (!res.ok) throw new Error(`Failed to load timeseries for ${stateName}`);
  return res.json();
}
