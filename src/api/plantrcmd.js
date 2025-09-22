// src/api/plantrcmd.js
// GET /plant_recommendation?lat=..&lon=..
// 返回中可能字段名不同，这里统一归一到 recommended_plant_ids

const BASE_URL =
  'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx/plant_recommendation'

function normalizeIds(json = {}) {
  const ids =
    json.recommended_plant_ids ||
    json.recommended_ids ||
    json.plant_ids ||
    json.ids ||
    (Array.isArray(json.items) ? json.items.map(it => it.id) : []) ||
    []
  return Array.isArray(ids) ? ids : []
}

/**
 * GET 推荐植物ID
 * @param {number} lat
 * @param {number} lng
 * @returns {Promise<{ recommended_plant_ids: number[] } & any>}
 */
export async function getRecommendations(lat, lng) {
  const url = `${BASE_URL}?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lng)}`
  const res = await fetch(url, { method: 'GET' })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Request failed: ${res.status}`)
  }
  const json = await res.json().catch(() => ({}))
  return { ...json, recommended_plant_ids: normalizeIds(json) }
}
