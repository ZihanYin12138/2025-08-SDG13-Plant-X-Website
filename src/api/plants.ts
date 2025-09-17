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

// 单个实现
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

/** ===== 卡片简化类型与批量获取 ===== */
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
