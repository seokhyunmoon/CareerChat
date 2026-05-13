import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import RootLayout from './layouts/RootLayout';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Result from './pages/Result';
import MyInfo from './pages/MyInfo';
import Analyze from './pages/Analyze';
import History from './pages/History';

const router = createBrowserRouter([
  // 1. Header/Footer가 필요한 페이지들
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'result', element: <Result /> },
      { path: 'myinfo', element: <MyInfo /> },
      { path: 'analyze', element: <Analyze /> },
      { path: 'history', element: <History /> },
    ],
  },
  // 2. Header/Footer가 필요 없는 페이지들 (RootLayout 밖으로 이동)
  {
    path: 'login',
    element: <Login />,
  },
  {
    path: 'signup',
    element: <Signup />,
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
