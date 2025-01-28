
// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
//import LoginForm from './components/LoginForm';
//import VerifyOtpForm from './components/VerifyOtpForm';
import Dashboard from './components/Dashboard';
//import VerifyBackupForm from './components/VerifyBackupForm';
//import GenerateQrCode from './components/GenerateQrCode';
//import PrivateRoute from './components/PrivateRoute';
//import PublicRoute from './components/PublicRoute';
import Logout from './components/Logout';
import AuthFlow from './components/AuthFlow';
//import RestrictedRoute from './components/RestrictedRoute';

function App() {
  return (
    <Router>
      <Routes>
      <Route path="/" element={<AuthFlow />} />
      <Route path="/login" element={<AuthFlow />} />
        <Route path="/dashboard" element={<Dashboard />}/>
        <Route path="/logout" element={<Logout />} />
      </Routes>
    </Router>
  );
}

export default App;
