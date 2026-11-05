import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Analyze } from './pages/Analyze';
import { Admin } from './pages/Admin';
import { Landmark, LogOut, LayoutDashboard, Search, ShieldCheck } from 'lucide-react';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  return token ? <>{children}</> : <Navigate to="/login" />;
}

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };
  
  const isActive = (path: string) => {
    if (path === '/' && (location.pathname === '/' || location.pathname === '/dashboard')) return true;
    return location.pathname === path;
  };

  return (
    <nav className="bg-white/95 backdrop-blur-md sticky top-0 z-50 border-b border-slate-200 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          
          {/* Logo & Brand */}
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-sm shadow-blue-200 group-hover:scale-105 transition-transform">
                <Landmark className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-1.5 font-extrabold text-slate-900 tracking-tight text-lg">
                  <span>GovScheme</span>
                  <span className="text-blue-600">AI</span>
                </div>
                <div className="text-[10px] font-bold text-slate-400 tracking-wider uppercase -mt-1 flex items-center gap-1">
                  <span>Multi-Agent RAG</span>
                </div>
              </div>
            </Link>

            {/* Navigation Links */}
            <div className="hidden sm:flex items-center gap-1.5">
              <Link 
                to="/" 
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition ${
                  isActive('/') 
                    ? 'bg-blue-50 text-blue-700 shadow-2xs' 
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <LayoutDashboard className="w-3.5 h-3.5" />
                <span>Dashboard</span>
              </Link>
              <Link 
                to="/analyze" 
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition ${
                  isActive('/analyze') 
                    ? 'bg-blue-50 text-blue-700 shadow-2xs' 
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Search className="w-3.5 h-3.5" />
                <span>AI Analyze</span>
              </Link>
              <Link 
                to="/admin" 
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition ${
                  isActive('/admin') 
                    ? 'bg-blue-50 text-blue-700 shadow-2xs' 
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Admin & Rules</span>
              </Link>
            </div>
          </div>

          {/* Right Action: Logout */}
          <div className="flex items-center gap-3">
            <button 
              onClick={handleLogout} 
              className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-rose-600 px-3 py-1.5 rounded-xl border border-slate-200 hover:border-rose-200 hover:bg-rose-50/50 transition"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-slate-50">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<Navigate to="/" replace />} />
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
