import { toDiagnosisFailureViewModel } from './diagnosisFailureMessages';

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
  MATCHED: 'strong',
  PARTIAL: 'partial',
  WEAK: 'weak',
  NONE: 'none',
};

const DEFAULT_STRENGTH = '아직 강점 요약이 제공되지 않았습니다.';
const DEFAULT_GAP = '아직 보완점 요약이 제공되지 않았습니다.';
const DEFAULT_HIGHLIGHT = '강점과 보완점을 바탕으로 이력서 핵심 경험을 정리해 주세요.';

export function isPollingStatus(status) {
  return POLLING_STATUSES.has(status);
}

export function toDiagnosisViewModel(diagnosis) {
  const jobs = (diagnosis.jobs ?? []).map(toJobViewModel);
  const jobCount = jobs.length;
  const failure = toDiagnosisFailureViewModel(diagnosis.errorCode);

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
    failure,
    errorMessage: failure.title,
    recoveryHint: failure.description,
    failureNextAction: failure.nextAction,
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
  const strengthsSummary = normalizeText(job.strengthsSummary, DEFAULT_STRENGTH);
  const gapsSummary = normalizeText(job.gapsSummary, DEFAULT_GAP);

  return {
    ...job,
    rankOrder: job.rankOrder ?? job.displayOrder,
    fitScore: toScore(job.fitScore),
    strengthsSummary,
    gapsSummary,
    strengths: [strengthsSummary],
    gaps: [{ body: gapsSummary }],
    highlightPoints: highlightPoints.join(', ') || DEFAULT_HIGHLIGHT,
    highlightCards: (highlightPoints.length > 0 ? highlightPoints : [DEFAULT_HIGHLIGHT]).map((point, index) => ({
      title: `강조 포인트 ${index + 1}`,
      body: point,
    })),
    requirementMatches: matchDetails,
  };
}

function normalizeMatchDetails(matchDetails) {
  const parsedMatchDetails = parseJsonLikeValue(matchDetails);
  const requirements = getRequirementItems(parsedMatchDetails);

  return requirements.map((requirement) => ({
    normalizedText:
      requirement.requirement?.description ??
      requirement.normalizedText ??
      requirement.name ??
      requirement.description ??
      '요구사항',
    importance: normalizeImportance(
      requirement.importance ?? requirement.priority ?? requirement.requirement?.priority
    ),
    matchLevel: normalizeMatchLevel(
      requirement.matchLevel ?? requirement.match ?? requirement.status
    ),
    reason:
      requirement.reason ??
      requirement.rationale ??
      requirement.gap ??
      '분석 결과에 포함된 판단 근거입니다.',
    evidence: formatEvidence(requirement.evidence),
  }));
}

function getRequirementItems(matchDetails) {
  if (Array.isArray(matchDetails)) {
    return matchDetails;
  }

  if (Array.isArray(matchDetails?.requirements)) {
    return matchDetails.requirements;
  }

  if (Array.isArray(matchDetails?.requirementMatches)) {
    return matchDetails.requirementMatches;
  }

  return [];
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
      .map((item) => {
        const evidenceItem = item?.evidence ?? item;

        return (
          item?.rationale ??
          evidenceItem?.text ??
          evidenceItem?.summary ??
          evidenceItem?.title ??
          evidenceItem?.sourceType ??
          null
        );
      })
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
  const parsedValue = parseJsonLikeValue(value);

  if (Array.isArray(parsedValue)) {
    return parsedValue.map(String).filter(Boolean);
  }

  if (Array.isArray(value)) {
    return value.map(String).filter(Boolean);
  }

  if (typeof value !== 'string' || !value.trim()) {
    return [];
  }

  return [value];
}

function parseJsonLikeValue(value) {
  if (typeof value !== 'string' || !value.trim()) {
    return value;
  }

  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
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

function normalizeText(value, fallback) {
  if (typeof value === 'string' && value.trim()) {
    return value;
  }

  return fallback;
}
