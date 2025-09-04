// src/api/plants.ts
import { apiGet } from './http'

/** ===== 类型定义（列表项） ===== */
export type Plant = {
  general_plant_id: number
  common_name: string
  scientific_name: string
  other_name?: string[] | string
  image_url: string
}

export type PlantListResp = {
  items: Plant[]
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

  if_threatened?: boolean
  if_edible?: boolean
  if_indoors?: boolean
  if_medicinal?: boolean
  if_poisonous?: boolean
  if_fruits?: boolean
  if_flowers?: boolean

  sun_expose?: string | string[]
  watering?: string
  plant_cycle?: string
  growth_rate?: string

  description?: any
  care_guide?: any
  distribution_map?: any
  image_urls?: string[]
  threatened?: {
    description?: any
    care_guide?: any
  }
}

/** ===== API 基础路径 ===== */
const BASE_URL =
  'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx/plants'

/** 
 * yes/no/all → boolean | undefined
 */
export function ynToBool(v?: string): boolean | undefined {
  if (v === 'yes') return true
  if (v === 'no') return false
  return undefined
}

/**
 * 模糊搜索 + 11 个筛选参数
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
    rare?: string
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

  if (page !== undefined) qs.page = page
  if (page_size !== undefined) qs.page_size = page_size

  if (filters) {
    const {
      threatened,
      edible,
      medicinal,
      fruits,
      indoors,
      rare,
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
      if_rare: ynToBool(rare),
      if_flowers: ynToBool(flowers),
      sun_expose: Array.isArray(sun)
        ? sun.filter(Boolean).join(',')
        : sun || undefined,
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

/** ✅ 用 ?general_plant_id= 查询详情 */
export function getPlantById(id: number) {
  return apiGet<PlantDetail>(BASE_URL, { general_plant_id: id })
}
