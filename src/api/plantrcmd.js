// src/api/plantrcmd.js
// 可按你的 axios 实例风格改写；这里用 fetch 示例。
// 后端路由仅作示例，请按实际接口名调整。

const JSON_HEADERS = { 'Content-Type': 'application/json' }

// 1) 16 天聚合天气
export async function fetchWeatherAggregate (lat, lng) {
  const resp = await fetch('/api/plantrcmd/aggregate-weather', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({ lat, lng, horizon_days: 16 })
  })
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
  return await resp.json()
}

// 2) 植物推荐
export async function fetchRecommendations (lat, lng) {
  const resp = await fetch('/api/plantrcmd/recommendations', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({ lat, lng, horizon_days: 16 })
  })
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
  return await resp.json()
}
