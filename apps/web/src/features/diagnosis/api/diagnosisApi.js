import { apiRequest } from '@/services/apiClient';

export function createDiagnosis(request) {
  return apiRequest('/diagnoses', {
    method: 'POST',
    body: request,
  });
}

export function getDiagnosis(diagnosisId) {
  return apiRequest(`/diagnoses/${diagnosisId}`);
}

export function getDiagnoses() {
  return apiRequest('/diagnoses');
}
