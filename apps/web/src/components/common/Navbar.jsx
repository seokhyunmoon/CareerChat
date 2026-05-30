import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

export default function Navbar({ isLoggedIn, user, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);

  useEffect(() => {
    const closeUserMenu = (event) => {
      if (!userMenuRef.current?.contains(event.target)) {
        setIsUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', closeUserMenu);
    return () => document.removeEventListener('mousedown', closeUserMenu);
  }, []);

  const isActivePath = (path) => location.pathname === path;

  const handleLogout = () => {
    setIsUserMenuOpen(false);
    onLogout();
  };

  const displayName = user?.name || '사용자';
  const avatarText = displayName.trim().charAt(0) || '?';

  return (
    <nav>
      <div className="nav-inner">
        <div className="nav-left">
          <div className="nav-logo" onClick={() => navigate('/')}>Career<span>Chat</span></div>
          {isLoggedIn && (
            <div className="nav-main-links">
              <Link to="/analyze" className={`nav-text-link ${isActivePath('/analyze') ? 'active' : ''}`}>이력서 진단</Link>
              <Link to="/history" className={`nav-text-link ${isActivePath('/history') ? 'active' : ''}`}>진단 기록</Link>
            </div>
          )}
        </div>
        <div className="nav-links">
          {isLoggedIn ? (
            <div className="nav-user" ref={userMenuRef}>
              <button
                type="button"
                className={`nav-profile-trigger ${isUserMenuOpen ? 'open' : ''}`}
                onClick={() => setIsUserMenuOpen((prev) => !prev)}
                aria-expanded={isUserMenuOpen}
                aria-haspopup="menu"
              >
                <div
                  className="nav-avatar"
                  data-active={isActivePath('/myinfo')}
                >
                  {avatarText}
                </div>
                <span className="nav-name">{displayName}</span>
                <span className="nav-chevron">⌄</span>
              </button>
              {isUserMenuOpen && (
                <div className="nav-user-menu" role="menu">
                  <button type="button" role="menuitem" onClick={() => navigate('/myinfo')}>마이페이지</button>
                  <button type="button" role="menuitem" className="danger" onClick={handleLogout}>로그아웃</button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex gap-2" id="nav-auth-btns">
              <Link to="/login" className="nav-btn">로그인</Link>
              <Link to="/login" className="nav-btn primary">시작하기</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
