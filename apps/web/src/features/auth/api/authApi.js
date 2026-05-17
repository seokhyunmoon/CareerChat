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

export function signup({ name, email, password }) {
  return apiRequest('/auth/signup', {
    method: 'POST',
    auth: false,
    body: {
      name,
      email,
      password,
    },
  });
}
