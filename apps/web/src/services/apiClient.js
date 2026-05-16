import { getAccessToken } from '@/features/auth/tokenStorage';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

export class ApiError extends Error {
  constructor({ status, code, message, errors }) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.errors = errors;
  }
}

export async function apiRequest(path, options = {}) {
  const { method = 'GET', body, headers = {}, auth = true } = options;
  const accessToken = auth ? getAccessToken() : null;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await parseJson(response);

  if (!response.ok) {
    throw new ApiError({
      status: response.status,
      code: data?.code ?? 'UNKNOWN_ERROR',
      message: data?.message ?? 'Request failed.',
      errors: data?.errors,
    });
  }

  return data?.data;
}

async function parseJson(response) {
  const text = await response.text();

  if (!text) {
    return null;
  }

  return JSON.parse(text);
}
