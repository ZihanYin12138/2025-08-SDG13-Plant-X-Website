// src/api/uploads.ts

/** ========= API ========= */
export const API_ROOT =
  import.meta.env.VITE_API_ROOT ??
  'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx';

/** Allowed image types & maximum sizes */
const ALLOWED_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp', 'image/gif']);
const MAX_BYTES = 10 * 1024 * 1024;

/** ========= type ========= */
export interface UploadResp {
  bucket: string;
  key: string;
  contentType: string;
  size: number;
  s3Uri: string;
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

/** ========= tool ========= */
function assertImageValid(file: File) {
  if (!ALLOWED_TYPES.has(file.type)) {
    const list = Array.from(ALLOWED_TYPES).map(t => t.split('/')[1]).join(', ');
    throw new Error(`仅支持上传图片类型：${list}`);
  }
  if (file.size > MAX_BYTES) {
    throw new Error(`图片过大（${(file.size / (1024 * 1024)).toFixed(2)}MB），最大 10MB`);
  }
}

/** Convert backend error responses (JSON or plain text) to Error for UI display */
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

/** Upload image */
export async function uploadImage(
  file: File,
  opts?: { signal?: AbortSignal }
): Promise<UploadResp> {
  assertImageValid(file);

  const url = `${API_ROOT}/upload?filename=${encodeURIComponent(file.name)}`;
  const fd = new FormData();
  fd.append('file', file, file.name);

  const res = await fetch(url, { method: 'POST', body: fd, signal: opts?.signal });
  if (!res.ok) return toNiceError(res);
  return res.json() as Promise<UploadResp>;
}

/**
* Prediction: Identify plants based on an S3 key
* @param s3Key (e.g., uploads/2025/09/04/xxx.png)
* @param count (number of candidates to return) (default 8)
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
* Combination: upload and predict (one-step)
* Returns { upload, predict }, the upload response and the predicted response, respectively
*/
export async function uploadAndPredict(
  file: File,
  opts?: { count?: number; signal?: AbortSignal }
): Promise<{ upload: UploadResp; predict: PredictResp }> {
  const upload = await uploadImage(file, { signal: opts?.signal });
  const predict = await predictByS3Key(upload.key, opts?.count ?? 8, { signal: opts?.signal });
  return { upload, predict };
}
