import React from 'react';

const DEFAULT_STEPS = [
  '공고 핵심 요소를 확인하고 있습니다.',
  '저장된 내 정보와 비교하고 있습니다.',
  '지원 전략과 보완 방향을 정리하고 있습니다.',
];

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
      <div className="loading-helper">
        완료되면 자동으로 결과 화면으로 이동합니다.
      </div>
      <div className="loading-steps">
        {steps.map((step) => (
          <div
            className="loading-step"
            key={step}
          >
            <span className="loading-step-marker"></span>
            {step}
          </div>
        ))}
      </div>
    </div>
  );
}
