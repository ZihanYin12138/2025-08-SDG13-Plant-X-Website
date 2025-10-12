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

/** 单页列表（GET） */
export function getPlantsList({ page = 1, limit = 100 } = {}) {
  // 接口要求 1-100
  const safeLimit = Math.min(100, Math.max(1, Math.floor(limit)));
  return getJSON(`${BASE}/plants${toQS({ page, limit: safeLimit })}`);
}

/** 全部分页抓取（每页最多 100，直到 hasNext 为 false） */
export async function getAllPlantsList(limitPerPage = 100) {
  const limit = Math.min(100, Math.max(1, Math.floor(limitPerPage)));
  let page = 1;
  let hasNext = true;
  const all = [];

  while (hasNext) {
    const { plants = [], pagination = {} } = await getPlantsList({ page, limit });
    all.push(...plants);

    // 优先使用服务端分页标志
    if (typeof pagination?.hasNext === 'boolean') {
      hasNext = pagination.hasNext;
      page = (pagination.page || page) + 1;
    } else if (pagination?.totalPages && pagination?.page) {
      hasNext = pagination.page < pagination.totalPages;
      page += 1;
    } else {
      // 兜底：拿到的数量小于 limit 说明已经最后一页
      hasNext = plants.length === limit;
      page += 1;
    }

    // 安全阈值，防止意外死循环
    if (page > 200) break;
  }
  return all;
}

/** 地图点位（GET） */
export function getPlantsMapData() {
  return getJSON(`${BASE}/getPlantsMapData`);
}

/** 植物详情（GET，使用 plantId 参数） */
export function getPlantDetail(plantId) {
  return getJSON(`${BASE}/getPlantDetail${toQS({ plantId })}`);
}
