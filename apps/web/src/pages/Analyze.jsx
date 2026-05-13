import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Analyze() {
  const navigate = useNavigate();
  const [jobCards, setJobCards] = useState([Date.now()]);
  const [isLoading, setIsLoading] = useState(false);

  const addJobCard = () => {
    if (jobCards.length >= 3) return;
    setJobCards([...jobCards, Date.now()]);
  };

  const removeJobCard = (id) => {
    setJobCards(jobCards.filter((cardId) => cardId !== id));
  };

  const runAnalysis = () => {
    if (jobCards.length === 0) {
      alert('공고를 최소 1개 이상 입력해주세요.');
      return;
    }
    setIsLoading(true);
    // Simulate loading
    setTimeout(() => {
      setIsLoading(false);
      navigate('/result');
    }, 3600);
  };

  return (
    <>
      <div id="page-diagnose" className="page active">
        <div className="diag-layout">
          {/* Main: job cards */}
          <div>
            <div className="jobs-header">
              <div>
                <div className="tag" style={{ marginBottom: '12px' }}>STEP 2 / 2</div>
                <div className="jobs-title">채용공고 입력</div>
              </div>
              <div className="jobs-count" id="jobs-count">
                {jobCards.length} / 3
              </div>
            </div>
            <div className="job-cards" id="job-cards">
              {jobCards.map((id, index) => (
                <div className="job-card" key={id}>
                  <div className="job-card-header">
                    <span className="job-card-num">공고 {String(index + 1).padStart(2, '0')}</span>
                    <button className="job-card-remove" onClick={() => removeJobCard(id)}>
                      ×
                    </button>
                  </div>
                  <div className="field" style={{ marginBottom: '12px' }}>
                    <label>회사명 / 공고명</label>
                    <input placeholder="예: 토스 Frontend Engineer" />
                  </div>
                  <div className="field">
                    <label>채용공고 내용 또는 URL</label>
                    <textarea
                      rows="6"
                      placeholder="채용공고 전문을 붙여넣거나 URL을 입력하세요.&#10;예: https://toss.im/career/...&#10;&#10;또는 공고 내용 전체를 그대로 붙여넣으세요."
                    ></textarea>
                  </div>
                </div>
              ))}
            </div>
            <button
              className={`add-job-btn ${jobCards.length >= 3 ? 'disabled' : ''}`}
              id="add-job-btn"
              onClick={addJobCard}
              disabled={jobCards.length >= 3}
            >
              <span style={{ fontSize: '20px' }}>＋</span>
              공고 추가 (최대 3개)
            </button>
            <div className="run-btn-wrap">
              <div className="run-btn-info">
                <strong>준비되셨나요?</strong>
                내 정보와 입력한 공고를 AI가 분석합니다. 약 10–20초 소요됩니다.
              </div>
              <button className="btn btn-primary" style={{ whiteSpace: 'nowrap' }} onClick={runAnalysis}>
                진단 시작 →
              </button>
            </div>
          </div>

          {/* Sidebar */}
          <div className="diag-sidebar">
            <div className="diag-profile-card">
              <div className="diag-profile-header">
                <div className="diag-profile-av">문</div>
                <div>
                  <div className="diag-profile-name">문석현</div>
                  <div className="diag-profile-badge">신입 · 응용정보공학</div>
                </div>
              </div>
              <div className="profile-chips">
                <span className="chip green">Python</span>
                <span className="chip green">RAG / LangGraph</span>
                <span className="chip green">Spring Boot</span>
                <span className="chip green">FastAPI</span>
                <span className="chip">PostgreSQL</span>
                <span className="chip">Next.js</span>
                <span className="chip">Docker</span>
                <span className="chip">FAISS / Qdrant</span>
              </div>
              <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--muted)' }}>내 정보 불러옴</span>
                <button className="btn btn-ghost" style={{ padding: '6px 14px', fontSize: '11px' }} onClick={() => navigate('/myinfo')}>
                  수정
                </button>
              </div>
            </div>
            <div className="diag-tip">
              <strong>💡 TIP</strong>
              공고 전문을 붙여넣을수록 더 정확한 분석이 가능합니다. URL 입력도 지원합니다.
            </div>
          </div>
        </div>
      </div>

      {/* LOADING OVERLAY */}
      {isLoading && (
        <div className="loading-overlay show">
          <div className="loading-logo">CareerChat</div>
          <div style={{ fontSize: '14px', color: 'var(--muted)', marginBottom: '8px', fontFamily: 'var(--mono)' }}>
            AI 분석 중...
          </div>
          <div className="loading-bar-wrap">
            <div className="loading-bar"></div>
          </div>
          <div className="loading-steps">
            <div className="loading-step done">공고 핵심 요소 추출 중</div>
            <div className="loading-step">프로필 데이터 매핑 중</div>
            <div className="loading-step">적합도 점수 계산 중</div>
            <div className="loading-step">보완 방향 생성 중</div>
          </div>
        </div>
      )}
    </>
  );
}
