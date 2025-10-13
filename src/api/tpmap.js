// src/api/tpmap.js —— 使用原生 fetch（GET）

const BASE =
  'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx/getPlantsList';

function toQS(params = {}) {
  const s = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') s.set(k, String(v));
  });
  const str = s.toString();
  return str ? `?${str}` : '';
}

async function getJSON(url) {
  const res = await fetch(url, { method: 'GET' });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status} ${res.statusText} - ${text}`);
  }
  return res.json();
}

/** Single page list (GET) */
export function getPlantsList({ page = 1, limit = 100 } = {}) {
 // Interface requirements 1-100
  const safeLimit = Math.min(100, Math.max(1, Math.floor(limit)));
  return getJSON(`${BASE}/plants${toQS({ page, limit: safeLimit })}`);
}

/** Fetch all pages (up to 100 per page, until hasNext is false) */
export async function getAllPlantsList(limitPerPage = 100) {
  const limit = Math.min(100, Math.max(1, Math.floor(limitPerPage)));
  let page = 1;
  let hasNext = true;
  const all = [];

  while (hasNext) {
    const { plants = [], pagination = {} } = await getPlantsList({ page, limit });
    all.push(...plants);

    // Give priority to using the server-side paging flag
    if (typeof pagination?.hasNext === 'boolean') {
      hasNext = pagination.hasNext;
      page = (pagination.page || page) + 1;
    } else if (pagination?.totalPages && pagination?.page) {
      hasNext = pagination.page < pagination.totalPages;
      page += 1;
    } else {
      // Back-up: If the number of items you get is less than the limit, it means you have reached the last page.
      hasNext = plants.length === limit;
      page += 1;
    }
    if (page > 200) break;
  }
  return all;
}

/** Map point */
export function getPlantsMapData() {
  return getJSON(`${BASE}/getPlantsMapData`);
}

/** Plant details */
export function getPlantDetail(plantId) {
  return getJSON(`${BASE}/getPlantDetail${toQS({ plantId })}`);
}
