import { apiRequest } from '@/services/apiClient';

export function login({ email, password }) {
  return apiRequest('/auth/login', {
    method: 'POST',
    auth: false,
    body: {
      email,
      password,
    },
  });
}

export function getMe() {
  return apiRequest('/auth/me');
}
