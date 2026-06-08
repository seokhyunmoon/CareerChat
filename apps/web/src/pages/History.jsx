import React, { useEffect, useMemo, useState } from 'react';
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
  const [statusFilter, setStatusFilter] = useState('ALL');

  const historyCounts = useMemo(() => {
    return diagnoses.reduce(
      (counts, item) => {
        counts.total += 1;
        if (item.status === 'COMPLETED') counts.completed += 1;
        if (item.status === 'FAILED') counts.failed += 1;
        return counts;
      },
      { total: 0, completed: 0, failed: 0 },
    );
  }, [diagnoses]);

  const filteredDiagnoses = useMemo(() => {
    if (statusFilter === 'ALL') return diagnoses;
    return diagnoses.filter((item) => item.status === statusFilter);
  }, [diagnoses, statusFilter]);

  const statusFilters = [
    { key: 'ALL', label: '전체', tone: 'all' },
    { key: 'COMPLETED', label: '완료', tone: 'completed' },
    { key: 'FAILED', label: '실패', tone: 'failed' },
  ];

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
        <div className="history-header page-header">
          <div className="tag page-step">STEP 3 / 4</div>
          <div className="history-title page-title">진단 기록</div>
          <div className="history-sub page-subtitle">과거에 진행한 비교 진단 결과를 다시 확인하세요.</div>
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
          <>
            <div className="history-toolbar">
              <div className="history-summary">
                <div>
                  <span>전체</span>
                  <strong>{historyCounts.total}</strong>
                </div>
                <div className="completed">
                  <span>완료</span>
                  <strong>{historyCounts.completed}</strong>
                </div>
                <div className="failed">
                  <span>실패</span>
                  <strong>{historyCounts.failed}</strong>
                </div>
              </div>
              <div className="history-filters" aria-label="진단 기록 상태 필터">
                {statusFilters.map((filter) => (
                  <button
                    key={filter.key}
                    type="button"
                    className={`history-filter ${filter.tone} ${statusFilter === filter.key ? 'active' : ''}`}
                    onClick={() => setStatusFilter(filter.key)}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>
            </div>

            {filteredDiagnoses.length === 0 ? (
              <HistoryFeedback
                title="해당 상태의 진단 기록이 없습니다."
                description="다른 상태 필터를 선택해 기록을 확인해 주세요."
              />
            ) : (
              <div className="history-list">
                {filteredDiagnoses.map((item) => (
                  <button
                    key={item.diagnosisId}
                    type="button"
                    className="history-item"
                    onClick={() => navigate(`/result/${item.diagnosisId}`)}
                  >
                    <div className="history-date">
                      <div className="h-day">{item.dateParts.day}</div>
                      <div>{item.dateParts.monthYear}</div>
                    </div>
                    <div className="history-info">
                      <div className="history-companies">{item.titleText}</div>
                      <div className="history-jobs">{item.jobsSummary}</div>
                      <div className="history-id">{item.createdAtLabel}</div>
                    </div>
                    <div className={`history-note ${item.statusClass}`}>
                      <div className={`history-status ${item.statusClass}`}>
                        {item.statusLabel}
                      </div>
                      <div>{item.summaryText}</div>
                    </div>
                    <div className={`history-meta ${item.statusClass}`}>
                      <div className="history-score">{item.scoreText}</div>
                      <div className="history-score-label">{item.scoreLabel}</div>
                    </div>
                    <div className={`history-action ${item.statusClass}`}>
                      {item.actionLabel}
                      <span>›</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
