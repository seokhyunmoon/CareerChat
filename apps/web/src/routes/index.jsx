import { createBrowserRouter } from 'react-router-dom';
import RootLayout from '@/layouts/RootLayout';
import Home from '@/pages/Home';
import Login from '@/pages/Login';
import Signup from '@/pages/Signup';
import Result from '@/pages/Result';
import MyInfo from '@/pages/MyInfo';
import Analyze from '@/pages/Analyze';
import History from '@/pages/History';
import NotFound from '@/pages/NotFound';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <NotFound />,
    children: [
      { index: true, element: <Home /> },
      { path: 'result', element: <Result /> },
      { path: 'myinfo', element: <MyInfo /> },
      { path: 'analyze', element: <Analyze /> },
      { path: 'history', element: <History /> },
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
