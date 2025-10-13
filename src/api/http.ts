// src/api/http.ts

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:3000'

function tryUnwrapLambdaProxy<T>(data: any): T {
  if (!data || typeof data !== 'object' || !('body' in data)) return data as T

  const body = (data as any).body

  if (typeof body === 'string') {
    // Base64 compatible
    if (data.isBase64Encoded) {
      try {
        const jsonStr = atob(body)
        return JSON.parse(jsonStr) as T
      } catch {
        // If it is not json, return the original string
        return body as unknown as T
      }
    }
    // Not base64, parsed as json
    try {
      return JSON.parse(body) as T
    } catch {
      return body as unknown as T
    }
  }
  return body as T
}

async function parseJSONSafe<T>(res: Response): Promise<T> {
  const text = await res.text()
  if (!text) return undefined as unknown as T
  try {
    return JSON.parse(text) as T
  } catch {
    return text as unknown as T
  }
}

/** GET */
export async function apiGet<T>(
  path: string,
  params?: Record<string, any>,
  signal?: AbortSignal
): Promise<T> {
  const url = new URL(path, API_BASE)

  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        url.searchParams.set(k, String(v))
      }
    })
  }

  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { Accept: 'application/json' },
    signal,
  })

  if (!res.ok) throw new Error(`HTTP ${res.status}`)

  const raw = await parseJSONSafe<any>(res)
  return tryUnwrapLambdaProxy<T>(raw)
}

/** POST */
export async function apiPost<T>(
  path: string,
  body: any,
  signal?: AbortSignal
): Promise<T> {
  const url = new URL(path, API_BASE)

  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
    signal,
  })

  if (!res.ok) throw new Error(`HTTP ${res.status}`)

  const raw = await parseJSONSafe<any>(res)
  return tryUnwrapLambdaProxy<T>(raw)
}


