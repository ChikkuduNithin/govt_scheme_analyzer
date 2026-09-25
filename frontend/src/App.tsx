import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Analyze } from './pages/Analyze';
import { Admin } from './pages/Admin';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token')
  return token ? <>{children}</> : <Navigate to="/login" />
}

function Navigation() {
  const navigate = useNavigate()
  
  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }
  
  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-8">
            <h1 className="text-xl font-bold text-blue-600">GovSchemeAI</h1>
            <div className="flex items-center gap-4">
              <Link to="/" className="text-gray-600 hover:text-gray-900 font-medium">Dashboard</Link>
              <Link to="/analyze" className="text-gray-600 hover:text-gray-900 font-medium">Analyze</Link>
              <Link to="/admin" className="text-gray-600 hover:text-gray-900 font-medium">Admin</Link>
            </div>
          </div>
          <div className="flex items-center">
            <button onClick={handleLogout} className="text-gray-500 hover:text-gray-700 font-medium">Logout</button>
          </div>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={
              <PrivateRoute>
                <Navigation />
                <Dashboard />
              </PrivateRoute>
            } />
            <Route path="/analyze" element={
              <PrivateRoute>
                <Navigation />
                <Analyze />
              </PrivateRoute>
            } />
            <Route path="/admin" element={
              <PrivateRoute>
                <Navigation />
                <Admin />
              </PrivateRoute>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
