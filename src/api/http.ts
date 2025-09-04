// src/api/http.ts

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:3000'

function tryUnwrapLambdaProxy<T>(data: any): T {
  // 非 proxy 格式，直接返回
  if (!data || typeof data !== 'object' || !('body' in data)) return data as T

  // proxy: body 可能是 string（json 或 base64），也可能已是对象
  const body = (data as any).body

  if (typeof body === 'string') {
    // 兼容 base64
    if (data.isBase64Encoded) {
      try {
        const jsonStr = atob(body)
        return JSON.parse(jsonStr) as T
      } catch {
        // 不是 json，就返回原始字符串
        return body as unknown as T
      }
    }
    // 非 base64，按 json 解析
    try {
      return JSON.parse(body) as T
    } catch {
      return body as unknown as T
    }
  }

  // body 已是对象
  return body as T
}

async function parseJSONSafe<T>(res: Response): Promise<T> {
  // 某些 204/空 body 会抛错，这里兜底
  const text = await res.text()
  if (!text) return undefined as unknown as T
  try {
    return JSON.parse(text) as T
  } catch {
    // 返回非 JSON 文本（极少见）
    return text as unknown as T
  }
}

/** GET */
export async function apiGet<T>(
  path: string,
  params?: Record<string, any>,
  signal?: AbortSignal
): Promise<T> {
  // 支持相对路径 + 绝对路径
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


