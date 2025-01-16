import { FC } from 'react';
import './App.css'
import { AuthProvider } from './context/Authcontext';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import { Home } from './pages/Home';
import { Login } from './pages/Login';

export const App: FC = () => {
  return (
    <AuthProvider>
        <Router>
            {/* <Navbar /> */}
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              {/* <Route path="/register" element={<Register />} /> */}
            </Routes>
        </Router>
      </AuthProvider>
  );
};
