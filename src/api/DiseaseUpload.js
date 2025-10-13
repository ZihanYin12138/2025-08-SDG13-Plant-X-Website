// src/api/DiseaseUpload.js

const UPLOAD_D_URL = 'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx/upload-D';
const DISEASE_QUERY_URL = 'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx/disease-query';

async function parseJsonSafely(res) {
  const text = await res.text();
  try { return JSON.parse(text); } catch { return { message: text }; }
}

/** Extract "Disease ID" uniformly, compatible with different field names */
function pickDiseaseId(obj = {}) {
  const raw =
    obj.plant_disease_id ??
    obj.disease_id ??
    obj.predicted_id ??
    obj.id ??
    obj?.disease?.id ??
    obj?.prediction?.id;

  const n = Number(raw);
  return Number.isFinite(n) ? n : null;
}

/** Unified extraction of "score/probability" */
function pickScore(obj = {}) {
  const raw =
    obj.score ??
    obj.probability ??
    obj.confidence ??
    obj?.metrics?.score ??
    obj?.prob ??
    obj?.p;
  const n = Number(raw);
  return Number.isFinite(n) ? n : null;
}

/**Upload disease pictures*/
export async function uploadDiseaseImage(file) {
  const fd = new FormData();
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

/**Use S3 Key to enable the backend to perform disease identification*/
export async function predictDiseaseByS3Key(s3Key, count = 8) {
  const u = new URL(DISEASE_QUERY_URL);
  u.searchParams.set('s3_key', s3Key);
  u.searchParams.set('count', String(count));

  const res = await fetch(u.toString(), { method: 'GET', mode: 'cors' });
  const data = await parseJsonSafely(res);

  // Treat "no match" responses as empty results
  const msg = (data?.message || data?.error || '').toString();
  if (!res.ok) {
    if (res.status === 404 || res.status === 422 || /no matching/i.test(msg)) {
      return { results: [], total: 0 };
    }
    throw new Error(`HTTP ${res.status}: ${msg || 'Unknown error'}`);
  }

  const rawList =
    (Array.isArray(data?.results) && data.results) ||
    (Array.isArray(data?.items) && data.items) ||
    (Array.isArray(data?.predictions) && data.predictions) ||
    [];

  const results = rawList
    .map(r => {
      const id = pickDiseaseId(r);
      if (id == null) return null;
      return { disease_id: id, score: pickScore(r) };
    })
    .filter(Boolean);

  const total = typeof data?.total === 'number' ? data.total : undefined;
  return { results, total };
}

export default {
  uploadDiseaseImage,
  predictDiseaseByS3Key,
};
