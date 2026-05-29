const DEFAULT_FAILURE_MESSAGE = {
  title: '분석을 완료하지 못했습니다.',
  description: '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.',
  nextAction: '같은 공고로 다시 시도하거나 진단 기록에서 상태를 확인해 주세요.',
};

const FAILURE_MESSAGES_BY_CODE = {
  AI_JOB_ENQUEUE_FAILED: {
    title: '분석 작업을 시작하지 못했습니다.',
    description: '분석 요청을 처리하는 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.',
    nextAction: '프로필과 공고 입력 내용을 확인한 뒤 새 진단을 시작해 주세요.',
  },
  PROFILE_SNAPSHOT_INVALID: {
    title: '내 정보가 부족해 분석을 진행하지 못했습니다.',
    description: '프로필의 경력, 기술, 프로젝트 정보가 충분히 저장되어 있는지 확인해 주세요.',
    nextAction: '내 정보를 보완한 뒤 같은 공고로 다시 진단해 주세요.',
  },
  INVALID_INPUT: {
    title: '입력 내용을 확인해 주세요.',
    description: '공고 회사명, 포지션, 공고 원문이 충분히 입력되었는지 확인해 주세요.',
    nextAction: '입력값을 보완한 뒤 다시 진단을 시작해 주세요.',
  },
  JOB_POSTING_INVALID: {
    title: '공고 내용을 확인해 주세요.',
    description: '분석할 수 있는 공고 정보가 부족합니다. 공고 원문을 다시 확인해 주세요.',
    nextAction: '회사명, 포지션, 공고 원문을 보완한 뒤 다시 진단해 주세요.',
  },
  EMBEDDING_ERROR: {
    title: '분석 자료를 준비하지 못했습니다.',
    description: '내 정보와 공고 내용을 분석 자료로 변환하는 중 문제가 발생했습니다.',
    nextAction: '잠시 후 같은 공고로 다시 진단해 주세요.',
  },
  QDRANT_ERROR: {
    title: '분석 자료를 준비하지 못했습니다.',
    description: '저장된 내 정보를 불러와 분석 자료로 준비하는 중 문제가 발생했습니다.',
    nextAction: '잠시 후 같은 공고로 다시 진단해 주세요.',
  },
  AI_TIMEOUT: {
    title: '분석 시간이 초과되었습니다.',
    description: '요청 처리 시간이 길어져 분석을 완료하지 못했습니다.',
    nextAction: '잠시 후 다시 시도하거나 공고 원문을 조금 줄여 다시 진단해 주세요.',
  },
  LLM_TIMEOUT: {
    title: 'AI 분석 시간이 초과되었습니다.',
    description: 'AI 응답을 기다리는 중 시간이 초과되었습니다.',
    nextAction: '잠시 후 다시 시도하거나 공고 원문을 조금 줄여 다시 진단해 주세요.',
  },
  LLM_PROVIDER_ERROR: {
    title: 'AI 분석 중 문제가 발생했습니다.',
    description: 'AI 분석 응답을 생성하는 중 일시적인 문제가 발생했습니다.',
    nextAction: '잠시 후 같은 공고로 다시 진단해 주세요.',
  },
  INVALID_AI_RESPONSE: {
    title: 'AI 분석 결과를 정리하지 못했습니다.',
    description: '분석 응답을 결과 화면에 맞게 정리하는 중 문제가 발생했습니다.',
    nextAction: '잠시 후 같은 공고로 다시 진단해 주세요.',
  },
  CALLBACK_FAILED: {
    title: '분석 결과 저장 중 문제가 발생했습니다.',
    description: '분석은 처리되었지만 결과를 저장하는 중 문제가 발생했습니다.',
    nextAction: '잠시 후 진단 기록에서 다시 확인하거나 새 진단을 시작해 주세요.',
  },
  UNEXPECTED_ERROR: DEFAULT_FAILURE_MESSAGE,
};

export function toDiagnosisFailureViewModel(errorCode) {
  const normalizedCode = normalizeErrorCode(errorCode);

  return {
    code: normalizedCode ?? 'UNKNOWN_ERROR',
    ...DEFAULT_FAILURE_MESSAGE,
    ...(FAILURE_MESSAGES_BY_CODE[normalizedCode] ?? {}),
  };
}

function normalizeErrorCode(errorCode) {
  if (typeof errorCode !== 'string' || !errorCode.trim()) {
    return null;
  }

  return errorCode.trim().toUpperCase();
}
