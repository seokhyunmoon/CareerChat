import { useNavigate, useOutletContext } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();
  const { isLoggedIn } = useOutletContext();

  const startDiagnose = () => {
    if (!isLoggedIn) {
      navigate('/login');
    } else {
      navigate('/analyze');
    }
  };

  return (
    <div id="page-landing" className="page active">
      {/* Hero */}
      <section className="hero" style={{ padding: 0 }}>
        <div className="hero-grid-bg"></div>
        <div className="hero-glow"></div>
        <div className="container" style={{ width: '100%' }}>
          <div className="hero-content">
            <div className="hero-eyebrow fade-up">
              <div className="hero-line"></div>
              <span className="tag">AI 커리어 진단 서비스</span>
            </div>
            <h1 className="hero-title fade-up fade-up-d1">
              지원할 공고,<br />
              <em>정말 맞는지</em><br />
              알아보세요.
            </h1>
            <p className="hero-sub fade-up fade-up-d2">
              내 이력서를 최대 3개 채용공고와 비교해<br />
              적합도 분석, 강점·보완점, 우선순위를 한번에 파악합니다.
            </p>
            <div className="hero-cta fade-up fade-up-d3">
              <button className="btn btn-primary" onClick={startDiagnose}>
                <span>무료로 진단하기</span>
                <span>→</span>
              </button>
              <span className="hero-note">회원가입 무료 · 언제든지 재진단 가능</span>
            </div>
          </div>
          <div className="stats-row fade-up fade-up-d4">
            <div className="stat-cell">
              <div className="stat-num">3개</div>
              <div className="stat-label">채용공고 동시 비교 분석</div>
            </div>
            <div className="stat-cell">
              <div className="stat-num">AI</div>
              <div className="stat-label">GPT 기반 적합도 리포트</div>
            </div>
            <div className="stat-cell">
              <div className="stat-num">1:1</div>
              <div className="stat-label">결과 기반 챗봇 Q&A</div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="how">
        <div className="container">
          <div className="how-header">
            <div>
              <div className="tag" style={{ marginBottom: '16px' }}>HOW IT WORKS</div>
              <h2 className="section-title">4단계로 완성하는<br />커리어 진단</h2>
            </div>
            <p style={{ color: 'var(--muted)', fontSize: '14px', maxWidth: '280px', lineHeight: 1.7 }}>
              복잡한 설정 없이 내 정보를 한 번만 저장하면 언제든 재활용 가능합니다.
            </p>
          </div>
          <div className="steps-grid">
            <div className="step-cell">
              <div className="step-num">STEP 01</div>
              <div className="step-icon">👤</div>
              <div className="step-title">내 정보 저장</div>
              <div className="step-desc">학력, 경력, 프로젝트, 기술스택을 한번 입력해두면 매번 다시 쓸 필요가 없어요.</div>
            </div>
            <div className="step-cell">
              <div className="step-num">STEP 02</div>
              <div className="step-icon">📋</div>
              <div className="step-title">공고 붙여넣기</div>
              <div className="step-desc">채용공고 전문 또는 URL을 최대 3개까지 입력하세요. 복사-붙여넣기로 충분합니다.</div>
            </div>
            <div className="step-cell">
              <div className="step-num">STEP 03</div>
              <div className="step-icon">🔍</div>
              <div className="step-title">AI 분석 실행</div>
              <div className="step-desc">공고별 적합도, 강점·부족 역량, 지원 우선순위를 자동으로 분석합니다.</div>
            </div>
            <div className="step-cell">
              <div className="step-num">STEP 04</div>
              <div className="step-icon">💬</div>
              <div className="step-title">리포트 & 챗봇</div>
              <div className="step-desc">결과 리포트를 보며 챗봇에게 추가 질문을 해보세요. 근거 기반으로 답변합니다.</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA band */}
      <div className="container">
        <div className="cta-band">
          <h2>지금 바로 내 이력서의<br /><em>강점과 약점을 파악</em>하세요.</h2>
          <button className="btn btn-primary" style={{ fontSize: '15px', padding: '16px 40px' }} onClick={startDiagnose}>
            진단 시작하기 →
          </button>
        </div>
      </div>
    </div>
  );
}
