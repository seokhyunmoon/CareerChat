export const diagnosisStatusLabels = {
  PENDING: '접수됨',
  PROCESSING: '분석 중',
  COMPLETED: '완료',
  FAILED: '실패',
};

export const mockDiagnoses = [
  {
    diagnosisId: 1002,
    status: 'PROCESSING',
    createdAt: '2026.05.22 15:42',
    companies: '토스 · 네이버 클라우드 · 라인플러스',
    jobsSummary: 'AI Engineer · LLM/RAG 서비스 개발 · 백엔드 서버 개발',
    meta: '공고 3개 비교',
    loadingMessage: '입력한 공고와 저장된 내 정보를 비교하고 있습니다.',
  },
  {
    diagnosisId: 1001,
    status: 'COMPLETED',
    createdAt: '2026.05.22 14:18',
    completedAt: '2026.05.22 14:20',
    companies: '토스 · 네이버 클라우드 · 라인플러스',
    jobsSummary: 'AI Engineer · LLM/RAG 서비스 개발 · 백엔드 서버 개발',
    meta: '공고 3개 비교',
    reportSummary: 'RAG 시스템 구현 경험이 핵심 요구사항과 직접 맞는 토스 AI Engineer 공고를 1순위로 추천합니다.',
    reportContent: '현재 프로필은 RAG 기반 문서 분석, Spring Boot API 설계, Docker 기반 개발 환경 구성 경험이 뚜렷합니다. AI Platform 성격의 공고에서는 검색 품질 개선 경험을 강하게 제시하고, 백엔드 중심 공고에서는 API 설계와 데이터 모델링 경험을 앞세우는 전략이 적합합니다.',
    jobs: [
      {
        jdId: 20,
        displayOrder: 1,
        rankOrder: 1,
        companyName: '토스',
        position: 'AI Engineer',
        fitScore: 86,
        strengthsSummary: 'RAG 시스템 구현, hybrid retrieval, LLM reranking 경험이 필수 요구사항과 강하게 맞습니다.',
        gapsSummary: 'Agent 운영 경험과 대규모 AI platform 운영 경험은 추가 근거가 필요합니다.',
        highlightPoints: 'Financial Document Analyzer의 chunking 개선, BM25+dense retrieval, RRF, reranking 흐름을 수치와 함께 강조하세요.',
        strengths: [
          'A*STAR IHPC 인턴십에서 Python 기반 RAG 시스템을 실제로 설계·구현한 경험이 공고 핵심 요구사항과 직접 매칭됩니다.',
          'Hybrid Retrieval, RRF, LLM Reranking 흐름을 직접 다뤄본 점이 AI 서비스 최적화 이해도를 보여줍니다.',
          'CareerChat 프로젝트에서 Spring Boot와 AI 분석 구조를 함께 설계한 경험이 AI 백엔드 역량을 보강합니다.',
          'FinanceBench 기반 정량 평가 경험은 AI 서비스 품질을 수치로 설명할 수 있는 차별화 포인트입니다.',
        ],
        gaps: [
          {
            title: 'Agent 운영 경험',
            body: 'RAG 경험은 뚜렷하지만 Agent를 실제 서비스 흐름에 운영한 근거는 아직 약합니다.',
          },
          {
            title: '대규모 AI 서비스 운영 경험',
            body: '성능 지표, 장애 대응, 비용 최적화 경험을 추가로 정리하면 설득력이 높아집니다.',
          },
        ],
        highlightCards: [
          {
            title: '강조할 경험',
            body: 'Financial Document Analyzer에서 chunking 전략 개선, hybrid retrieval, reranking을 단계적으로 적용한 과정을 수치와 함께 서술하세요.',
          },
          {
            title: '강조할 기술',
            body: 'Python, RAG, LangGraph, vector search, Spring Boot, PostgreSQL 순으로 공고와 맞는 기술을 앞쪽에 배치하세요.',
          },
        ],
        requirementMatches: [
          {
            normalizedText: 'LLM, RAG, Agent 적용 경험',
            importance: 'required',
            matchLevel: 'partial',
            reason: 'RAG 구현 경험은 명확하지만 Agent 운영 경험은 직접 근거가 부족합니다.',
            evidence: 'A*STAR IHPC에서 금융 문서 질의응답용 RAG 시스템을 개발하고 hybrid retrieval과 reranking을 적용했습니다.',
          },
          {
            normalizedText: '구조화되지 않은 문제의 시스템적 해결',
            importance: 'required',
            matchLevel: 'strong',
            reason: '문서 parsing, chunking, retrieval 품질 문제를 단계적으로 개선한 근거가 있습니다.',
            evidence: 'section title을 metadata로 분리하고 low-context title chunk 반환 문제를 줄였습니다.',
          },
        ],
      },
      {
        jdId: 21,
        displayOrder: 2,
        rankOrder: 2,
        companyName: '네이버 클라우드',
        position: 'LLM/RAG 서비스 개발',
        fitScore: 78,
        strengthsSummary: 'RAG 구성과 embedding/vector search 이해도가 강점입니다.',
        gapsSummary: '클라우드 운영, NCP 기반 서비스 배포 근거가 상대적으로 약합니다.',
        highlightPoints: 'sentence-transformers, vector search, evaluation script 경험을 LLM 서비스 개발 역량으로 연결하세요.',
        strengths: [
          'RAG pipeline 구성과 embedding 기반 검색 흐름을 이해하고 직접 구현한 경험이 있습니다.',
          '문서 chunking, metadata 설계, vector search 최적화 경험이 LLM 서비스 개발 요구사항과 연결됩니다.',
          '평가 스크립트와 benchmark를 활용해 검색 품질을 확인한 경험이 있습니다.',
        ],
        gaps: [
          {
            title: '클라우드 운영 경험',
            body: 'NCP 또는 유사 클라우드 환경에서 운영한 경험은 이력서상 근거가 상대적으로 약합니다.',
          },
          {
            title: '서비스 배포 사례 구체화',
            body: '배포 환경, 모니터링 방식, 운영 중 개선한 내용을 함께 정리하면 좋습니다.',
          },
        ],
        highlightCards: [
          {
            title: '강조할 경험',
            body: 'RAG 시스템에서 문서 분할, 검색, 재정렬, 평가까지 이어지는 전체 흐름을 프로젝트 단위로 설명하세요.',
          },
          {
            title: '강조할 기술',
            body: 'sentence-transformers, vector search, BM25, LangGraph, Docker 기반 실행 환경을 LLM 서비스 역량으로 연결하세요.',
          },
        ],
        requirementMatches: [
          {
            normalizedText: 'RAG 서비스 개발 경험',
            importance: 'required',
            matchLevel: 'strong',
            reason: '실제 RAG 구현과 평가 경험이 있습니다.',
            evidence: 'FinanceBench benchmark를 기준으로 retrieval 품질을 측정했습니다.',
          },
        ],
      },
      {
        jdId: 22,
        displayOrder: 3,
        rankOrder: 3,
        companyName: '라인플러스',
        position: '백엔드 서버 개발',
        fitScore: 67,
        strengthsSummary: 'Spring Boot 기반 인증, 프로필, 진단 요청 API 설계 경험이 있습니다.',
        gapsSummary: '대규모 트래픽, Java/Kotlin production 경험은 보완이 필요합니다.',
        highlightPoints: 'CareerChat의 Spring 도메인 설계와 PostgreSQL 기반 Entity 구성을 백엔드 역량으로 강조하세요.',
        strengths: [
          'Spring Boot 기반 인증, 프로필, 진단 요청 API를 구현한 경험이 백엔드 기본 역량을 보여줍니다.',
          'PostgreSQL 기반 Entity 구성과 도메인 테이블 설계 경험이 있습니다.',
          'Docker 기반 개발 환경을 구성해 프론트, 백엔드, 데이터베이스 실행 흐름을 이해하고 있습니다.',
        ],
        gaps: [
          {
            title: 'Java/Kotlin 실무 근거',
            body: 'Spring Boot 사용 경험은 있으나 Java/Kotlin 기반 production 경험은 더 구체화가 필요합니다.',
          },
          {
            title: '대규모 동시 요청 처리',
            body: '성능 테스트나 병목 개선 사례가 추가되면 서버 개발 포지션 설득력이 높아집니다.',
          },
        ],
        highlightCards: [
          {
            title: '강조할 프로젝트',
            body: 'CareerChat의 인증, 프로필, 진단 요청 API 설계와 도메인 저장 흐름을 명확히 기술하세요.',
          },
          {
            title: '보완 제안',
            body: '어학 성적과 협업 경험을 함께 배치해 글로벌 서비스 환경에서의 커뮤니케이션 역량을 보여주세요.',
          },
        ],
        requirementMatches: [
          {
            normalizedText: 'Spring 기반 API 설계 경험',
            importance: 'required',
            matchLevel: 'strong',
            reason: 'CareerChat에서 인증, 프로필, 진단 도메인 API를 설계했습니다.',
            evidence: 'CareerChat에서 진단 요청 생성과 공고별 결과 저장 흐름을 구현했습니다.',
          },
        ],
      },
    ],
  },
  {
    diagnosisId: 1000,
    status: 'FAILED',
    createdAt: '2026.05.21 19:10',
    companies: '카카오엔터프라이즈 · 쿠팡',
    jobsSummary: 'AI 백엔드 개발자 · Platform Engineer',
    meta: '공고 2개 비교',
    errorMessage: '일시적인 처리 지연으로 분석을 완료하지 못했습니다.',
    recoveryHint: '잠시 후 같은 공고로 다시 진단을 시작하거나, 공고 원문 길이를 줄여 다시 시도하세요.',
  },
];

export function getDiagnosisById(diagnosisId) {
  return mockDiagnoses.find((diagnosis) => String(diagnosis.diagnosisId) === String(diagnosisId));
}

export function getLatestDiagnosis() {
  return mockDiagnoses[0];
}
