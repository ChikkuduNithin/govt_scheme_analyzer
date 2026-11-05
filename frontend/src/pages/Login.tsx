import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { Lock, Mail, UserPlus, LogIn } from 'lucide-react';

export const Login: React.FC = () => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (isRegister) {
      try {
        await api.post('/auth/register', {
          email,
          password
        });
        setSuccess('Registration successful! Signing you in...');
        // Auto-login after registration
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        const res = await api.post('/auth/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        const userData = { id: 1, email, is_admin: email.toLowerCase().includes('admin') };
        login(res.data.access_token, userData);
        navigate('/');
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Registration failed. Try a different email.');
      }
    } else {
      try {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const res = await api.post('/auth/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        
        const userData = { id: 1, email, is_admin: email.toLowerCase().includes('admin') };
        login(res.data.access_token, userData);
        navigate('/');
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Invalid email or password.');
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 w-full max-w-md">
        <h2 className="text-2xl font-bold text-center text-blue-600 mb-2">Govt Scheme Analyzer</h2>
        <p className="text-xs text-center text-gray-500 mb-6">Agentic RAG & Deterministic Eligibility Verification</p>
        
        <div className="flex border-b border-gray-200 mb-6">
          <button 
            type="button"
            onClick={() => { setIsRegister(false); setError(''); setSuccess(''); }}
            className={`flex-1 py-2 text-sm font-semibold border-b-2 text-center transition ${!isRegister ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-400 hover:text-gray-600'}`}
          >
            <span className="flex items-center justify-center gap-1.5"><LogIn className="w-4 h-4"/> Sign In</span>
          </button>
          <button 
            type="button"
            onClick={() => { setIsRegister(true); setError(''); setSuccess(''); }}
            className={`flex-1 py-2 text-sm font-semibold border-b-2 text-center transition ${isRegister ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-400 hover:text-gray-600'}`}
          >
            <span className="flex items-center justify-center gap-1.5"><UserPlus className="w-4 h-4"/> Create Account</span>
          </button>
        </div>

        {error && <div className="bg-rose-50 border border-rose-200 text-rose-600 text-xs p-3 mb-4 rounded-lg">{error}</div>}
        {success && <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs p-3 mb-4 rounded-lg">{success}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-2.5 text-gray-400 w-4 h-4" />
              <input 
                type="email" 
                value={email} 
                onChange={e => setEmail(e.target.value)} 
                className="pl-9 w-full border border-gray-300 rounded-lg p-2 text-sm focus:ring-blue-500 focus:border-blue-500" 
                placeholder="citizen@example.com"
                required 
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-2.5 text-gray-400 w-4 h-4" />
              <input 
                type="password" 
                value={password} 
                onChange={e => setPassword(e.target.value)} 
                className="pl-9 w-full border border-gray-300 rounded-lg p-2 text-sm focus:ring-blue-500 focus:border-blue-500" 
                placeholder="••••••••"
                required 
              />
            </div>
          </div>
          <button 
            type="submit" 
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg text-sm transition shadow-sm"
          >
            {isRegister ? 'Register & Continue' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-gray-100 text-center">
          <p className="text-xs text-gray-400">Demo test credentials: <code className="bg-gray-100 px-1 py-0.5 rounded text-gray-600">test@example.com / password123</code></p>
        </div>
      </div>
    </div>
  );
};
