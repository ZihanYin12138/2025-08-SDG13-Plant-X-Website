// src/api/plantrcmd.js
// 约定后端返回：{ weather: {...}, recommended_ids: [1,2,3,...] }
// 若字段名不同（如 plant_ids / ids / kpi / metrics），下方会做兼容映射。

const RCMD_ENDPOINT = '/api/plantrcmd' // ← 修改为你的真实接口路径

function normalizeBundle(json = {}) {
  // 天气聚合字段兼容
  const weather = json.weather || json.kpi || json.metrics || {}
  // 推荐 ID 列表兼容
  const ids =
    json.recommended_ids ||
    json.plant_ids ||
    json.ids ||
    (Array.isArray(json.items) ? json.items.map(it => it.id) : []) ||
    []

  return { weather, recommended_ids: Array.isArray(ids) ? ids : [] }
}

/**
 * POST 经纬度，返回 { weather, recommended_ids }
 * @param {number} lat
 * @param {number} lng
 */
export async function postCoordinates(lat, lng) {
  const res = await fetch(RCMD_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lat, lng })
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Request failed: ${res.status}`)
  }
  const json = await res.json()
  return normalizeBundle(json)
}
