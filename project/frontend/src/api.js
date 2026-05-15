/**
 * API client for the Road Damage Detection backend.
 * All requests go to BASE_URL (configurable via REACT_APP_API_URL env var).
 */

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

async function handleResponse(res) {
  const data = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
  if (!res.ok) throw data;
  return data;
}

/** Health check */
export async function healthCheck() {
  const res = await fetch(`${BASE_URL}/health`);
  return handleResponse(res);
}

/** Get current model metadata */
export async function getModelInfo() {
  const res = await fetch(`${BASE_URL}/model/info`);
  return handleResponse(res);
}

/**
 * Run detection on an image file.
 * @param {File} imageFile
 * @param {number} confidence - 0.0 to 1.0
 */
export async function detectImage(imageFile, confidence = 0.5) {
  const form = new FormData();
  form.append('file', imageFile);

  const res = await fetch(
    `${BASE_URL}/detect?confidence=${confidence.toFixed(2)}`,
    { method: 'POST', body: form }
  );
  return handleResponse(res);
}
