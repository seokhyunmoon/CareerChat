import { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import { getMe } from '../features/auth/api/authApi';
import { getAccessToken, removeAccessToken } from '@/features/auth/tokenStorage';

export default function RootLayout() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  const isLoggedIn = Boolean(user);

  useEffect(() => {
    const restoreAuth = async () => {
      const accessToken = getAccessToken();

      if (!accessToken) {
        setIsAuthLoading(false);
        return;
      }
      try {
        const currentUser = await getMe();
        setUser(currentUser);
      } catch {
        removeAccessToken();
        setUser(null);
      } finally {
        setIsAuthLoading(false);
      }
    };

    restoreAuth();
  }, []);
  
  const handleLogout = () => {
    removeAccessToken();
    setUser(null);
    navigate('/');
  };

  return (
    <div className="root-layout">
      <Navbar isLoggedIn={isLoggedIn} user={user} onLogout={handleLogout} />
      <Outlet context={{ isLoggedIn, user, isAuthLoading }} />
      <Footer />
    </div>
  );
}
