import { Navigate, useOutletContext } from 'react-router-dom';

export default function RequireAuth({ children }) {
  const { isLoggedIn, isAuthLoading } = useOutletContext();

  if (isAuthLoading) {
    return null;
  }

  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
