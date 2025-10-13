// src/api/plants.ts
import { apiGet } from './http'

/** ===== Generic Plant type ===== */
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

/** ===== List item (union type) ===== */
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

/** ===== Detail type ===== */
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

/** ===== API ===== */
const BASE_URL =
  'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx/plants'


export function ynToBool(v?: string): boolean | undefined {
  if (v === 'yes') return true
  if (v === 'no') return false
  return undefined
}

/** ===== Search parameter type (exported for external reuse) ===== */
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

export function searchPlants(): Promise<PlantListResp>
export function searchPlants(search: string): Promise<PlantListResp>
export function searchPlants(params: SearchPlantsParams): Promise<PlantListResp>

/** Single implementation */
export function searchPlants(arg?: string | SearchPlantsParams): Promise<PlantListResp> {
  const params: SearchPlantsParams =
    typeof arg === 'string' ? { search: arg } : (arg ?? {})

  const { search, page, page_size, filters } = params

  const qs: Record<string, any> = {}
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

/** ===== Details: Common Plants ===== */
export function getPlantById(id: number) {
  return apiGet<PlantDetail>(BASE_URL, { general_plant_id: id })
}

/** ===== Details: Endangered Plants ===== */
export function getThreatenedById(id: number) {
  return apiGet<PlantDetail>(BASE_URL, { threatened_plant_id: id })
}

/** ===== Parsing "ID Query" tool =====*/
export function parseIdQuery(raw: string): { kind: 'none' | 'general' | 'threatened', ids: number[] } {
  const q = (raw || '').trim()
  if (!q) return { kind: 'none', ids: [] }

  const tMatch = q.match(/^(?:t#|t:\s*|threat(?:ened)?\s*:\s*)(.+)$/i)
  if (tMatch) return { kind: 'threatened', ids: splitIds(tMatch[1]) }

  const gMatch = q.match(/^(?:#|ids:\s*)(.+)$/i)
  if (gMatch) return { kind: 'general', ids: splitIds(gMatch[1]) }

  return { kind: 'none', ids: [] }
}

/** Split multiple IDs, remove duplicates and filter illegal values ​​*/
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

/** ===== Card simplified type and batch acquisition (general) ===== */
export type PlantCardSimple = {
  general_plant_id: number
  common_name: string
  scientific_name: string
  image_url: string
}

/** Pull cards in batches by general_plant_id to display the minimum information required */
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

/** ===== Pull cards in batches by threatened_plant_id ===== */
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

/** ===== Pull in batches by type ===== */
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
