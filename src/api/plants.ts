// src/api/plants.ts
import { apiGet } from './http'

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

/**
 * 模糊搜索 + 11 个筛选参数
 * 注意：UI 里如果没有某个字段（例如 rare），就不要传
 */
export function searchPlants(params: {
  search?: string
  page?: number
  page_size?: number
  filters?: {
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
}) {
  const { search, page, page_size, filters } = params || {}

  const qs: Record<string, any> = {}
  qs.q = search && search.trim() ? search.trim() : 'a'

  if (page_size !== undefined) qs.limit = page_size
  if (page !== undefined && page_size !== undefined) qs.offset = Math.max(0, (page - 1) * page_size)

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
      sun_expose: Array.isArray(sun) ? sun.filter(Boolean).join(',') : sun || undefined,
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

/** 详情：普通植物 */
export function getPlantById(id: number) {
  return apiGet<PlantDetail>(BASE_URL, { general_plant_id: id })
}

/** 详情：濒危植物 */
export function getThreatenedById(id: number) {
  return apiGet<PlantDetail>(BASE_URL, { threatened_plant_id: id })
}

/** 用于卡片的简化类型（修复：原来引用了未定义的 Plant 类型） */
export type PlantCardSimple = {
  general_plant_id: number
  common_name: string
  scientific_name: string
  image_url: string
}

export async function getPlantsForCardsByIds(ids: number[]): Promise<PlantCardSimple[]> {
  const uniq = Array.from(new Set(ids)).slice(0, 12)
  const details = await Promise.all(uniq.map(id => getPlantById(id)))
  return details.map(d => {
    const cover = Array.isArray(d.image_urls) && d.image_urls.length ? d.image_urls[0] : ''
    return {
      general_plant_id: d.general_plant_id,
      common_name: d.common_name,
      scientific_name: d.scientific_name,
      image_url: cover,
    }
  })
}
