import { Navigate, createBrowserRouter } from 'react-router-dom';
import RootLayout from '@/layouts/RootLayout';
import Home from '@/pages/Home';
import Login from '@/pages/Login';
import Signup from '@/pages/Signup';
import Result from '@/pages/Result';
import MyInfo from '@/pages/MyInfo';
import Analyze from '@/pages/Analyze';
import History from '@/pages/History';
import NotFound from '@/pages/NotFound';
import RequireAuth from '@/routes/RequireAuth';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <NotFound />,
    children: [
      { index: true, element: <Home /> },
      { path: 'result', element: <Navigate to="/result/1001" replace /> },
      { path: 'result/:diagnosisId', element: <Result /> },
      { path: 'myinfo', element: <RequireAuth><MyInfo /></RequireAuth> },
      { path: 'analyze', element: <RequireAuth><Analyze /></RequireAuth> },
      { path: 'history', element: <RequireAuth><History /></RequireAuth> },
    ],
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/signup',
    element: <Signup />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);
