import { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';

const DEMO_USER = { name: '문석현' };

export default function RootLayout() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(true); 
  
  const handleLogout = () => {
    setIsLoggedIn(false);
    navigate('/');
  };

  return (
    <div className="root-layout">
      <Navbar isLoggedIn={isLoggedIn} user={DEMO_USER} onLogout={handleLogout} />
      <Outlet context={{ isLoggedIn }} />
      <Footer />
    </div>
  );
}
