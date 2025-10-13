// src/api/plantrcmd.js
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
 * GET plantID
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
