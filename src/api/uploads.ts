import { apiGet } from './http'

export type PresignResp = { putUrl: string; key: string }

export function presignUpload(params: { filename: string; contentType: string }) {
  return apiGet<PresignResp>('/uploads/presign', params)
}
