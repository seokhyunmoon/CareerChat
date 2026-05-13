import { useNavigate, Link } from 'react-router-dom';

export default function Signup() {
  const navigate = useNavigate();

  const doSignup = () => {
    // Demo logic
    navigate('/myinfo');
  };

  return (
    <div id="page-auth" className="page active" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <div className="auth-wrap fade-up">
        <div className="auth-logo">CareerChat</div>
        <div className="auth-sub">커리어 진단을 시작해볼까요? 🚀</div>
        <div className="auth-tabs">
          <Link to="/login" className="auth-tab" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>로그인</Link>
          <button className="auth-tab active">회원가입</button>
        </div>

        {/* Signup form */}
        <div id="form-signup">
          <div className="auth-form">
            <div className="field">
              <label>이름</label>
              <input type="text" id="signup-name" placeholder="홍길동" />
            </div>
            <div className="field">
              <label>이메일</label>
              <input type="email" id="signup-email" placeholder="example@email.com" />
            </div>
            <div className="field">
              <label>비밀번호</label>
              <input type="password" id="signup-pw" placeholder="8자 이상 입력" />
            </div>
            <div className="field">
              <label>비밀번호 확인</label>
              <input type="password" id="signup-pw2" placeholder="비밀번호 재입력" />
            </div>
            <div className="form-error" id="signup-error">비밀번호가 일치하지 않습니다.</div>
            <button className="btn btn-primary btn-full" onClick={doSignup}>가입하기</button>
          </div>
        </div>
      </div>
    </div>
  );
}
