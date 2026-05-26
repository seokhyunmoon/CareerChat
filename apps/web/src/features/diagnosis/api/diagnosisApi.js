import { apiRequest } from '@/services/apiClient';

export function createDiagnosis(request) {
  return apiRequest('/diagnoses', {
    method: 'POST',
    body: request,
  });
}
