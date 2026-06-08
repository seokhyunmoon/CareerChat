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

export function getDiagnosisChatMessages(diagnosisId) {
  return apiRequest(`/diagnoses/${diagnosisId}/chat/messages`);
}

export function createDiagnosisChatMessage(diagnosisId, content) {
  return apiRequest(`/diagnoses/${diagnosisId}/chat/messages`, {
    method: 'POST',
    body: { content },
  });
}
