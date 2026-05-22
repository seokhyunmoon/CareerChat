import React from 'react';

const DEFAULT_STEPS = [
  '공고 핵심 요소 추출 중',
  '프로필 데이터 매핑 중',
  '적합도 점수 계산 중',
  '보완 방향 생성 중',
];

const STEP_DELAYS = [600, 1400, 2200, 2900];

export default function AnalysisLoadingOverlay({
  show,
  message = 'AI 분석 중...',
  steps = DEFAULT_STEPS,
}) {
  if (!show) return null;

  return (
    <div className="loading-overlay show" role="status" aria-live="polite">
      <div className="loading-logo">CareerChat</div>
      <div className="loading-text">{message}</div>
      <div className="loading-bar-wrap">
        <div className="loading-bar"></div>
      </div>
      <div className="loading-steps">
        {steps.map((step, index) => (
          <div
            className="loading-step"
            key={step}
            style={{ '--step-delay': `${STEP_DELAYS[index] ?? STEP_DELAYS[STEP_DELAYS.length - 1]}ms` }}
          >
            <span className="loading-step-marker"></span>
            {step}
          </div>
        ))}
      </div>
    </div>
  );
}
