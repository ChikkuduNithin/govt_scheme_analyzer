import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { Lock, Mail } from 'lucide-react';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const res = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      // In a real app we'd decode JWT or fetch /me. Hardcoding is_admin false for demo unless admin@...
      const userData = { id: 1, email, is_admin: email.includes('admin') };
      login(res.data.access_token, userData);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold text-center text-blue-600 mb-6">Govt Scheme Analyzer</h2>
        {error && <div className="bg-red-50 text-red-500 p-3 mb-4 rounded">{error}</div>}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <div className="mt-1 relative">
              <Mail className="absolute left-3 top-3 text-gray-400 w-5 h-5" />
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} 
                className="pl-10 w-full border border-gray-300 rounded p-2 focus:ring-blue-500 focus:border-blue-500" required />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <div className="mt-1 relative">
              <Lock className="absolute left-3 top-3 text-gray-400 w-5 h-5" />
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} 
                className="pl-10 w-full border border-gray-300 rounded p-2 focus:ring-blue-500 focus:border-blue-500" required />
            </div>
          </div>
          <button type="submit" className="w-full bg-blue-600 text-white rounded p-2 hover:bg-blue-700 transition">
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
};
