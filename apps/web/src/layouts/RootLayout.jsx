import { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';

export default function RootLayout() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(true); 
  const [user, setUser] = useState({ name: '문석현' });
  
  const handleLogout = () => {
    setIsLoggedIn(false);
    navigate('/');
  };

  return (
    <div className="root-layout">
      <Navbar isLoggedIn={isLoggedIn} user={user} onLogout={handleLogout} />
      <Outlet context={{ isLoggedIn }} />
      <Footer />
    </div>
  );
}
