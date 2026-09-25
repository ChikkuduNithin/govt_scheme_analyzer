import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<any>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [saveStatus, setSaveStatus] = useState('');

  useEffect(() => {
    api.get('/profile/').then(res => setProfile(res.data)).catch(console.error);
  }, []);

  const updateField = (field: string, value: string | boolean) => {
    setProfile((current: any) => ({ ...current, [field]: value }));
  };

  const saveProfile = async () => {
    setSaveStatus('Saving...');
    const payload = {
      ...profile,
      annual_income: profile?.annual_income ? Number(profile.annual_income) : null,
    };

    try {
      const res = await api.put('/profile/', payload);
      setProfile(res.data);
      setIsEditing(false);
      setSaveStatus('Profile saved.');
    } catch (err) {
      setSaveStatus('Could not save profile.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-blue-600">Govt Scheme Analyzer</h1>
        <div className="flex gap-4">
          <span className="text-gray-600">Welcome, {user?.email}</span>
          <button onClick={() => { logout(); navigate('/'); }} className="text-red-500 hover:underline">Logout</button>
        </div>
      </nav>
      
      <main className="max-w-4xl mx-auto p-6 space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-start justify-between gap-4 mb-4">
            <div>
              <h2 className="text-2xl font-bold">Your Profile</h2>
              <p className="text-sm text-gray-500 mt-1">This information is used to check scheme eligibility.</p>
            </div>
            <button onClick={() => setIsEditing(!isEditing)} className="text-blue-600 hover:underline text-sm font-medium">
              {isEditing ? 'Cancel' : 'Update Profile'}
            </button>
          </div>
          {profile ? (
            isEditing ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <label className="space-y-1">
                  <span className="font-semibold">Full name</span>
                  <input className="w-full border border-gray-300 rounded p-2" value={profile.full_name || ''} onChange={e => updateField('full_name', e.target.value)} />
                </label>
                <label className="space-y-1">
                  <span className="font-semibold">Date of birth</span>
                  <input type="date" className="w-full border border-gray-300 rounded p-2" value={profile.date_of_birth || ''} onChange={e => updateField('date_of_birth', e.target.value)} />
                </label>
                <label className="space-y-1">
                  <span className="font-semibold">State</span>
                  <input className="w-full border border-gray-300 rounded p-2" value={profile.state || ''} onChange={e => updateField('state', e.target.value)} />
                </label>
                <label className="space-y-1">
                  <span className="font-semibold">District</span>
                  <input className="w-full border border-gray-300 rounded p-2" value={profile.district || ''} onChange={e => updateField('district', e.target.value)} />
                </label>
                <label className="space-y-1">
                  <span className="font-semibold">Annual income</span>
                  <input type="number" className="w-full border border-gray-300 rounded p-2" value={profile.annual_income || ''} onChange={e => updateField('annual_income', e.target.value)} />
                </label>
                <label className="space-y-1">
                  <span className="font-semibold">Category</span>
                  <select className="w-full border border-gray-300 rounded p-2" value={profile.category || ''} onChange={e => updateField('category', e.target.value)}>
                    <option value="">Select category</option>
                    <option>General</option>
                    <option>OBC</option>
                    <option>SC</option>
                    <option>ST</option>
                  </select>
                </label>
                <label className="space-y-1">
                  <span className="font-semibold">Employment status</span>
                  <select className="w-full border border-gray-300 rounded p-2" value={profile.employment_status || ''} onChange={e => updateField('employment_status', e.target.value)}>
                    <option value="">Select status</option>
                    <option>Unemployed</option>
                    <option>Employed</option>
                    <option>Self-employed</option>
                    <option>Student</option>
                  </select>
                </label>
                <label className="space-y-1">
                  <span className="font-semibold">Education level</span>
                  <input className="w-full border border-gray-300 rounded p-2" value={profile.education_level || ''} onChange={e => updateField('education_level', e.target.value)} />
                </label>
                <label className="flex items-center gap-2 md:col-span-2">
                  <input type="checkbox" checked={!!profile.disability_status} onChange={e => updateField('disability_status', e.target.checked)} />
                  <span className="font-semibold">Person with disability</span>
                </label>
                <div className="md:col-span-2 flex items-center gap-3">
                  <button onClick={saveProfile} className="bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700">Save Profile</button>
                  {saveStatus && <span className="text-sm text-gray-600">{saveStatus}</span>}
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div><span className="font-semibold">Name:</span> {profile.full_name || 'Not set'}</div>
                <div><span className="font-semibold">Date of birth:</span> {profile.date_of_birth || 'Not set'}</div>
                <div><span className="font-semibold">State:</span> {profile.state || 'Not set'}</div>
                <div><span className="font-semibold">District:</span> {profile.district || 'Not set'}</div>
                <div><span className="font-semibold">Income:</span> Rs. {profile.annual_income || 0}</div>
                <div><span className="font-semibold">Category:</span> {profile.category || 'Not set'}</div>
                <div><span className="font-semibold">Employment:</span> {profile.employment_status || 'Not set'}</div>
                <div><span className="font-semibold">Education:</span> {profile.education_level || 'Not set'}</div>
              </div>
            )
          ) : (
            <p>Loading profile...</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6 text-center py-12">
          <h3 className="text-xl font-bold mb-2">Find Schemes You Are Eligible For</h3>
          <p className="text-gray-600 mb-6">Ask our AI to analyze your profile against government databases.</p>
          <button onClick={() => navigate('/analyze')} className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 shadow transition">
            Start Analysis
          </button>
        </div>
      </main>
    </div>
  );
};
