// src/api/plants.ts
import { apiGet } from './http'

/** ===== 通用 Plant 类型（你的现有定义保留） ===== */
export interface Plant {
  general_plant_id: string
  commonName: string
  scientificName: string
  family?: string
  light: 'full-sun' | 'part-sun' | 'shade'
  waterNeed: 'low' | 'medium' | 'high'
  tempMinC?: number
  tempMaxC?: number
  soil?: Array<'sand' | 'loam' | 'clay' | 'acidic' | 'alkaline'>
  images?: string[]
}

/** ===== 列表项（联合类型） ===== */
export type PlantGeneralCard = {
  id_type: 'general'
  general_plant_id: number
  common_name: string
  scientific_name: string
  image_url: string | null
}

export type PlantThreatCard = {
  id_type: 'threatened'
  threatened_plant_id: number
  common_name: string
  scientific_name: string
  image_url: string | null
}

export type PlantCardItem = PlantGeneralCard | PlantThreatCard

export type PlantListResp = {
  items: PlantCardItem[]
  total?: number
  limit?: number
  offset?: number
}

/** ===== 详情类型 ===== */
export type PlantDetail = {
  plant_id: number
  general_plant_id: number
  threatened_plant_id?: number | null

  common_name: string
  scientific_name: string
  other_name?: string[] | string

  if_threatened?: boolean | string
  if_edible?: boolean | string
  if_indoors?: boolean | string
  if_medicinal?: boolean | string
  if_poisonous?: boolean | string
  if_fruits?: boolean | string
  if_flowers?: boolean | string

  sun_expose?: string[] | string
  watering?: string
  plant_cycle?: string
  growth_rate?: string

  description?: any

  care_guide?: {
    general_plant_id?: number
    watering?: string
    watering_general_benchmark?: string
    sunlight?: string[]
    soil?: string[]
    pruning_month?: string[]
    pruning_count?: string
    growth_rate?: string
    care_level?: string
    watering_guide?: string
    sunlight_guide?: string
    pruning_guide?: string
  }
  distribution_map?: {
    distribution_map_html?: string
  }
  image_urls?: string[]
  threatened?: {
    description?: any
    care_guide?: any
  }
}

/** ===== API 基础路径 ===== */
const BASE_URL =
  'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx/plants'

/** yes/no/all → boolean | undefined */
export function ynToBool(v?: string): boolean | undefined {
  if (v === 'yes') return true
  if (v === 'no') return false
  return undefined
}

/** ===== 搜索参数类型（导出便于外部复用） ===== */
export type SearchPlantsFilters = {
  threatened?: string
  edible?: string
  medicinal?: string
  fruits?: string
  indoors?: string
  poisonous?: string
  flowers?: string
  sun?: string | string[]
  watering?: string
  cycle?: string
  growth?: string
}

export type SearchPlantsParams = {
  search?: string
  page?: number
  page_size?: number
  filters?: SearchPlantsFilters
}

/** ===== 搜索：支持 () / ('xxx') / ({ ... }) 三种用法 ===== */
// 重载声明（必须在实现前）
export function searchPlants(): Promise<PlantListResp>
export function searchPlants(search: string): Promise<PlantListResp>
export function searchPlants(params: SearchPlantsParams): Promise<PlantListResp>

/** 单个实现 */
export function searchPlants(arg?: string | SearchPlantsParams): Promise<PlantListResp> {
  // 兼容字符串 / 对象 / 未传参数
  const params: SearchPlantsParams =
    typeof arg === 'string' ? { search: arg } : (arg ?? {})

  const { search, page, page_size, filters } = params

  const qs: Record<string, any> = {}
  // 后端要求空搜索也传点内容，这里默认 'a'
  qs.q = search && search.trim() ? search.trim() : 'a'

  if (page_size != null) qs.limit = page_size
  if (page != null && page_size != null) {
    qs.offset = Math.max(0, (page - 1) * page_size)
  }

  if (filters) {
    const {
      threatened,
      edible,
      medicinal,
      fruits,
      indoors,
      poisonous,
      flowers,
      sun,
      watering,
      cycle,
      growth,
    } = filters

    const mapped: Record<string, any> = {
      if_threatened: ynToBool(threatened),
      if_edible: ynToBool(edible),
      if_medicinal: ynToBool(medicinal),
      if_fruits: ynToBool(fruits),
      if_indoors: ynToBool(indoors),
      if_poisonous: ynToBool(poisonous),
      if_flowers: ynToBool(flowers),
      sun_expose: Array.isArray(sun) ? sun.filter(Boolean).join(',') : (sun || undefined),
      watering: watering || undefined,
      plant_cycle: cycle || undefined,
      growth_rate: growth || undefined,
    }

    for (const [k, v] of Object.entries(mapped)) {
      if (v !== undefined && v !== null && v !== '') {
        qs[k] = v
      }
    }
  }

  return apiGet<PlantListResp>(BASE_URL, qs)
}

/** ===== 详情：普通植物 ===== */
export function getPlantById(id: number) {
  return apiGet<PlantDetail>(BASE_URL, { general_plant_id: id })
}

/** ===== 详情：濒危植物 ===== */
export function getThreatenedById(id: number) {
  return apiGet<PlantDetail>(BASE_URL, { threatened_plant_id: id })
}

/** ===== 解析“ID 查询”工具（可选导出，供页面复用） =====
 * 支持：
 *   - "#1,2,3"   => general
 *   - "ids:1,2"  => general
 *   - "t#4,5"    => threatened
 *   - "threat:6" => threatened
 */
export function parseIdQuery(raw: string): { kind: 'none' | 'general' | 'threatened', ids: number[] } {
  const q = (raw || '').trim()
  if (!q) return { kind: 'none', ids: [] }

  const tMatch = q.match(/^(?:t#|t:\s*|threat(?:ened)?\s*:\s*)(.+)$/i)
  if (tMatch) return { kind: 'threatened', ids: splitIds(tMatch[1]) }

  const gMatch = q.match(/^(?:#|ids:\s*)(.+)$/i)
  if (gMatch) return { kind: 'general', ids: splitIds(gMatch[1]) }

  return { kind: 'none', ids: [] }
}

/** 拆分多个 ID，去重并过滤非法值 */
export function splitIds(s: string): number[] {
  return Array.from(
    new Set(
      (s || '')
        .split(/[\s,，;；]+/)
        .map(x => parseInt(x, 10))
        .filter(n => Number.isFinite(n) && n > 0)
    )
  )
}

/** ===== 卡片简化类型与批量获取（general） ===== */
export type PlantCardSimple = {
  general_plant_id: number
  common_name: string
  scientific_name: string
  image_url: string
}

/** 批量按 general_plant_id 拉取卡片展示所需最小信息 */
export async function getPlantsForCardsByIds(ids: number[]): Promise<PlantCardSimple[]> {
  const uniq = Array.from(new Set(ids)).slice(0, 12)
  const details = await Promise.all(uniq.map(id => getPlantById(id).catch(() => null)))
  return details
    .filter((d): d is PlantDetail => !!d)
    .map(d => {
      const cover = Array.isArray(d.image_urls) && d.image_urls.length ? d.image_urls[1] : ''
      return {
        general_plant_id: d.general_plant_id,
        common_name: d.common_name,
        scientific_name: d.scientific_name,
        image_url: cover,
      }
    })
}

/** ===== （可选）批量按 threatened_plant_id 拉取卡片（与 PlantCardItem 兼容） ===== */
export async function getThreatenedCardsByIds(ids: number[]): Promise<PlantThreatCard[]> {
  const uniq = Array.from(new Set(ids)).slice(0, 12)
  const details = await Promise.all(uniq.map(id => getThreatenedById(id).catch(() => null)))
  return details
    .filter((d): d is PlantDetail => !!d)
    .map(d => ({
      id_type: 'threatened' as const,
      threatened_plant_id: (typeof d.threatened_plant_id === 'number' ? d.threatened_plant_id : d.plant_id)!,
      common_name: d.common_name,
      scientific_name: d.scientific_name,
      image_url: Array.isArray(d.image_urls) && d.image_urls.length ? d.image_urls[0] : null
    }))
}

/** ===== （可选）统一方法：按类型批量拉取，直接得到列表用的 PlantCardItem[] ===== */
export async function getCardsByIds(
  ids: number[],
  kind: 'general' | 'threatened' = 'general'
): Promise<PlantCardItem[]> {
  if (kind === 'general') {
    const simple = await getPlantsForCardsByIds(ids)
    return simple.map(s => ({
      id_type: 'general' as const,
      general_plant_id: s.general_plant_id,
      common_name: s.common_name,
      scientific_name: s.scientific_name,
      image_url: s.image_url || null
    }))
  } else {
    return getThreatenedCardsByIds(ids)
  }
}
