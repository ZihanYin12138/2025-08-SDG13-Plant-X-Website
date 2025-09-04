// src/api/uploads.ts

/** ========= 配置 ========= */
export const API_ROOT =
  import.meta.env.VITE_API_ROOT ??
  'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx';

/** 允许的图片类型 & 最大大小（与后端保持一致） */
const ALLOWED_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp', 'image/gif']);
const MAX_BYTES = 10 * 1024 * 1024; // 10MB

/** ========= 类型 ========= */
export interface UploadResp {
  bucket: string;
  key: string;          // S3 对象键：如 uploads/2025/09/04/xxxx.png
  contentType: string;
  size: number;
  s3Uri: string;        // s3://bucket/key
}

export interface PredictItem {
  plant_id: number;
  score: number;
}

export interface PredictResp {
  s3_key: string;
  count: number;
  results: PredictItem[];
}

/** ========= 工具 ========= */
function assertImageValid(file: File) {
  if (!ALLOWED_TYPES.has(file.type)) {
    const list = Array.from(ALLOWED_TYPES).map(t => t.split('/')[1]).join(', ');
    throw new Error(`仅支持上传图片类型：${list}`);
  }
  if (file.size > MAX_BYTES) {
    throw new Error(`图片过大（${(file.size / (1024 * 1024)).toFixed(2)}MB），最大 10MB`);
  }
}

/** 将后端错误响应（JSON 或纯文本）转成 Error，便于 UI 展示 */
async function toNiceError(res: Response): Promise<never> {
  let msg = `HTTP ${res.status}`;
  try {
    const data = await res.json();
    if (data?.message) msg = `${msg} - ${data.message}`;
  } catch {
    try {
      msg = `${msg} - ${await res.text()}`;
    } catch { /* ignore */ }
  }
  throw new Error(msg);
}

/** ========= API ========= */

/**
 * 上传图片（multipart/form-data，不要手动设置 Content-Type）
 * 成功返回后端给出的 S3 信息（包含 key）
 */
export async function uploadImage(
  file: File,
  opts?: { signal?: AbortSignal }
): Promise<UploadResp> {
  assertImageValid(file);

  const url = `${API_ROOT}/upload?filename=${encodeURIComponent(file.name)}`;
  const fd = new FormData();
  // 字段名随意，后端会取第一个带 filename 的 part
  fd.append('file', file, file.name);

  const res = await fetch(url, { method: 'POST', body: fd, signal: opts?.signal });
  if (!res.ok) return toNiceError(res);
  return res.json() as Promise<UploadResp>;
}

/**
 * 预测：根据 S3 key 识别植物
 * @param s3Key 形如 uploads/2025/09/04/xxx.png
 * @param count 返回候选数量（默认 8）
 */
export async function predictByS3Key(
  s3Key: string,
  count = 8,
  opts?: { signal?: AbortSignal }
): Promise<PredictResp> {
  const url = `${API_ROOT}/predict?s3_key=${encodeURIComponent(s3Key)}&count=${count}`;
  const res = await fetch(url, { signal: opts?.signal });
  if (!res.ok) return toNiceError(res);
  return res.json() as Promise<PredictResp>;
}

/**
 * 组合：上传并预测（一步到位）
 * 返回 { upload, predict }，分别是上传响应与预测响应
 */
export async function uploadAndPredict(
  file: File,
  opts?: { count?: number; signal?: AbortSignal }
): Promise<{ upload: UploadResp; predict: PredictResp }> {
  const upload = await uploadImage(file, { signal: opts?.signal });
  const predict = await predictByS3Key(upload.key, opts?.count ?? 8, { signal: opts?.signal });
  return { upload, predict };
}
