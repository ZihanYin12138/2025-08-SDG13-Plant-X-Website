// src/api/pdisease.js
const BASE = 'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx/diseases'
const DEFAULT_SEEDS = ['a', 'e', 'i', 'o', 'u']

function mapItem(raw) {
  const id = raw.plant_disease_id
  const name = raw.common_name || ''
  const scientific_name = raw.scientific_name || ''
  const images = Array.isArray(raw.regular_url_images) ? raw.regular_url_images : []
  const hosts = Array.isArray(raw.host) ? raw.host : (raw.host ? [raw.host] : [])
  const alias = Array.isArray(raw.other_name) ? raw.other_name : (raw.other_name ? [raw.other_name] : [])

  const descArr = Array.isArray(raw.description) ? raw.description : []
  const solArr  = Array.isArray(raw.solution)    ? raw.solution    : []

  const symptoms  = (descArr[0]?.description || '').trim()
  const diagnosis = (descArr[1]?.description || '').trim()
  const treatment = solArr
    .map(s => {
      const t = s.subtitle ? `${s.subtitle}\n` : ''
      return `${t}${s.description || ''}`.trim()
    })
    .filter(Boolean)
    .join('\n\n')

  return {
    id,
    name,
    scientific_name,
    images,
    hosts,
    alias,
    symptoms,
    diagnosis,
    treatment,
    prevention: '',
  }
}

async function fetchText(url) {
  const res = await fetch(url)
  const text = await res.text()
  if (!res.ok) throw new Error(`Disease API failed: HTTP ${res.status} - ${text}`)
  return text
}
async function fetchJson(url) {
  const text = await fetchText(url)
  return JSON.parse(text)
}

function pickTotal(data) {
  const candidates = [
    data?.total,
    data?.Total,
    data?.count,
    data?.total_count,
    data?.TotalCount,
    data?.totalItems,
    data?.TotalItems,
  ]
  for (const v of candidates) {
    if (typeof v === 'number' && Number.isFinite(v)) return v
    if (typeof v === 'string' && /^\d+$/.test(v)) return Number(v)
  }
  return null
}

export async function searchDiseases(q, { page = 1, pageSize = 8 } = {}) {
  const query = (q && q.trim()) ? q.trim() : ''
  const offset = Math.max(0, (Number(page) || 1) - 1) * pageSize

  // If there is no search term, use seeds to remove duplicates and count the total
  if (!query) {
    const idSet = new Set()

    for (const s of DEFAULT_SEEDS) {
      let innerOffset = 0
      let hasMore = true

      while (hasMore) {
        const data = await fetchJson(`${BASE}?q=${encodeURIComponent(s)}&limit=50&offset=${innerOffset}`)
        const items = Array.isArray(data.items) ? data.items : []
        for (const item of items) {
          idSet.add(item.plant_disease_id)
        }
        innerOffset += items.length
        hasMore = items.length > 0 && items.length === 50
      }
    }

    const total = idSet.size

    // By default, use the first seed to get the first page of data
    const data1 = await fetchJson(`${BASE}?q=${encodeURIComponent(DEFAULT_SEEDS[0])}&limit=${pageSize}&offset=${offset}`)
    const items1 = Array.isArray(data1.items) ? data1.items.map(mapItem) : []
    const hasNext = offset + items1.length < total

    return {
      items: items1,
      page,
      pageSize,
      total,
      hasNext,
    }
  }

  // With search terms: follow the original logic
  const baseUrl = `${BASE}?q=${encodeURIComponent(query)}&limit=${pageSize}&offset=${offset}`
  const data1 = await fetchJson(baseUrl)
  const items1 = Array.isArray(data1.items) ? data1.items.map(mapItem) : []

  const knownTotal = pickTotal(data1)
  if (knownTotal !== null) {
    const hasNext = offset + items1.length < knownTotal
    return {
      items: items1,
      page,
      pageSize,
      total: knownTotal,
      hasNext,
    }
  }

  // —— No total: do overfetch (get 1 more record) to determine if there is a next page —— //
  const overfetch = pageSize + 1
  const overUrl = `${BASE}?q=${encodeURIComponent(query)}&limit=${overfetch}&offset=${offset}`
  const data2 = await fetchJson(overUrl)
  const items2 = Array.isArray(data2.items) ? data2.items.map(mapItem) : []
  const hasNext = items2.length > pageSize

  const items = items2.slice(0, pageSize)
  const softTotal = hasNext
    ? offset + pageSize + 1
    : offset + items.length

  return {
    items,
    page,
    pageSize,
    total: softTotal,
    hasNext,
  }
}

export async function getDiseaseById(id) {
  const byIdUrl = `${BASE}?plant_disease_id=${encodeURIComponent(id)}`
  try {
    const data = await fetchJson(byIdUrl)
    const first = Array.isArray(data.items) ? data.items[0] : null
    if (first) return mapItem(first)
  } catch {}
  const seeds = ['a', 'e', 'i', 'o', 'u', 'r', 's', 't', 'n']
  const seen = new Set()
  for (const s of seeds) {
    const url = `${BASE}?q=${encodeURIComponent(s)}&limit=50&offset=0`
    const data = await fetchJson(url)
    const arr = Array.isArray(data.items) ? data.items : []
    for (const raw of arr) {
      const it = mapItem(raw)
      if (seen.has(it.id)) continue
      seen.add(it.id)
      if (String(it.id) === String(id)) return it
    }
  }
  throw new Error(`Disease not found for id=${id}`)
}

export async function expandPredictionsToDiseases(predictions = []) {
  function pickId(p = {}) {
    const raw =
      p.predicted_id ??
      p.disease_id ??
      p.plant_disease_id ??
      p.id ??
      p?.disease?.id ??
      p?.prediction?.id
    const n = Number(raw)
    return Number.isFinite(n) ? n : null
  }

  const uniqueIds = Array.from(
    new Set(
      predictions.map(p => pickId(p)).filter(n => n != null)
    )
  )

  const details = await Promise.all(uniqueIds.map(id => getDiseaseById(id).catch(() => null)))
  const id2meta = new Map(predictions.map(p => [pickId(p), p]))

  return details
    .filter(Boolean)
    .map(d => {
      const m = id2meta.get(Number(d.id)) || {}
      const prob =
        (m.score != null ? m.score : null) ??
        (m.probability != null ? m.probability : null) ??
        (m.confidence != null ? m.confidence : null)
      return { ...d, probability: prob }
    })
}

export default {
  searchDiseases,
  getDiseaseById,
  expandPredictionsToDiseases,
}
