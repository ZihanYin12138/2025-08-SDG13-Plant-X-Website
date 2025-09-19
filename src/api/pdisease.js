// src/api/pdisease.js
const BASE = 'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx/diseases'
const DEFAULT_SEED = 'a'

// —— 映射一条疾病记录到前端所需结构 —— //
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

// 兼容不同后端“总数字段名”
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

/**
 * 搜索疾病（分页）：
 * - 若后端返回 total：直接用
 * - 若没有 total：overfetch（limit+1）判断 hasNext，并给“渐进式总数”
 */
export async function searchDiseases(q, { page = 1, pageSize = 8 } = {}) {
  const query = (q && q.trim()) ? q.trim() : DEFAULT_SEED
  const offset = Math.max(0, (Number(page) || 1) - 1) * pageSize

  // 先按正常页大小取一次
  const baseUrl = `${BASE}?q=${encodeURIComponent(query)}&limit=${pageSize}&offset=${offset}`
  const data1 = await fetchJson(baseUrl)
  const items1 = Array.isArray(data1.items) ? data1.items.map(mapItem) : []

  // 若后端已经提供 total，直接返回
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

  // —— 没有 total：做 overfetch（多取 1 条）来判断是否还有下一页 —— //
  const overfetch = pageSize + 1
  const overUrl = `${BASE}?q=${encodeURIComponent(query)}&limit=${overfetch}&offset=${offset}`
  const data2 = await fetchJson(overUrl)
  const items2 = Array.isArray(data2.items) ? data2.items.map(mapItem) : []
  const hasNext = items2.length > pageSize

  // 最终用于显示的本页数据
  const items = items2.slice(0, pageSize)

  // “渐进式总数”：不是末页 -> 给最小可能总数，末页 -> 给精确总数
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

/**
 * 详情：优先使用 ?plant_disease_id= 接口；若不支持则回退到种子扫描
 */
export async function getDiseaseById(id) {
  const byIdUrl = `${BASE}?plant_disease_id=${encodeURIComponent(id)}`
  try {
    const data = await fetchJson(byIdUrl)
    const first = Array.isArray(data.items) ? data.items[0] : null
    if (first) return mapItem(first)
  } catch {
    // ignore and fallback
  }

  // 回退：用常见字母 seed 扫描
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

/**
 * 把识别结果扩展成疾病详情（保留概率/置信度）
 * predictions: [{ predicted_id, probability?, confidence? }]
 */
export async function expandPredictionsToDiseases(predictions = []) {
  const uniqueIds = Array.from(
    new Set(predictions.map(p => Number(p.predicted_id)).filter(n => Number.isFinite(n)))
  )
  const details = await Promise.all(uniqueIds.map(id => getDiseaseById(id).catch(() => null)))
  const id2meta = new Map(predictions.map(p => [Number(p.predicted_id), p]))

  return details
    .filter(Boolean)
    .map(d => {
      const m = id2meta.get(Number(d.id)) || {}
      return { ...d, probability: m.probability ?? null, confidence: m.confidence ?? null }
    })
}

export default {
  searchDiseases,
  getDiseaseById,
  expandPredictionsToDiseases,
}
