import { apiRequest } from '@/services/apiClient';

export function getProfile() {
  return apiRequest('/profile');
}

export function saveProfile(profile) {
  return apiRequest('/profile', {
    method: 'PUT',
    body: profile,
  });
}
