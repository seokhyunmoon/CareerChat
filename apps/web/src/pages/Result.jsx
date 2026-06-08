import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle,
  BriefcaseBusiness,
  CheckCircle2,
  FileText,
  Lightbulb,
  Target,
} from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  createDiagnosisChatMessage,
  getDiagnosis,
  getDiagnosisChatMessages,
} from '@/features/diagnosis/api/diagnosisApi';
import AnalysisLoadingOverlay from '@/features/diagnosis/AnalysisLoadingOverlay';
import {
  isPollingStatus,
  toDiagnosisViewModel,
  toResultErrorViewModel,
} from '@/features/diagnosis/utils/diagnosisResultMapper';

const POLLING_INTERVAL_MS = 3000;

const INTRO_CHAT_MESSAGE = {
  id: 'intro',
  role: 'ai',
  text: '분석 결과를 바탕으로 공고별 강점, 부족한 근거, 이력서 강조 방향을 설명해드릴게요.',
  time: '방금 전',
};

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

function getRankClass(index, jobCount, score) {
  if (jobCount === 1) {
    if (score >= 70) return 'r1';
    if (score >= 40) return 'r2';
    return 'r-low';
  }

  if (index === 0) return 'r1';
  if (index === 1) return 'r2';
  return 'r3';
}

function getScoreClass(score) {
  if (score >= 70) return 's1';
  if (score >= 40) return 's2';
  return 's-low';
}

function getBarClass(score) {
  if (score >= 70) return 'b1';
  if (score >= 40) return 'b2';
  return 'b-low';
}

function getRankLabel(index, jobCount) {
  return jobCount === 1 ? '대상' : rankLabels[index];
}

function getResultStatus(job) {
  if (!job) return { label: '분석 완료', tone: '' };
  if (job.fitScore < 40) return { label: '보완 우선', tone: 'caution' };
  if (job.fitScore < 70) return { label: '검토 필요', tone: 'caution' };

  return { label: '분석 완료', tone: '' };
}

function StructuredItemList({ items, icon, tone = 'default' }) {
  return (
    <div className={`structured-list ${tone}`}>
      {items.map((item, index) => (
        <div className="structured-item" key={`${item.title}-${index}`}>
          <div className="structured-item-icon" aria-hidden="true">
            {React.createElement(icon, { size: 17, strokeWidth: 2 })}
          </div>
          <div className="structured-item-content">
            <div className="structured-item-title">{item.title}</div>
            <div className="structured-item-description">{item.description}</div>
            {item.evidence?.length > 0 && (
              <div className="structured-item-evidence">
                <span>근거</span>
                {item.evidence.join(' · ')}
              </div>
            )}
            {item.action && (
              <div className="structured-item-action">
                <span>다음 행동</span>
                {item.action}
              </div>
            )}
            {item.suggestedWording && (
              <div className="structured-item-wording">
                <span>추천 문구</span>
                {item.suggestedWording}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function toChatMessageViewModel(message) {
  return {
    id: message.messageId ? String(message.messageId) : `${message.role}-${message.createdAt}-${message.content}`,
    role: message.role === 'USER' ? 'user' : 'ai',
    text: message.content,
    time: formatChatTime(message.createdAt),
    evidenceData: message.evidenceData,
  };
}

function formatChatTime(value) {
  if (!value) {
    return '방금 전';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '방금 전';
  }

  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

function toChatErrorMessage(error) {
  if (error?.code === 'AI_CHAT_RESPONSE_FAILED') {
    return 'AI 답변을 생성하지 못했습니다. 잠시 후 다시 질문해 주세요.';
  }

  if (error?.code === 'DIAGNOSIS_NOT_COMPLETED') {
    return '진단 결과가 준비된 뒤 질문할 수 있습니다.';
  }

  if (error?.code === 'UNAUTHORIZED') {
    return '로그인이 만료되었습니다. 다시 로그인한 뒤 이용해 주세요.';
  }

  if (error?.status === 404 || error?.code === 'RESOURCE_NOT_FOUND') {
    return '챗봇 대화를 불러올 진단 결과를 찾지 못했습니다.';
  }

  return '챗봇 메시지를 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.';
}

function ResultStatusMessage({ title, description, actionLabel, onAction }) {
  const navigate = useNavigate();

  return (
    <div id="page-result" className="page active">
      <div className="result-layout">
        <div className="result-main">
          <div className="result-hero failed-hero fade-up">
            <div className="result-hero-top">
              <div>
                <div className="tag danger page-step result-step-tag">STEP 4 / 4</div>
                <div className="result-title page-title">
                  진단 결과를
                  <br />
                  확인할 수 없습니다
                </div>
                <div className="result-meta page-subtitle">진단 상태 조회</div>
              </div>
              <div className="result-tag danger">확인 필요</div>
            </div>
            <div className="failure-box">
              <div className="failure-title">{title}</div>
              <div className="failure-desc">{description}</div>
            </div>
          </div>
          <div className="result-actions">
            <button className="btn btn-primary" onClick={onAction}>
              {actionLabel}
            </button>
            <button className="btn btn-outline" onClick={() => navigate('/analyze')}>
              새 진단 시작하기
            </button>
          </div>
        </div>

        <div className="chat-panel status-panel">
          <div className="chat-header">
            <div className="chat-dot danger"></div>
            <div>
              <div className="chat-title">안내</div>
              <div className="chat-subtitle">진단 상태 확인</div>
            </div>
          </div>
          <div className="status-panel-body">
            <div className="status-kicker">다음 행동</div>
            <p>{description}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Result() {
  const navigate = useNavigate();
  const { diagnosisId } = useParams();
  const [diagnosis, setDiagnosis] = useState(null);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const jobs = useMemo(
    () => [...(diagnosis?.jobs ?? [])].sort((a, b) => a.rankOrder - b.rankOrder),
    [diagnosis?.jobs]
  );
  const [activeTab, setActiveTab] = useState(0);
  const [chatMessages, setChatMessages] = useState([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [isChatSending, setIsChatSending] = useState(false);
  const [chatError, setChatError] = useState(null);
  const [inputValue, setInputValue] = useState('');
  const chatMessagesRef = useRef(null);

  useEffect(() => {
    let isActive = true;
    let pollingTimerId = null;

    const clearPollingTimer = () => {
      if (pollingTimerId) {
        window.clearTimeout(pollingTimerId);
        pollingTimerId = null;
      }
    };

    async function loadDiagnosis({ showInitialLoading = false } = {}) {
      if (!diagnosisId) {
        setLoadError(toResultErrorViewModel({ status: 404 }));
        setIsInitialLoading(false);
        return;
      }

      try {
        if (showInitialLoading) {
          setIsInitialLoading(true);
        }

        const response = await getDiagnosis(diagnosisId);

        if (!isActive) return;

        const nextDiagnosis = toDiagnosisViewModel(response);
        setDiagnosis(nextDiagnosis);
        setLoadError(null);
        setIsInitialLoading(false);

        clearPollingTimer();

        if (isPollingStatus(nextDiagnosis.status)) {
          pollingTimerId = window.setTimeout(() => {
            loadDiagnosis();
          }, POLLING_INTERVAL_MS);
        }
      } catch (error) {
        if (!isActive) return;

        clearPollingTimer();
        setLoadError(toResultErrorViewModel(error));
        setIsInitialLoading(false);
      }
    }

    loadDiagnosis({ showInitialLoading: true });

    return () => {
      isActive = false;
      clearPollingTimer();
    };
  }, [diagnosisId]);

  useEffect(() => {
    if (diagnosis?.status !== 'COMPLETED' || !diagnosisId) {
      setChatMessages([]);
      setChatError(null);
      setIsChatLoading(false);
      setIsChatSending(false);
      return undefined;
    }

    let isActive = true;

    async function loadChatMessages() {
      try {
        setIsChatLoading(true);
        setChatError(null);

        const response = await getDiagnosisChatMessages(diagnosisId);
        if (!isActive) return;

        setChatMessages((response.messages ?? []).map(toChatMessageViewModel));
      } catch (error) {
        if (!isActive) return;
        setChatError(toChatErrorMessage(error));
      } finally {
        if (isActive) {
          setIsChatLoading(false);
        }
      }
    }

    loadChatMessages();

    return () => {
      isActive = false;
    };
  }, [diagnosis?.status, diagnosisId]);

  useEffect(() => {
    if (!chatMessagesRef.current) {
      return;
    }

    chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
  }, [chatMessages, isChatSending, chatError]);

  const safeActiveTab = activeTab < jobs.length ? activeTab : 0;
  const activeJob = jobs[safeActiveTab] ?? jobs[0];
  const resultStatus = getResultStatus(jobs[0]);
  const displayChatMessages = chatMessages.length > 0 ? chatMessages : [INTRO_CHAT_MESSAGE];
  const canSendChat = diagnosis?.status === 'COMPLETED' && !isChatLoading && !isChatSending;
  const showQuickQuestions = !isChatLoading && !isChatSending && chatMessages.length === 0;

  const handleSendChat = async (text) => {
    const messageText = text || inputValue.trim();
    if (!messageText || diagnosis?.status !== 'COMPLETED' || isChatLoading || isChatSending) return;

    try {
      setIsChatSending(true);
      setChatError(null);

      const response = await createDiagnosisChatMessage(diagnosisId, messageText);
      const nextMessages = [
        response.userMessage,
        response.assistantMessage,
      ].filter(Boolean).map(toChatMessageViewModel);

      setChatMessages((prev) => [...prev, ...nextMessages]);
      if (!text) {
        setInputValue('');
      }
    } catch (error) {
      setChatError(toChatErrorMessage(error));
    } finally {
      setIsChatSending(false);
    }
  };

  if (isInitialLoading) {
    return (
      <AnalysisLoadingOverlay
        show
        message="진단 상태를 불러오고 있습니다."
        steps={[
          '진단 요청 확인 중',
          '분석 상태 조회 중',
          '결과 화면 준비 중',
        ]}
      />
    );
  }

  if (loadError) {
    return (
      <ResultStatusMessage
        {...loadError}
        onAction={() => navigate(loadError.actionPath)}
      />
    );
  }

  if (!diagnosis) {
    return (
      <ResultStatusMessage
        title="진단 상태를 확인할 수 없습니다."
        description="잠시 후 다시 시도하거나 진단 기록에서 다시 열어 주세요."
        actionLabel="진단 기록으로"
        onAction={() => navigate('/history')}
      />
    );
  }

  if (diagnosis.status === 'PROCESSING' || diagnosis.status === 'PENDING') {
    return (
      <AnalysisLoadingOverlay
        show
        message={diagnosis.loadingMessage ?? 'AI 분석 중...'}
      />
    );
  }

  if (diagnosis.status === 'FAILED') {
    const failure = diagnosis.failure ?? {
      title: '분석을 완료하지 못했습니다.',
      description: '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.',
      nextAction: '같은 공고로 다시 시도하거나 진단 기록에서 상태를 확인해 주세요.',
    };

    return (
      <div id="page-result" className="page active">
        <div className="result-layout">
          <div className="result-main">
            <div className="result-hero failed-hero fade-up">
              <div className="result-hero-top">
                <div>
                  <div className="tag danger page-step result-step-tag">STEP 4 / 4</div>
                  <div className="result-title page-title">
                    분석을 완료하지
                    <br />
                    못했습니다
                  </div>
                  <div className="result-meta page-subtitle">
                    요청일 {diagnosis.createdAt} · {diagnosis.meta}
                  </div>
                </div>
                <div className="result-tag danger">분석 실패</div>
              </div>
              <div className="failure-box">
                <div className="failure-title">{failure.title}</div>
                <div className="failure-desc">{failure.description}</div>
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
              <p>{failure.nextAction}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (diagnosis.status === 'COMPLETED' && jobs.length === 0) {
    return (
      <ResultStatusMessage
        title="결과 데이터가 누락되었습니다."
        description="분석은 완료됐지만 화면에 표시할 공고별 결과가 응답에 포함되지 않았습니다. 진단 기록에서 다시 열어보거나 새 진단을 시작해 주세요."
        actionLabel="진단 기록으로"
        onAction={() => navigate('/history')}
      />
    );
  }

  return (
    <div id="page-result" className="page active">
      <div className="result-layout">
        <div className="result-main">
          <div className="history-header page-header">
            <div className="tag page-step">STEP 4 / 4</div>
            <div className="history-title page-title">진단 결과 리포트</div>
            <div className="history-sub page-subtitle">분석일 {diagnosis.completedAt} · {diagnosis.meta}</div>
          </div>
          <div className="result-hero fade-up">
            <div className="result-hero-top">
              <div className="result-tag">
                <span className="pulse" aria-hidden="true"></span>
                {jobs.length === 1 ? '공고 적합도 분석' : '지원 우선순위 추천'}
              </div>
              <div className={`result-tag ${resultStatus.tone}`}>
                <span className="pulse" aria-hidden="true"></span>
                {resultStatus.label}
              </div>
            </div>
            <div className="ranking-list">
              {jobs.map((job, index) => (
                <div className="rank-item" key={job.jdId}>
                  <div className={`rank-badge ${getRankClass(index, jobs.length, job.fitScore)}`}>
                    {getRankLabel(index, jobs.length)}
                  </div>
                  <div className="rank-info">
                    <div className="rank-company">{job.companyName}</div>
                    <div className="rank-job">{job.position}</div>
                  </div>
                  <div className="rank-score-wrap">
                    <div className={`rank-score ${getScoreClass(job.fitScore)}`}>
                      {job.fitScore}
                      <span style={{ fontSize: '16px', color: 'var(--muted)' }}>점</span>
                    </div>
                    <div className="rank-bar-wrap">
                      <div
                        className={`rank-bar ${getBarClass(job.fitScore)}`}
                        style={{ width: `${job.fitScore}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card report-overview fade-up fade-up-d1">
            <div className="tag" style={{ marginBottom: '12px' }}>분석 요약</div>
            <div className="report-summary-title">
              {diagnosis.reportSummary ?? '요약 결과가 아직 제공되지 않았습니다.'}
            </div>
            {diagnosis.reportContentSections?.length > 0 ? (
              <div className="report-section-list">
                {diagnosis.reportContentSections.map((section, sectionIndex) => (
                  <div className="report-section" key={`${section.title}-${sectionIndex}`}>
                    <div className="report-section-title">{section.title}</div>
                    <ul>
                      {section.items.map((item, index) => (
                        <li key={`${section.title}-${index}`}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            ) : (
              <p className="report-summary-content">
                {diagnosis.reportContent ?? '상세 분석 본문이 아직 제공되지 않았습니다.'}
              </p>
            )}
          </div>

          <div className="card fade-up fade-up-d2">
            <div style={{ marginBottom: '16px' }}>
              <div className="tag" style={{ marginBottom: '12px' }}>공고별 상세 분석</div>
            </div>
            <div className="job-tabs">
              {jobs.map((job, index) => (
                <button
                  className={`job-tab ${safeActiveTab === index ? 'active' : ''}`}
                  key={job.jdId}
                  onClick={() => setActiveTab(index)}
                >
                  <span className={`job-tab-dot ${getScoreClass(job.fitScore)}`} aria-hidden="true"></span>
                  {job.companyName}
                </button>
              ))}
            </div>

            {activeJob && (
              <div className="detail-panel active">
                <div className="detail-section-heading">
                  <CheckCircle2 size={16} aria-hidden="true" />
                  <span>확인된 강점</span>
                </div>
                <StructuredItemList items={activeJob.strengthItems} icon={CheckCircle2} tone="strength" />

                {activeJob.relatedExperienceItems.length > 0 && (
                  <>
                    <div className="detail-section-heading">
                      <BriefcaseBusiness size={16} aria-hidden="true" />
                      <span>관련 경험</span>
                    </div>
                    <StructuredItemList
                      items={activeJob.relatedExperienceItems}
                      icon={BriefcaseBusiness}
                      tone="experience"
                    />
                  </>
                )}

                <div className="detail-section-heading">
                  <AlertTriangle size={16} aria-hidden="true" />
                  <span>부족 역량 및 보완 방향</span>
                </div>
                <StructuredItemList items={activeJob.gapItems} icon={AlertTriangle} tone="gap" />

                <div className="detail-section-heading">
                  <FileText size={16} aria-hidden="true" />
                  <span>이력서 강조 포인트</span>
                </div>
                <div className="highlight-cards">
                  {activeJob.highlightCards.map((card, index) => (
                    <div className="highlight-card" key={`${card.title}-${index}`}>
                      <div className="highlight-card-title">{card.title}</div>
                      <div className="highlight-card-body">{card.body}</div>
                      {card.action && (
                        <div className="highlight-card-action">
                          <span>반영 방법</span>
                          {card.action}
                        </div>
                      )}
                      {card.suggestedWording && (
                        <div className="highlight-card-wording">
                          <span>추천 문구</span>
                          {card.suggestedWording}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {activeJob.strategyItems.length > 0 && (
                  <>
                    <div className="detail-section-heading strategy-heading">
                      <Target size={16} aria-hidden="true" />
                      <span>지원 전략</span>
                    </div>
                    <StructuredItemList items={activeJob.strategyItems} icon={Lightbulb} tone="strategy" />
                  </>
                )}

                <details className="evidence-details">
                  <summary>판단 근거 자세히 보기</summary>
                  <div className="requirement-list">
                    {activeJob.requirementMatches.length > 0 ? (
                      activeJob.requirementMatches.map((requirement, index) => (
                        <div className="requirement-item" key={`${requirement.normalizedText}-${index}`}>
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
                      ))
                    ) : (
                      <div className="requirement-empty">
                        요구사항별 판단 근거가 아직 제공되지 않았습니다.
                      </div>
                    )}
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
          <div className="chat-messages" id="chat-messages" ref={chatMessagesRef}>
            {isChatLoading ? (
              <div className="chat-state">이전 대화를 불러오는 중입니다.</div>
            ) : (
              displayChatMessages.map((msg) => (
                <div key={msg.id} className={`msg msg-${msg.role}`}>
                  {msg.text}
                  <div className="msg-time">{msg.time}</div>
                </div>
              ))
            )}
            {isChatSending && (
              <div className="msg msg-ai msg-pending">
                답변을 생성하고 있습니다.
                <div className="msg-time">잠시만요</div>
              </div>
            )}
            {chatError && (
              <div className="chat-feedback error">{chatError}</div>
            )}
          </div>
          <div className="chat-quick" style={{ display: showQuickQuestions ? 'flex' : 'none' }}>
            <button className="quick-btn" disabled={!canSendChat} onClick={() => handleSendChat('어떤 공고를 먼저 지원할까?')}>지원 순서 추천</button>
            <button className="quick-btn" disabled={!canSendChat} onClick={() => handleSendChat('강점을 어떻게 강조할까?')}>강점 강조 방법</button>
            <button className="quick-btn" disabled={!canSendChat} onClick={() => handleSendChat('부족한 점은 뭐야?')}>보완점 보기</button>
          </div>
          <div className="chat-input-wrap">
            <textarea
              className="chat-input"
              placeholder={isChatLoading ? '이전 대화를 불러오는 중...' : '질문을 입력하세요...'}
              rows="1"
              value={inputValue}
              disabled={!canSendChat}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendChat();
                }
              }}
            ></textarea>
            <button className="chat-send" disabled={!canSendChat || !inputValue.trim()} onClick={() => handleSendChat()}>
              ↑
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
