import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDiagnoses } from '@/features/diagnosis/api/diagnosisApi';
import {
  toDiagnosisHistoryItems,
  toHistoryErrorViewModel,
} from '@/features/diagnosis/utils/diagnosisHistoryMapper';

function HistoryFeedback({ title, description, actionLabel, onAction }) {
  return (
    <div className="history-feedback">
      <div className="history-feedback-title">{title}</div>
      <p>{description}</p>
      {actionLabel && (
        <button className="btn btn-primary" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
}

export default function History() {
  const navigate = useNavigate();
  const [diagnoses, setDiagnoses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    let isActive = true;

    async function loadDiagnoses() {
      try {
        setIsLoading(true);

        const response = await getDiagnoses();

        if (!isActive) return;

        setDiagnoses(toDiagnosisHistoryItems(response));
        setLoadError(null);
      } catch (error) {
        if (!isActive) return;

        setLoadError(toHistoryErrorViewModel(error));
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    loadDiagnoses();

    return () => {
      isActive = false;
    };
  }, []);

  return (
    <div id="page-history" className="page active">
      <div className="history-layout">
        <div className="history-header">
          <div className="history-title">진단 기록</div>
          <div className="history-sub">과거에 진행한 비교 진단 결과를 다시 확인하세요.</div>
        </div>

        {isLoading && (
          <HistoryFeedback
            title="진단 기록을 불러오는 중입니다."
            description="저장된 진단 목록을 확인하고 있습니다."
          />
        )}

        {!isLoading && loadError && (
          <HistoryFeedback
            {...loadError}
            onAction={() => navigate(loadError.actionPath)}
          />
        )}

        {!isLoading && !loadError && diagnoses.length === 0 && (
          <HistoryFeedback
            title="아직 진단 기록이 없습니다."
            description="공고를 입력하고 첫 진단을 시작하면 이곳에서 결과를 다시 확인할 수 있습니다."
            actionLabel="진단 시작하기"
            onAction={() => navigate('/analyze')}
          />
        )}

        {!isLoading && !loadError && diagnoses.length > 0 && (
          <div className="history-list">
            {diagnoses.map((item) => (
              <div
                key={item.diagnosisId}
                className="history-item"
                onClick={() => navigate(`/result/${item.diagnosisId}`)}
              >
                <div className="history-date">
                  <div className="h-day">{item.dateParts.day}</div>
                  <div>{item.dateParts.month}</div>
                </div>
                <div className="history-divider"></div>
                <div className="history-info">
                  <div className="history-companies">{item.companiesText}</div>
                  <div className="history-jobs">{item.jobsSummary}</div>
                  <div className="history-id">
                    {item.createdAtLabel}
                    {item.errorMessage ? ` · ${item.errorMessage}` : ''}
                  </div>
                </div>
                <div className="history-meta">
                  <div className={`history-status ${item.statusClass}`}>
                    {item.statusLabel}
                  </div>
                  <div className="history-score">{item.scoreText}</div>
                  <div className="history-score-label">{item.scoreLabel}</div>
                </div>
                <div className="history-arrow">›</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
