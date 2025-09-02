// src/api/plants.ts
import { apiGet } from './http'

export type Plant = {
  id: number
  common_name: string
  scientific_name: string
  other_name: string[] | string
  image_url: string
}

export type PlantListResp = {
  items: Plant[]
  page: number
  page_size: number
  total: number
}

// 过滤条件：和表结构一一对应
export type PlantFilters = {
  if_threatened?: boolean
  if_edible?: boolean
  if_indoors?: boolean
  if_medicinal?: boolean
  if_poisonous?: boolean
  if_fruits?: boolean
  if_flowers?: boolean
  sun_expose?: string[]        // 多选：'low','medium','high'... 由你后端定义
  watering?: string            // 'low' | 'average' | 'frequent' ...
  plant_cycle?: string         // 'annual' | 'perennial' ...
  growth_rate?: string         // 'slow' | 'medium' | 'fast'
}

export function fetchPlants(params: {
  search?: string
  page?: number
  page_size?: number
  // 新增 filters
  filters?: PlantFilters
}) {
  const { filters, ...rest } = params || {}
  const flat: Record<string, any> = { ...rest }

  // 把 filters 扁平化到 querystring
  if (filters) {
    Object.entries(filters).forEach(([k, v]) => {
      if (v === undefined || v === null || v === '') return
      if (Array.isArray(v)) {
        if (v.length) flat[k] = v.join(',') // sun_expose=low,high
      } else {
        flat[k] = v
      }
    })
  }
  return apiGet<PlantListResp>('/plants', flat)
}

