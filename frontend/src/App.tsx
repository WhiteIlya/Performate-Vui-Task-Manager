import { FC } from 'react';
import './App.css'
import { AuthProvider } from './context/Authcontext';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Navbar } from './shared/Navbar';
import { MainPage } from './pages/MainPage';
import { ToastContainer } from 'react-toastify';
import { Notifications } from './pages/Notifications';

export const App: FC = () => {
  return (
    <AuthProvider>
        <Router>
            <Navbar />
            <ToastContainer />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/chat" element={<MainPage />} />
              <Route path="/notifications" element={<Notifications />} />
              {/* <Route path="/register" element={<Register />} /> */}
            </Routes>
        </Router>
      </AuthProvider>
  );
};
