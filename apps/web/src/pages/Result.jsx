import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Result() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [chatMessages, setChatMessages] = useState([
    { role: 'ai', text: '안녕하세요! 분석 결과에 대해 궁금한 점이 있으면 편하게 물어보세요. 공고별 강점, 이력서 작성 팁, 보완 방향 등 무엇이든 답변해드릴게요. 😊', time: '방금 전' }
  ]);
  const [inputValue, setInputValue] = useState('');

  const aiResponses = {
    '카카오엔터프라이즈 합격 가능성은?': 'A*STAR IHPC 인턴십 RAG 경험이 핵심 강점입니다. 84점으로 가장 높은 적합도를 보이고 있어요. Hybrid Retrieval + RRF + Reranking 파이프라인을 FinanceBench 수치 변화와 함께 구체적으로 서술하면 합격 가능성이 한층 올라갑니다. Kotlin 학습 이력을 추가하면 더욱 유리합니다.',
    'RAG 경험 어떻게 강조할까?': '단순히 "RAG 구현"이라고 쓰지 말고, 문제 → 시도 → 결과 흐름으로 서술하세요. 예: "dense vector search 단독 사용 시 저품질 chunk 반환 문제 → element-based chunking + hybrid retrieval + RRF 적용 → FinanceBench 정답률 N% 향상" 처럼 수치를 곁들이면 면접관 눈에 확 띕니다.',
    '어떤 공고 먼저 지원할까?': '카카오엔터프라이즈(84점) → 네이버 클라우드(76점) → 라인플러스(61점) 순서를 추천합니다. RAG/AI 백엔드 쪽이 문석현님 프로필과 가장 잘 맞으므로, AI 포지션 먼저 집중적으로 지원하는 전략이 효과적입니다.'
  };

  const handleSendChat = (text) => {
    const messageText = text || inputValue.trim();
    if (!messageText) return;

    const newUserMsg = { role: 'user', text: messageText, time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }) };
    setChatMessages(prev => [...prev, newUserMsg]);
    setInputValue('');

    setTimeout(() => {
      const reply = aiResponses[messageText] || '좋은 질문이에요! 분석 결과를 바탕으로 말씀드리면, IHPC 인턴십 경험과 CareerChat 프로젝트의 AI 서비스 설계 역량이 가장 큰 강점입니다. 구체적인 수치와 함께 서술하는 것이 핵심이에요. 더 궁금한 점이 있으면 언제든지 물어보세요!';
      setChatMessages(prev => [...prev, { role: 'ai', text: reply, time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }) }]);
    }, 900);
  };

  return (
    <div id="page-result" className="page active">
      <div className="result-layout">
        {/* Main result */}
        <div className="result-main">
          {/* Summary hero */}
          <div className="result-hero fade-up">
            <div className="result-hero-top">
              <div>
                <div className="tag" style={{ marginBottom: '12px' }}>분석 완료</div>
                <div className="result-title">지원 우선순위<br />리포트</div>
                <div className="result-meta">분석일 2026.04.20 · 공고 3개 비교</div>
              </div>
              <div className="result-tag"><span className="pulse">●</span> 신선한 분석</div>
            </div>
            <div className="ranking-list">
              <div className="rank-item">
                <div className="rank-badge r1">1st</div>
                <div className="rank-info">
                  <div className="rank-company">카카오엔터프라이즈</div>
                  <div className="rank-job">AI 백엔드 개발자 · 신입/주니어</div>
                </div>
                <div className="rank-score-wrap">
                  <div className="rank-score s1">84<span style={{ fontSize: '16px', color: 'var(--muted)' }}>점</span></div>
                  <div className="rank-bar-wrap"><div className="rank-bar b1" style={{ width: '84%' }}></div></div>
                </div>
              </div>
              <div className="rank-item">
                <div className="rank-badge r2">2nd</div>
                <div className="rank-info">
                  <div className="rank-company">네이버 클라우드</div>
                  <div className="rank-job">LLM/RAG 서비스 개발 · 신입</div>
                </div>
                <div className="rank-score-wrap">
                  <div className="rank-score s2">76<span style={{ fontSize: '16px', color: 'var(--muted)' }}>점</span></div>
                  <div className="rank-bar-wrap"><div className="rank-bar b2" style={{ width: '76%' }}></div></div>
                </div>
              </div>
              <div className="rank-item">
                <div className="rank-badge r3">3rd</div>
                <div className="rank-info">
                  <div className="rank-company">라인플러스</div>
                  <div className="rank-job">백엔드 서버 개발 · 신입</div>
                </div>
                <div className="rank-score-wrap">
                  <div className="rank-score s3">61<span style={{ fontSize: '16px', color: 'var(--muted)' }}>점</span></div>
                  <div className="rank-bar-wrap"><div className="rank-bar b3" style={{ width: '61%' }}></div></div>
                </div>
              </div>
            </div>
          </div>

          {/* Job-by-job detail */}
          <div className="card fade-up fade-up-d1">
            <div style={{ marginBottom: '16px' }}>
              <div className="tag" style={{ marginBottom: '12px' }}>공고별 상세 분석</div>
            </div>
            <div className="job-tabs">
              <button className={`job-tab ${activeTab === 0 ? 'active' : ''}`} onClick={() => setActiveTab(0)}>🟢 카카오엔터프라이즈</button>
              <button className={`job-tab ${activeTab === 1 ? 'active' : ''}`} onClick={() => setActiveTab(1)}>🟡 네이버 클라우드</button>
              <button className={`job-tab ${activeTab === 2 ? 'active' : ''}`} onClick={() => setActiveTab(2)}>⚪ 라인플러스</button>
            </div>

            {/* Panel 0: Kakao Enterprise */}
            {activeTab === 0 && (
              <div className="detail-panel active">
                <span className="sub-label">✅ 강점</span>
                <div className="strength-list">
                  <div className="strength-item">
                    <div className="strength-icon">💪</div>
                    <div className="strength-text">A*STAR IHPC 인턴십에서 Python 기반 RAG 시스템을 실제로 설계·구현한 경험이 공고 핵심 요구사항과 직접 매칭됩니다.</div>
                  </div>
                  <div className="strength-item">
                    <div className="strength-icon">💪</div>
                    <div className="strength-text">Hybrid Retrieval (Dense + BM25) + RRF + LLM Reranking 파이프라인 경험 — 업계 수준의 RAG 최적화 이해도를 보여줍니다.</div>
                  </div>
                  <div className="strength-item">
                    <div className="strength-icon">💪</div>
                    <div className="strength-text">CareerChat 프로젝트의 Spring Boot + FastAPI + LangGraph 조합이 AI 백엔드 설계 역량을 입증합니다.</div>
                  </div>
                  <div className="strength-item">
                    <div className="strength-icon">💪</div>
                    <div className="strength-text">FinanceBench 기반 정량적 평가 경험 — AI 서비스 품질을 수치로 측정하는 능력은 신입 지원자 중 차별화 포인트입니다.</div>
                  </div>
                </div>
                <span className="sub-label">⚠️ 부족 역량 및 보완 방향</span>
                <div className="gap-list">
                  <div className="strength-item">
                    <div className="strength-icon">📌</div>
                    <div className="strength-text"><strong style={{ color: 'var(--yellow)' }}>대규모 트래픽 처리 경험</strong> — Redis/Celery 비동기 구조를 CareerChat에 적용했다면 실제 부하 테스트 결과를 함께 기재하면 좋습니다.</div>
                  </div>
                  <div className="strength-item">
                    <div className="strength-icon">📌</div>
                    <div className="strength-text"><strong style={{ color: 'var(--yellow)' }}>Kotlin / Java 미기재</strong> — 카카오 백엔드 코드베이스는 Kotlin 기반이 많습니다. Spring Boot와 함께 Kotlin 학습 이력을 추가하세요.</div>
                  </div>
                </div>
                <span className="sub-label">📝 이력서 강조 포인트</span>
                <div className="highlight-cards">
                  <div className="highlight-card">
                    <div className="highlight-card-title">강조할 경험</div>
                    <div className="highlight-card-body">Financial Document Analyzer에서의 chunking 전략 개선 → Hybrid Retrieval → Reranking 단계적 최적화 과정을 수치(정답률 변화 등)와 함께 서술하세요.</div>
                  </div>
                  <div className="highlight-card">
                    <div className="highlight-card-title">강조할 기술</div>
                    <div className="highlight-card-body">Python, LangGraph, FAISS/Qdrant, Celery, Spring Boot, PostgreSQL 순으로 배치하고, Groq API 활용 경험도 포함하세요.</div>
                  </div>
                </div>
              </div>
            )}

            {/* Panel 1: Naver Cloud - LLM/RAG */}
            {activeTab === 1 && (
              <div className="detail-panel active">
                <span className="sub-label">✅ 강점</span>
                <div className="strength-list">
                  <div className="strength-item">
                    <div className="strength-icon">💪</div>
                    <div className="strength-text">IHPC 인턴십의 RAG 파이프라인 구현 경험이 네이버 클라우드 CLOVA Studio 관련 포지션 요구사항과 높은 매칭률을 보입니다.</div>
                  </div>
                  <div className="strength-item">
                    <div className="strength-icon">💪</div>
                    <div className="strength-text">element-based chunking, metadata 설계, vector search 최적화 — 실무 수준의 RAG 엔지니어링 경험 보유.</div>
                  </div>
                  <div className="strength-item">
                    <div className="strength-icon">💪</div>
                    <div className="strength-text">Docker Compose 기반 배포 경험으로 개발~배포 전 과정 이해도를 보여줄 수 있습니다.</div>
                  </div>
                </div>
                <span className="sub-label">⚠️ 부족 역량 및 보완 방향</span>
                <div className="gap-list">
                  <div className="strength-item">
                    <div className="strength-icon">📌</div>
                    <div className="strength-text"><strong style={{ color: 'var(--yellow)' }}>클라우드 인프라 경험(AWS/NCP) 미기재</strong> — EC2 배포 경험이 있다면 반드시 이력서에 포함하세요.</div>
                  </div>
                  <div className="strength-item">
                    <div className="strength-icon">📌</div>
                    <div className="strength-text"><strong style={{ color: 'var(--yellow)' }}>OpenAI/HuggingFace API 활용 사례 구체화 필요</strong> — 어떤 모델로 어떤 태스크를 수행했는지 모델명과 함께 명시하세요.</div>
                  </div>
                </div>
                <span className="sub-label">📝 이력서 강조 포인트</span>
                <div className="highlight-cards">
                  <div className="highlight-card">
                    <div className="highlight-card-title">강조할 경험</div>
                    <div className="highlight-card-body">RAG 시스템에서 thread pool 병렬처리로 metadata generation 속도를 개선한 사례를 구체적 수치와 함께 작성하면 차별점이 됩니다.</div>
                  </div>
                  <div className="highlight-card">
                    <div className="highlight-card-title">강조할 기술</div>
                    <div className="highlight-card-body">sentence-transformers, FAISS/Qdrant, BM25, Groq API, LangGraph를 중심으로 LLM 서비스 설계 역량을 강조하세요.</div>
                  </div>
                </div>
              </div>
            )}

            {/* Panel 2: Line Plus - Backend */}
            {activeTab === 2 && (
              <div className="detail-panel active">
                <span className="sub-label">✅ 강점</span>
                <div className="strength-list">
                  <div className="strength-item">
                    <div className="strength-icon">💪</div>
                    <div className="strength-text">Spring Boot 기반 REST API 설계 경험(CareerChat)이 라인플러스 서버 개발 포지션과 매칭됩니다.</div>
                  </div>
                  <div className="strength-item">
                    <div className="strength-icon">💪</div>
                    <div className="strength-text">Docker Compose 기반 로컬/EC2 배포 경험으로 인프라 이해도를 보여줄 수 있습니다.</div>
                  </div>
                  <div className="strength-item">
                    <div className="strength-icon">💪</div>
                    <div className="strength-text">PostgreSQL 데이터 모델링(8개 테이블 설계)으로 DB 설계 역량 입증 가능.</div>
                  </div>
                </div>
                <span className="sub-label">⚠️ 부족 역량 및 보완 방향</span>
                <div className="gap-list">
                  <div className="strength-item">
                    <div className="strength-icon">📌</div>
                    <div className="strength-text"><strong style={{ color: 'var(--yellow)' }}>Java/Kotlin 프로덕션 경험 부족</strong> — Spring Boot를 사용했으나 Java/Kotlin을 이력서 기술 스택에 명시적으로 기재하세요.</div>
                  </div>
                  <div className="strength-item">
                    <div className="strength-icon">📌</div>
                    <div className="strength-text"><strong style={{ color: 'var(--yellow)' }}>대규모 동시 요청 처리 경험 미기재</strong> — Celery/Redis 비동기 구조 설계 경험을 처리량 관점에서 서술하면 좋습니다.</div>
                  </div>
                </div>
                <span className="sub-label">📝 이력서 강조 포인트</span>
                <div className="highlight-cards">
                  <div className="highlight-card">
                    <div className="highlight-card-title">강조할 프로젝트</div>
                    <div className="highlight-card-body">CareerChat의 백엔드 API 설계(인증, 프로필 관리, 진단 요청) 구조와 비동기 처리 아키텍처를 명확히 기술하세요.</div>
                  </div>
                  <div className="highlight-card">
                    <div className="highlight-card-title">보완 제안</div>
                    <div className="highlight-card-body">라인플러스는 글로벌 서비스 경험을 중시합니다. OPIc IH 어학 성적을 이력서 상단에 배치해 글로벌 협업 역량을 어필하세요.</div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div style={{ marginTop: '16px', textAlign: 'center', padding: '20px 0' }}>
            <button className="btn btn-outline" onClick={() => navigate('/analyze')}>새 진단 시작하기</button>
          </div>
        </div>

        {/* Chat sidebar */}
        <div className="chat-panel">
          <div className="chat-header">
            <div className="chat-dot"></div>
            <div>
              <div className="chat-title">AI 어시스턴트</div>
              <div className="chat-subtitle">결과 기반 Q&A</div>
            </div>
          </div>
          <div className="chat-messages" id="chat-messages">
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`msg msg-${msg.role}`}>
                {msg.text}
                <div className="msg-time">{msg.time}</div>
              </div>
            ))}
          </div>
          <div className="chat-quick" style={{ display: chatMessages.length <= 1 ? 'flex' : 'none' }}>
            <button className="quick-btn" onClick={() => handleSendChat('카카오엔터프라이즈 합격 가능성은?')}>카카오 합격 가능성은?</button>
            <button className="quick-btn" onClick={() => handleSendChat('RAG 경험 어떻게 강조할까?')}>RAG 경험 강조 방법</button>
            <button className="quick-btn" onClick={() => handleSendChat('어떤 공고 먼저 지원할까?')}>지원 순서 추천</button>
          </div>
          <div className="chat-input-wrap">
            <textarea 
              className="chat-input" 
              placeholder="질문을 입력하세요..." 
              rows="1"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if(e.key === 'Enter' && !e.shiftKey) {
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
