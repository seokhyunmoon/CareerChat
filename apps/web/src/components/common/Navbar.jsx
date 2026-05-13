import { Link, useNavigate, useLocation } from 'react-router-dom';

export default function Navbar({ isLoggedIn, user, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();

  const getLinkStyle = (path) => {
    const isActive = location.pathname === path;
    return isActive 
      ? { color: 'var(--green)', borderColor: 'rgba(74,222,128,0.2)' }
      : {};
  };

  return (
    <nav>
      <div className="nav-logo" onClick={() => navigate('/')}>Career<span>Chat</span></div>
      <div className="nav-links">
        {isLoggedIn ? (
          <>
            <div className="nav-user show">
              <div 
                className="nav-profile-link" 
                onClick={() => navigate('/myinfo')}
                style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
              >
                <div 
                  className="nav-avatar" 
                  style={location.pathname === '/myinfo' ? { borderColor: 'var(--green)', background: 'var(--green-dim)' } : {}}
                >
                  {user?.name?.[0]}
                </div>
                <span 
                  className="nav-name" 
                  style={location.pathname === '/myinfo' ? { color: 'var(--text)', fontWeight: '600' } : {}}
                >
                  {user?.name}
                </span>
              </div>
              <button className="nav-logout" onClick={onLogout}>로그아웃</button>
            </div>
            <Link to="/analyze" className="nav-btn" style={getLinkStyle('/analyze')}>진단하기</Link>
            <Link to="/history" className="nav-btn" style={getLinkStyle('/history')}>진단 기록</Link>
          </>
        ) : (
          <div className="flex gap-2" id="nav-auth-btns">
            <Link to="/login" className="nav-btn">로그인</Link>
            <Link to="/login" className="nav-btn primary">시작하기</Link>
          </div>
        )}
      </div>
    </nav>
  );
}
