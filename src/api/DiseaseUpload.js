// src/api/DiseaseUpload.js

const UPLOAD_D_URL = 'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx/upload-D';
const DISEASE_QUERY_URL = 'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx/disease-query';

async function parseJsonSafely(res) {
  const text = await res.text();
  try { return JSON.parse(text); } catch { return { message: text }; }
}

/**
 * 上传疾病图片
 * 返回 { key, url? }
 */
export async function uploadDiseaseImage(file) {
  const fd = new FormData();
  // 若你后端字段名是 "image"，把下一行改成 'image'
  fd.append('file', file);

  const res = await fetch(UPLOAD_D_URL, { method: 'POST', body: fd, mode: 'cors' });
  const data = await parseJsonSafely(res);
  if (!res.ok) {
    const msg = data?.message || data?.error || JSON.stringify(data);
    throw new Error(`HTTP ${res.status}: ${msg}`);
  }
  const key = data?.key ?? data?.s3_key ?? data?.path;
  if (!key) throw new Error('Upload succeeded but no "key" returned.');
  return { key, url: data?.url };
}

/**
 * 用 S3 Key 让后端做疾病识别
 * 返回 { results: [{ disease_id:number, score?:number }], total?: number }
 * —— “无匹配”时返回空数组而不是抛错
 */
export async function predictDiseaseByS3Key(s3Key, count = 8) {
  const u = new URL(DISEASE_QUERY_URL);
  u.searchParams.set('s3_key', s3Key);
  u.searchParams.set('count', String(count));

  const res = await fetch(u.toString(), { method: 'GET', mode: 'cors' });
  const data = await parseJsonSafely(res);

  // 将“无匹配”的响应当作空结果处理（常见是 404/422，或文案包含 no matching）
  const msg = (data?.message || data?.error || '').toString();
  if (!res.ok) {
    if (res.status === 404 || res.status === 422 || /no matching/i.test(msg)) {
      return { results: [], total: 0 };
    }
    throw new Error(`HTTP ${res.status}: ${msg || 'Unknown error'}`);
  }

  const results = Array.isArray(data?.results) ? data.results : [];
  const total = typeof data?.total === 'number' ? data.total : undefined;
  return { results, total };
}

export default {
  uploadDiseaseImage,
  predictDiseaseByS3Key,
};
