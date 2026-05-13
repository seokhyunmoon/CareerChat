import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
  const navigate = useNavigate();

  const doLogin = () => {
    // Demo: any click logs in
    navigate('/myinfo');
  };

  return (
    <div id="page-auth" className="page active" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <div className="auth-wrap fade-up">
        <div className="auth-logo">CareerChat</div>
        <div className="auth-sub">다시 만나서 반가워요 👋</div>
        <div className="auth-tabs">
          <button className="auth-tab active">로그인</button>
          <Link to="/signup" className="auth-tab" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>회원가입</Link>
        </div>

        {/* Login form */}
        <div id="form-login">
          <div className="auth-form">
            <div className="field">
              <label>이메일</label>
              <input type="email" id="login-email" placeholder="example@email.com" />
            </div>
            <div className="field">
              <label>비밀번호</label>
              <input type="password" id="login-pw" placeholder="비밀번호 입력" />
            </div>
            <div className="form-error" id="login-error">이메일 또는 비밀번호가 올바르지 않습니다.</div>
            <button className="btn btn-primary btn-full" onClick={doLogin}>로그인</button>
          </div>
          <div className="auth-divider" style={{ marginTop: '20px' }}>또는</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
            <button className="btn-social">
              <svg width="18" height="18" viewBox="0 0 18 18"><path fill="#4285F4" d="M17.64 9.2c0-.638-.057-1.252-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"/><path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"/><path fill="#FBBC05" d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z"/><path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"/></svg>
              Google로 계속하기
            </button>
            <button className="btn-social">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="#3C1E1E"><path d="M9 1.5C4.86 1.5 1.5 4.134 1.5 7.38c0 2.088 1.35 3.918 3.384 4.986L4.05 15.3c-.06.216.15.39.342.27l3.582-2.37c.33.042.666.066 1.026.066C12.906 13.266 16.5 10.632 16.5 7.38 16.5 4.134 13.14 1.5 9 1.5z"/></svg>
              Kakao로 계속하기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
