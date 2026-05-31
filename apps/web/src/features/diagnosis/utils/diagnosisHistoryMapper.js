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
  const jobCount = Math.max(companies.filter(Boolean).length, Number(diagnosis.jobCount) || 0);
  const status = diagnosis.status ?? 'PENDING';
  const failure = toDiagnosisFailureViewModel(diagnosis.errorCode);

  return {
    diagnosisId: diagnosis.diagnosisId,
    status,
    statusLabel: diagnosisStatusLabels[status] ?? status,
    statusClass: String(status).toLowerCase(),
    dateParts,
    createdAtLabel: formatDateTime(diagnosis.createdAt),
    titleText: companiesText || diagnosis.topCompanyName || '회사 정보 없음',
    companiesText: companiesText || diagnosis.topCompanyName || '회사 정보 없음',
    jobsSummary:
      getJobsSummaryText(diagnosis, jobCount),
    scoreText: getScoreText(diagnosis),
    scoreLabel: getScoreLabel(status),
    summaryText: getSummaryText(diagnosis, status, failure),
    actionLabel: status === 'COMPLETED' ? '결과 보기' : '상태 확인',
    errorMessage: status === 'FAILED' ? failure.title : null,
  };
}

function getJobsSummaryText(diagnosis, jobCount) {
  if (jobCount > 1 && diagnosis.topPosition) {
    return `${diagnosis.topPosition} 외 ${jobCount - 1}개`;
  }

  return diagnosis.jobsSummary || diagnosis.topPosition || '공고 정보 없음';
}

function getSummaryText(diagnosis, status, failure) {
  if (status === 'COMPLETED') {
    const score = getScoreText(diagnosis);
    return score === '-' ? '분석이 완료되었습니다.' : `최고 적합도 ${score}`;
  }

  if (status === 'FAILED') {
    return failure.title;
  }

  if (status === 'PROCESSING') {
    return 'AI 분석이 진행 중입니다.';
  }

  return '진단 요청이 접수되었습니다.';
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
    monthYear: `${getEnglishMonth(date)} '${String(date.getFullYear()).slice(2)}`,
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

function getEnglishMonth(date) {
  return ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'][date.getMonth()];
}
