const API_BASE = import.meta.env.VITE_API_BASE || ''

export async function apiGet<T>(path: string, params?: Record<string, any>, signal?: AbortSignal): Promise<T> {
  const url = new URL(path, API_BASE)
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, String(v))
    })
  }
  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
    signal
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
