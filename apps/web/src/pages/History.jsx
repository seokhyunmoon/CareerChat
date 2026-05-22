import React from 'react';
import { useNavigate } from 'react-router-dom';
import { diagnosisStatusLabels, mockDiagnoses } from '@/features/diagnosis/mockDiagnosisData';

function parseDateParts(createdAt) {
  const [date] = createdAt.split(' ');
  const [, month, day] = date.split('.');

  return {
    day,
    month: `${month}월`,
  };
}

function getHighestScore(diagnosis) {
  if (diagnosis.status !== 'COMPLETED') return '-';

  const highest = Math.max(...diagnosis.jobs.map((job) => job.fitScore));
  return `${highest}점`;
}

function getHistoryScoreLabel(status) {
  return status === 'COMPLETED' ? '최고 적합도' : '분석 상태';
}

export default function History() {
  const navigate = useNavigate();

  return (
    <div id="page-history" className="page active">
      <div className="history-layout">
        <div className="history-header">
          <div className="history-title">진단 기록</div>
          <div className="history-sub">과거에 진행한 비교 진단 결과를 다시 확인하세요.</div>
        </div>
        <div className="history-list">
          {mockDiagnoses.map((item) => {
            const dateParts = parseDateParts(item.createdAt);

            return (
              <div
                key={item.diagnosisId}
                className="history-item"
                onClick={() => navigate(`/result/${item.diagnosisId}`)}
              >
                <div className="history-date">
                  <div className="h-day">{dateParts.day}</div>
                  <div>{dateParts.month}</div>
                </div>
                <div className="history-divider"></div>
                <div className="history-info">
                  <div className="history-companies">{item.companies}</div>
                  <div className="history-jobs">{item.jobsSummary}</div>
                  <div className="history-id">{item.createdAt}</div>
                </div>
                <div className="history-meta">
                  <div className={`history-status ${item.status.toLowerCase()}`}>
                    {diagnosisStatusLabels[item.status]}
                  </div>
                  <div className="history-score">{getHighestScore(item)}</div>
                  <div className="history-score-label">{getHistoryScoreLabel(item.status)}</div>
                </div>
                <div className="history-arrow">›</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
