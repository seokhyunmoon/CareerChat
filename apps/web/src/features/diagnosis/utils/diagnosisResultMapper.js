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
  const reportContentSections = parseReportContentSections(diagnosis.reportContent);

  return {
    ...diagnosis,
    createdAt: formatDateTime(diagnosis.createdAt),
    analysisStartedAt: formatDateTime(diagnosis.analysisStartedAt),
    completedAt: formatDateTime(diagnosis.completedAt),
    failedAt: formatDateTime(diagnosis.failedAt),
    reportSummary: cleanMarkdownText(diagnosis.reportSummary) || null,
    reportContent: cleanMarkdownText(diagnosis.reportContent) || null,
    reportContentSections,
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
  const strengthItems = normalizeStructuredItems(job.strengths, '강점');
  const relatedExperienceItems = normalizeStructuredItems(job.relatedExperiences, '관련 경험');
  const gapItems = normalizeStructuredItems(job.gaps, '보완점');
  const resumeHighlightItems = normalizeStructuredItems(job.resumeHighlights, '강조 포인트');
  const strategyItems = normalizeStructuredItems(job.strategyAdvice, '지원 전략');
  const fallbackStrengthItems = strengthItems.length > 0
    ? strengthItems
    : [toFallbackStructuredItem(strengthsSummary, '강점')];
  const fallbackGapItems = gapItems.length > 0
    ? gapItems
    : [toFallbackStructuredItem(gapsSummary, '보완점')];
  const fallbackHighlightItems = resumeHighlightItems.length > 0
    ? resumeHighlightItems
    : (highlightPoints.length > 0 ? highlightPoints : [DEFAULT_HIGHLIGHT]).map((point, index) => ({
      title: `강조 포인트 ${index + 1}`,
      description: point,
      evidence: [],
      action: '',
      suggestedWording: '',
    }));

  return {
    ...job,
    rankOrder: job.rankOrder ?? job.displayOrder,
    fitScore: toScore(job.fitScore),
    strengthsSummary,
    gapsSummary,
    strengthItems: fallbackStrengthItems,
    relatedExperienceItems,
    gapItems: fallbackGapItems,
    strategyItems,
    strengths: fallbackStrengthItems.map((item) => item.title),
    gaps: fallbackGapItems.map((item) => ({
      title: item.title,
      body: item.description,
      action: item.action,
      evidence: item.evidence,
      suggestedWording: item.suggestedWording,
    })),
    highlightPoints: highlightPoints.join(', ') || DEFAULT_HIGHLIGHT,
    highlightCards: fallbackHighlightItems.map((item, index) => ({
      title: item.title || `강조 포인트 ${index + 1}`,
      body: item.description,
      action: item.action,
      evidence: item.evidence,
      suggestedWording: item.suggestedWording,
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
          evidenceItem?.text ??
          evidenceItem?.summary ??
          evidenceItem?.title ??
          item?.rationale ??
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

function normalizeStructuredItems(value, fallbackTitle) {
  const parsedValue = parseJsonLikeValue(value);

  if (!Array.isArray(parsedValue)) {
    return [];
  }

  return parsedValue
    .map((item, index) => toStructuredItem(item, fallbackTitle, index))
    .filter(Boolean);
}

function toStructuredItem(item, fallbackTitle, index) {
  if (typeof item === 'string') {
    const text = cleanMarkdownText(item);

    return text
      ? {
        title: `${fallbackTitle} ${index + 1}`,
        description: text,
        evidence: [],
        action: '',
        suggestedWording: '',
      }
      : null;
  }

  if (!item || typeof item !== 'object') {
    return null;
  }

  const title = cleanMarkdownText(item.title) || `${fallbackTitle} ${index + 1}`;
  const description =
    cleanMarkdownText(item.description) ||
    cleanMarkdownText(item.body) ||
    cleanMarkdownText(item.action) ||
    title;
  const evidence = normalizeEvidenceList(item.evidence);
  const action = cleanMarkdownText(item.action);
  const suggestedWording = cleanMarkdownText(item.suggestedWording);

  return {
    title,
    description,
    evidence,
    action,
    suggestedWording,
    priority: item.priority,
    status: item.status,
  };
}

function toFallbackStructuredItem(value, fallbackTitle) {
  const description = cleanMarkdownText(value);

  return {
    title: fallbackTitle,
    description,
    evidence: [],
    action: '',
    suggestedWording: '',
  };
}

function normalizeEvidenceList(value) {
  const parsedValue = parseJsonLikeValue(value);

  if (Array.isArray(parsedValue)) {
    return parsedValue
      .map((item) => cleanMarkdownText(
        typeof item === 'string'
          ? item
          : item?.text ?? item?.summary ?? item?.title ?? item?.description
      ))
      .filter(Boolean);
  }

  const evidenceValue = parsedValue && typeof parsedValue === 'object'
    ? parsedValue.text ?? parsedValue.summary ?? parsedValue.title ?? parsedValue.description
    : parsedValue;
  const text = cleanMarkdownText(evidenceValue);
  return text ? [text] : [];
}

function parseReportContentSections(value) {
  if (typeof value !== 'string' || !value.trim()) {
    return [];
  }

  const sectionLabels = [
    '한 줄 총평',
    '적합도 요약',
    '확실한 강점',
    '보완이 필요한 부분',
    '지원서에서 강조할 경험',
    '지원 전략 조언',
  ];
  const sectionPattern = new RegExp(`#{1,6}\\s*(${sectionLabels.join('|')})\\s*`, 'g');
  const normalized = value
    .replace(/\r\n/g, '\n')
    .replace(sectionPattern, '\n## $1\n');
  const sections = [];
  let currentSection = null;

  normalized.split('\n').forEach((rawLine) => {
    const line = rawLine.trim();
    if (!line) return;

    const headingMatch = line.match(/^#{1,6}\s+(.+)$/);
    if (headingMatch) {
      const title = cleanMarkdownText(headingMatch[1]);
      if (title) {
        currentSection = { title, items: [] };
        sections.push(currentSection);
      }
      return;
    }

    const text = cleanMarkdownText(line);
    if (!text) return;

    if (!currentSection) {
      currentSection = { title: '상세 요약', items: [] };
      sections.push(currentSection);
    }

    currentSection.items.push(text);
  });

  return sections
    .map((section) => ({
      ...section,
      items: section.items.filter(Boolean),
    }))
    .filter((section) => section.title && section.items.length > 0);
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
    return cleanMarkdownText(value) || fallback;
  }

  return fallback;
}

function cleanMarkdownText(value) {
  if (value === null || value === undefined) {
    return '';
  }

  if (typeof value !== 'string') {
    return String(value);
  }

  return value
    .replace(/\r\n/g, '\n')
    .split('\n')
    .map((line) => line
      .trim()
      .replace(/^#{1,6}\s*/, '')
      .replace(/^[-*]\s+/, '')
      .replace(/^>\s+/, '')
      .trim())
    .filter(Boolean)
    .join('\n')
    .replace(/\s{2,}/g, ' ')
    .trim();
}
