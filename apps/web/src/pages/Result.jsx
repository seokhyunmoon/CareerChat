import React, { useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  getDiagnosisById,
  getLatestDiagnosis,
} from '@/features/diagnosis/mockDiagnosisData';
import AnalysisLoadingOverlay from '@/features/diagnosis/AnalysisLoadingOverlay';

const rankLabels = ['1st', '2nd', '3rd'];

const importanceLabels = {
  required: '필수',
  preferred: '우대',
};

const matchLevelLabels = {
  strong: '강함',
  partial: '부분',
  weak: '약함',
  none: '없음',
};

function getRankClass(index) {
  if (index === 0) return 'r1';
  if (index === 1) return 'r2';
  return 'r3';
}

function getScoreClass(index) {
  if (index === 0) return 's1';
  if (index === 1) return 's2';
  return 's3';
}

function getBarClass(index) {
  if (index === 0) return 'b1';
  if (index === 1) return 'b2';
  return 'b3';
}

export default function Result() {
  const navigate = useNavigate();
  const { diagnosisId } = useParams();
  const diagnosis = getDiagnosisById(diagnosisId) ?? getLatestDiagnosis();
  const jobs = useMemo(
    () => [...(diagnosis.jobs ?? [])].sort((a, b) => a.rankOrder - b.rankOrder),
    [diagnosis.jobs]
  );
  const [activeTab, setActiveTab] = useState(0);
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'ai',
      text: '분석 결과를 바탕으로 공고별 강점, 부족한 근거, 이력서 강조 방향을 설명해드릴게요.',
      time: '방금 전',
    },
  ]);
  const [inputValue, setInputValue] = useState('');

  const activeJob = jobs[activeTab] ?? jobs[0];
  const topJob = jobs[0];

  const handleSendChat = (text) => {
    const messageText = text || inputValue.trim();
    if (!messageText || diagnosis.status !== 'COMPLETED') return;

    const time = new Date().toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
    });
    setChatMessages((prev) => [...prev, { role: 'user', text: messageText, time }]);
    setInputValue('');

    setTimeout(() => {
      const reply = topJob
        ? `${topJob.companyName} ${topJob.position} 공고가 현재 1순위입니다. ${topJob.highlightPoints} 부족한 부분은 "${topJob.gapsSummary}"로 정리되어 있으니, 이 부분을 자기소개서와 포트폴리오에서 보완하는 전략이 좋습니다.`
        : '완료된 분석 결과가 있을 때 공고별 지원 전략을 더 자세히 설명할 수 있습니다.';
      setChatMessages((prev) => [...prev, { role: 'ai', text: reply, time }]);
    }, 700);
  };

  if (diagnosis.status === 'PROCESSING' || diagnosis.status === 'PENDING') {
    return (
      <AnalysisLoadingOverlay
        show
        message={diagnosis.loadingMessage ?? 'AI 분석 중...'}
      />
    );
  }

  if (diagnosis.status === 'FAILED') {
    return (
      <div id="page-result" className="page active">
        <div className="result-layout">
          <div className="result-main">
            <div className="result-hero failed-hero fade-up">
              <div className="result-hero-top">
                <div>
                  <div className="tag danger" style={{ marginBottom: '12px' }}>분석 실패</div>
                  <div className="result-title">
                    분석을 완료하지
                    <br />
                    못했습니다
                  </div>
                  <div className="result-meta">
                    요청일 {diagnosis.createdAt} · {diagnosis.meta}
                  </div>
                </div>
                <div className="result-tag danger">다시 시도 가능</div>
              </div>
              <div className="failure-box">
                <div className="failure-title">{diagnosis.errorMessage}</div>
                <div className="failure-desc">{diagnosis.recoveryHint}</div>
              </div>
            </div>
            <div className="result-actions">
              <button className="btn btn-primary" onClick={() => navigate('/analyze')}>다시 진단하기</button>
              <button className="btn btn-outline" onClick={() => navigate('/history')}>진단 기록으로</button>
            </div>
          </div>

          <div className="chat-panel status-panel">
            <div className="chat-header">
              <div className="chat-dot danger"></div>
              <div>
                <div className="chat-title">안내</div>
                <div className="chat-subtitle">다시 진단하기</div>
              </div>
            </div>
            <div className="status-panel-body">
              <div className="status-kicker">다음 행동</div>
              <p>
                일시적인 오류가 발생했을 수 있습니다. 같은 공고로 다시 시도하거나,
                공고 원문을 조금 줄여 다시 진단을 시작해 주세요.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div id="page-result" className="page active">
      <div className="result-layout">
        <div className="result-main">
          <div className="result-hero fade-up">
            <div className="result-hero-top">
              <div>
                <div className="tag" style={{ marginBottom: '12px' }}>분석 완료</div>
                <div className="result-title">
                  지원 우선순위
                  <br />
                  리포트
                </div>
                <div className="result-meta">
                  분석일 {diagnosis.completedAt} · {diagnosis.meta}
                </div>
              </div>
              <div className="result-tag">
                <span className="pulse">●</span> 신선한 분석
              </div>
            </div>
            <div className="ranking-list">
              {jobs.map((job, index) => (
                <div className="rank-item" key={job.jdId}>
                  <div className={`rank-badge ${getRankClass(index)}`}>{rankLabels[index]}</div>
                  <div className="rank-info">
                    <div className="rank-company">{job.companyName}</div>
                    <div className="rank-job">{job.position}</div>
                  </div>
                  <div className="rank-score-wrap">
                    <div className={`rank-score ${getScoreClass(index)}`}>
                      {job.fitScore}
                      <span style={{ fontSize: '16px', color: 'var(--muted)' }}>점</span>
                    </div>
                    <div className="rank-bar-wrap">
                      <div className={`rank-bar ${getBarClass(index)}`} style={{ width: `${job.fitScore}%` }}></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card fade-up fade-up-d1">
            <div style={{ marginBottom: '16px' }}>
              <div className="tag" style={{ marginBottom: '12px' }}>공고별 상세 분석</div>
            </div>
            <div className="job-tabs">
              {jobs.map((job, index) => (
                <button
                  className={`job-tab ${activeTab === index ? 'active' : ''}`}
                  key={job.jdId}
                  onClick={() => setActiveTab(index)}
                >
                  {['🟢', '🟡', '⚪'][index] ?? '•'} {job.companyName}
                </button>
              ))}
            </div>

            {activeJob && (
              <div className="detail-panel active">
                <span className="sub-label">✅ 강점</span>
                <div className="strength-list">
                  {(activeJob.strengths ?? [activeJob.strengthsSummary]).map((strength) => (
                    <div className="strength-item" key={strength}>
                      <div className="strength-icon">💪</div>
                      <div className="strength-text">{strength}</div>
                    </div>
                  ))}
                </div>

                <span className="sub-label">⚠️ 부족 역량 및 보완 방향</span>
                <div className="gap-list">
                  {(activeJob.gaps ?? [{ body: activeJob.gapsSummary }]).map((gap) => (
                    <div className="strength-item" key={`${gap.title ?? ''}-${gap.body}`}>
                      <div className="strength-icon">📌</div>
                      <div className="strength-text">
                        {gap.title && <strong style={{ color: 'var(--yellow)' }}>{gap.title}</strong>}
                        {gap.title ? ' — ' : ''}
                        {gap.body}
                      </div>
                    </div>
                  ))}
                </div>

                <span className="sub-label">📝 이력서 강조 포인트</span>
                <div className="highlight-cards">
                  {(activeJob.highlightCards ?? [
                    { title: '추천 서술 방향', body: activeJob.highlightPoints },
                  ]).map((card) => (
                    <div className="highlight-card" key={card.title}>
                      <div className="highlight-card-title">{card.title}</div>
                      <div className="highlight-card-body">{card.body}</div>
                    </div>
                  ))}
                </div>

                <details className="evidence-details">
                  <summary>판단 근거 자세히 보기</summary>
                  <div className="requirement-list">
                    {activeJob.requirementMatches.map((requirement) => (
                      <div className="requirement-item" key={requirement.normalizedText}>
                        <div className="requirement-head">
                          <div className="requirement-title">{requirement.normalizedText}</div>
                          <div className="requirement-badges">
                            <span>{importanceLabels[requirement.importance] ?? requirement.importance}</span>
                            <span>{matchLevelLabels[requirement.matchLevel] ?? requirement.matchLevel}</span>
                          </div>
                        </div>
                        <div className="requirement-reason">{requirement.reason}</div>
                        <div className="requirement-evidence">{requirement.evidence}</div>
                      </div>
                    ))}
                  </div>
                </details>
              </div>
            )}
          </div>

          <div className="result-actions">
            <button className="btn btn-outline" onClick={() => navigate('/history')}>진단 기록 보기</button>
            <button className="btn btn-primary" onClick={() => navigate('/analyze')}>새 진단 시작하기</button>
          </div>
        </div>

        <div className="chat-panel">
          <div className="chat-header">
            <div className="chat-dot"></div>
            <div>
              <div className="chat-title">AI 어시스턴트</div>
              <div className="chat-subtitle">결과 기반 Q&A</div>
            </div>
          </div>
          <div className="chat-messages" id="chat-messages">
            {chatMessages.map((msg) => (
              <div key={`${msg.role}-${msg.time}-${msg.text}`} className={`msg msg-${msg.role}`}>
                {msg.text}
                <div className="msg-time">{msg.time}</div>
              </div>
            ))}
          </div>
          <div className="chat-quick" style={{ display: chatMessages.length <= 1 ? 'flex' : 'none' }}>
            <button className="quick-btn" onClick={() => handleSendChat('어떤 공고를 먼저 지원할까?')}>지원 순서 추천</button>
            <button className="quick-btn" onClick={() => handleSendChat('RAG 경험을 어떻게 강조할까?')}>RAG 강조 방법</button>
            <button className="quick-btn" onClick={() => handleSendChat('부족한 점은 뭐야?')}>보완점 보기</button>
          </div>
          <div className="chat-input-wrap">
            <textarea
              className="chat-input"
              placeholder="질문을 입력하세요..."
              rows="1"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendChat();
                }
              }}
            ></textarea>
            <button className="chat-send" onClick={() => handleSendChat()}>↑</button>
          </div>
        </div>
      </div>
    </div>
  );
}
