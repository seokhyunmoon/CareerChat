import { toDiagnosisFailureViewModel } from './diagnosisFailureMessages';

export const diagnosisStatusLabels = {
  PENDING: '접수됨',
  PROCESSING: '분석 중',
  COMPLETED: '완료',
  FAILED: '실패',
};

export function toDiagnosisHistoryItems(response) {
  return (response?.diagnoses ?? []).map(toDiagnosisHistoryItem);
}

export function toHistoryErrorViewModel(error) {
  if (error?.status === 401) {
    return {
      title: '로그인이 필요합니다.',
      description: '진단 기록은 로그인한 사용자만 확인할 수 있습니다.',
      actionLabel: '로그인하기',
      actionPath: '/login',
    };
  }

  return {
    title: '진단 기록을 불러오지 못했습니다.',
    description: '잠시 후 다시 시도하거나 새 진단을 시작해 주세요.',
    actionLabel: '새 진단 시작하기',
    actionPath: '/analyze',
  };
}

function toDiagnosisHistoryItem(diagnosis) {
  const dateParts = formatHistoryDateParts(diagnosis.createdAt);
  const companies = Array.isArray(diagnosis.companies) ? diagnosis.companies : [];
  const companiesText = companies.filter(Boolean).join(' · ');
  const status = diagnosis.status ?? 'PENDING';
  const failure = toDiagnosisFailureViewModel(diagnosis.errorCode);

  return {
    diagnosisId: diagnosis.diagnosisId,
    status,
    statusLabel: diagnosisStatusLabels[status] ?? status,
    statusClass: String(status).toLowerCase(),
    dateParts,
    createdAtLabel: formatDateTime(diagnosis.createdAt),
    companiesText:
      companiesText ||
      diagnosis.topCompanyName ||
      '회사 정보 없음',
    jobsSummary:
      diagnosis.jobsSummary ||
      diagnosis.topPosition ||
      '공고 정보 없음',
    scoreText: getScoreText(diagnosis),
    scoreLabel: getScoreLabel(status),
    errorMessage: status === 'FAILED' ? failure.title : null,
  };
}

function getScoreText(diagnosis) {
  if (diagnosis.status !== 'COMPLETED' || diagnosis.topFitScore === null || diagnosis.topFitScore === undefined) {
    return '-';
  }

  const score = Number(diagnosis.topFitScore);
  if (Number.isNaN(score)) {
    return '-';
  }

  return `${Math.round(score)}점`;
}

function getScoreLabel(status) {
  if (status === 'COMPLETED') {
    return '최고 적합도';
  }

  return '분석 상태';
}

function formatHistoryDateParts(value) {
  const date = parseDate(value);

  if (!date) {
    return {
      day: '--',
      month: '--',
    };
  }

  return {
    day: pad(date.getDate()),
    month: `${pad(date.getMonth() + 1)}월`,
  };
}

function formatDateTime(value) {
  const date = parseDate(value);

  if (!date) {
    return value ?? '-';
  }

  return [
    `${date.getFullYear()}.${pad(date.getMonth() + 1)}.${pad(date.getDate())}`,
    `${pad(date.getHours())}:${pad(date.getMinutes())}`,
  ].join(' ');
}

function parseDate(value) {
  if (!value) return null;

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return date;
}

function pad(number) {
  return String(number).padStart(2, '0');
}
