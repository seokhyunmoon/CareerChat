export const POLLING_STATUSES = new Set(['PENDING', 'PROCESSING']);

const STATUS_LOADING_MESSAGES = {
  PENDING: '진단 요청을 접수했습니다. 곧 AI 분석을 시작합니다.',
  PROCESSING: '입력한 공고와 저장된 내 정보를 비교하고 있습니다.',
};

const MATCH_LEVEL_ALIASES = {
  HIGH: 'strong',
  MEDIUM: 'partial',
  LOW: 'weak',
  MISSING: 'none',
  NONE: 'none',
};

export function isPollingStatus(status) {
  return POLLING_STATUSES.has(status);
}

export function toDiagnosisViewModel(diagnosis) {
  const jobs = (diagnosis.jobs ?? []).map(toJobViewModel);
  const jobCount = jobs.length;

  return {
    ...diagnosis,
    createdAt: formatDateTime(diagnosis.createdAt),
    analysisStartedAt: formatDateTime(diagnosis.analysisStartedAt),
    completedAt: formatDateTime(diagnosis.completedAt),
    failedAt: formatDateTime(diagnosis.failedAt),
    jobs,
    companies: jobs.map((job) => job.companyName).filter(Boolean).join(' · '),
    jobsSummary: jobs.map((job) => job.position).filter(Boolean).join(' · '),
    meta: jobCount > 0 ? `공고 ${jobCount}개 비교` : '공고 정보 없음',
    loadingMessage:
      STATUS_LOADING_MESSAGES[diagnosis.status] ?? 'AI 분석 상태를 확인하고 있습니다.',
    errorMessage:
      diagnosis.errorMessage ??
      '일시적인 처리 지연으로 분석을 완료하지 못했습니다.',
    recoveryHint: getRecoveryHint(diagnosis.errorCode),
  };
}

export function toResultErrorViewModel(error) {
  if (error?.status === 401) {
    return {
      title: '로그인이 필요합니다.',
      description: '진단 결과는 로그인한 사용자만 확인할 수 있습니다.',
      actionLabel: '로그인하기',
      actionPath: '/login',
    };
  }

  if (error?.status === 403) {
    return {
      title: '이 진단 결과를 볼 수 없습니다.',
      description: '다른 계정에서 생성한 진단이거나 접근 권한이 없습니다.',
      actionLabel: '진단 기록으로',
      actionPath: '/history',
    };
  }

  if (error?.status === 404 || error?.code === 'RESOURCE_NOT_FOUND') {
    return {
      title: '진단 결과를 찾을 수 없습니다.',
      description: '진단이 삭제되었거나 잘못된 주소로 접근했습니다.',
      actionLabel: '진단 기록으로',
      actionPath: '/history',
    };
  }

  return {
    title: '진단 상태를 불러오지 못했습니다.',
    description: '잠시 후 다시 시도하거나 진단 기록에서 다시 열어 주세요.',
    actionLabel: '진단 기록으로',
    actionPath: '/history',
  };
}

function toJobViewModel(job) {
  const matchDetails = normalizeMatchDetails(job.matchDetails);
  const highlightPoints = parseListLikeValue(job.highlightPoints);

  return {
    ...job,
    rankOrder: job.rankOrder ?? job.displayOrder,
    fitScore: toScore(job.fitScore),
    highlightPoints: highlightPoints.join(', ') || job.highlightPoints,
    highlightCards: highlightPoints.map((point, index) => ({
      title: `강조 포인트 ${index + 1}`,
      body: point,
    })),
    requirementMatches: matchDetails,
  };
}

function normalizeMatchDetails(matchDetails) {
  const requirements = Array.isArray(matchDetails?.requirements)
    ? matchDetails.requirements
    : [];

  return requirements.map((requirement) => ({
    normalizedText:
      requirement.normalizedText ??
      requirement.name ??
      requirement.description ??
      '요구사항',
    importance: normalizeImportance(requirement.importance),
    matchLevel: normalizeMatchLevel(requirement.matchLevel ?? requirement.match),
    reason: requirement.reason ?? '분석 결과에 포함된 판단 근거입니다.',
    evidence: formatEvidence(requirement.evidence),
  }));
}

function normalizeImportance(importance) {
  if (!importance) return 'required';

  return String(importance).trim().toLowerCase();
}

function normalizeMatchLevel(matchLevel) {
  if (!matchLevel) return 'partial';

  const key = String(matchLevel).trim();
  return MATCH_LEVEL_ALIASES[key.toUpperCase()] ?? key.toLowerCase();
}

function formatEvidence(evidence) {
  if (Array.isArray(evidence)) {
    const evidenceText = evidence
      .map((item) => item?.text ?? item?.summary ?? item?.title ?? item)
      .filter(Boolean)
      .join(' / ');

    return evidenceText || '프로필 근거를 확인했습니다.';
  }

  if (typeof evidence === 'string' && evidence.trim()) {
    return evidence;
  }

  return '프로필 근거를 확인했습니다.';
}

function parseListLikeValue(value) {
  if (Array.isArray(value)) {
    return value.map(String).filter(Boolean);
  }

  if (typeof value !== 'string' || !value.trim()) {
    return [];
  }

  try {
    const parsed = JSON.parse(value);

    if (Array.isArray(parsed)) {
      return parsed.map(String).filter(Boolean);
    }
  } catch {
    return [value];
  }

  return [value];
}

function toScore(value) {
  if (value === null || value === undefined) return 0;

  const numberValue = Number(value);
  return Number.isNaN(numberValue) ? 0 : Math.round(numberValue);
}

function formatDateTime(value) {
  if (!value) return '-';

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  const pad = (number) => String(number).padStart(2, '0');

  return [
    `${date.getFullYear()}.${pad(date.getMonth() + 1)}.${pad(date.getDate())}`,
    `${pad(date.getHours())}:${pad(date.getMinutes())}`,
  ].join(' ');
}

function getRecoveryHint(errorCode) {
  if (errorCode === 'PROFILE_SNAPSHOT_INVALID') {
    return '내 정보가 충분히 저장되어 있는지 확인한 뒤 다시 진단해 주세요.';
  }

  if (errorCode === 'INVALID_INPUT') {
    return '공고 회사명, 포지션, 원문 내용을 확인한 뒤 다시 진단해 주세요.';
  }

  return '잠시 후 같은 공고로 다시 시도하거나, 공고 원문을 조금 줄여 다시 진단을 시작해 주세요.';
}
