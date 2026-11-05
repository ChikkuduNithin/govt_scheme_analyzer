import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { 
  User, 
  Calendar, 
  MapPin, 
  Wallet, 
  GraduationCap, 
  Briefcase, 
  Sparkles, 
  ArrowRight, 
  Edit3, 
  X,
  Building,
  Heart
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<any>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [saveStatus, setSaveStatus] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/profile/')
      .then(res => {
        setProfile(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const updateField = (field: string, value: string | boolean) => {
    setProfile((current: any) => ({ ...current, [field]: value }));
  };

  const saveProfile = async () => {
    setSaveStatus('Saving profile...');
    const payload = {
      ...profile,
      annual_income: profile?.annual_income ? Number(profile.annual_income) : null,
    };

    try {
      const res = await api.put('/profile/', payload);
      setProfile(res.data);
      setIsEditing(false);
      setSaveStatus('Profile updated successfully!');
      setTimeout(() => setSaveStatus(''), 3000);
    } catch (err) {
      setSaveStatus('Could not save profile.');
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-700 via-indigo-700 to-blue-900 text-white p-8 sm:p-10 shadow-lg shadow-blue-900/10">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/10 backdrop-blur-md text-blue-100 border border-white/20">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Citizen Portal • Verified Database Matcher</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Welcome, {profile?.full_name || user?.email?.split('@')[0] || 'Citizen'}
          </h2>
          <p className="text-blue-100 text-sm sm:text-base leading-relaxed">
            Your demographic profile allows our AI agents to verify official welfare eligibility rules deterministically without hallucinations.
          </p>
          <div className="pt-2">
            <button
              onClick={() => navigate('/analyze')}
              className="inline-flex items-center gap-2 bg-white text-blue-900 font-bold px-6 py-3 rounded-2xl shadow-md hover:bg-blue-50 transition transform hover:-translate-y-0.5 text-sm"
            >
              <span>Launch AI Scheme Analysis</span>
              <ArrowRight className="w-4 h-4 text-blue-700" />
            </button>
          </div>
        </div>
      </div>

      {/* Profile Section */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-6 sm:p-8 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <User className="w-5 h-5 text-blue-600" />
              <span>Demographic & Socio-Economic Profile</span>
            </h3>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              Used automatically as baseline data for state welfare schemes, pensions, and scholarships.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {saveStatus && (
              <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
                {saveStatus}
              </span>
            )}
            <button
              onClick={() => setIsEditing(!isEditing)}
              className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold border transition ${
                isEditing
                  ? 'bg-slate-100 text-slate-700 border-slate-300 hover:bg-slate-200'
                  : 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100'
              }`}
            >
              {isEditing ? (
                <>
                  <X className="w-3.5 h-3.5" />
                  <span>Cancel</span>
                </>
              ) : (
                <>
                  <Edit3 className="w-3.5 h-3.5" />
                  <span>Edit Profile</span>
                </>
              )}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400">Loading your profile...</div>
        ) : profile ? (
          <div className="p-6 sm:p-8">
            {isEditing ? (
              <form onSubmit={(e) => { e.preventDefault(); saveProfile(); }} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 text-xs">
                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Full Name</label>
                    <input
                      type="text"
                      className="w-full border border-slate-300 rounded-xl p-2.5 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm"
                      value={profile.full_name || ''}
                      onChange={e => updateField('full_name', e.target.value)}
                      placeholder="e.g. Ramesh Kumar"
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Date of Birth</label>
                    <input
                      type="date"
                      className="w-full border border-slate-300 rounded-xl p-2.5 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm"
                      value={profile.date_of_birth || ''}
                      onChange={e => updateField('date_of_birth', e.target.value)}
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">State</label>
                    <input
                      type="text"
                      className="w-full border border-slate-300 rounded-xl p-2.5 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm"
                      value={profile.state || ''}
                      onChange={e => updateField('state', e.target.value)}
                      placeholder="e.g. Telangana"
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">District</label>
                    <input
                      type="text"
                      className="w-full border border-slate-300 rounded-xl p-2.5 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm"
                      value={profile.district || ''}
                      onChange={e => updateField('district', e.target.value)}
                      placeholder="e.g. Hyderabad"
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Annual Family Income (₹)</label>
                    <input
                      type="number"
                      className="w-full border border-slate-300 rounded-xl p-2.5 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm"
                      value={profile.annual_income || ''}
                      onChange={e => updateField('annual_income', e.target.value)}
                      placeholder="e.g. 150000"
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Social Category (Caste)</label>
                    <select
                      className="w-full border border-slate-300 rounded-xl p-2.5 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm"
                      value={profile.category || ''}
                      onChange={e => updateField('category', e.target.value)}
                    >
                      <option value="">Select Category</option>
                      <option value="General">General</option>
                      <option value="OBC">OBC (Other Backward Class)</option>
                      <option value="SC">SC (Scheduled Caste)</option>
                      <option value="ST">ST (Scheduled Tribe)</option>
                      <option value="Minority">Minority</option>
                    </select>
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Employment Status</label>
                    <select
                      className="w-full border border-slate-300 rounded-xl p-2.5 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm"
                      value={profile.employment_status || ''}
                      onChange={e => updateField('employment_status', e.target.value)}
                    >
                      <option value="">Select Status</option>
                      <option value="Student">Student</option>
                      <option value="Unemployed">Unemployed</option>
                      <option value="Employed">Employed</option>
                      <option value="Self-employed">Self-employed / Farmer</option>
                    </select>
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Education Level</label>
                    <input
                      type="text"
                      className="w-full border border-slate-300 rounded-xl p-2.5 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm"
                      value={profile.education_level || ''}
                      onChange={e => updateField('education_level', e.target.value)}
                      placeholder="e.g. Undergraduate / Degree"
                    />
                  </div>

                  <div className="flex items-center gap-3 pt-6">
                    <input
                      type="checkbox"
                      id="disability"
                      checked={!!profile.disability_status}
                      onChange={e => updateField('disability_status', e.target.checked)}
                      className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500"
                    />
                    <label htmlFor="disability" className="font-bold text-slate-700 cursor-pointer">
                      Person with Disability (PwD)
                    </label>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100 flex justify-end">
                  <button
                    type="submit"
                    className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-2.5 rounded-xl shadow-xs transition text-sm"
                  >
                    Save Changes
                  </button>
                </div>
              </form>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                
                <div className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200/80 space-y-1">
                  <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                    <Calendar className="w-3.5 h-3.5 text-blue-600" />
                    <span>Date of Birth</span>
                  </div>
                  <div className="text-base font-bold text-slate-900">
                    {profile.date_of_birth || 'Not specified'}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200/80 space-y-1">
                  <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                    <MapPin className="w-3.5 h-3.5 text-blue-600" />
                    <span>State / District</span>
                  </div>
                  <div className="text-base font-bold text-slate-900">
                    {[profile.state, profile.district].filter(Boolean).join(', ') || 'Not specified'}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200/80 space-y-1">
                  <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                    <Wallet className="w-3.5 h-3.5 text-blue-600" />
                    <span>Annual Income</span>
                  </div>
                  <div className="text-base font-bold text-slate-900">
                    {profile.annual_income ? `₹${Number(profile.annual_income).toLocaleString('en-IN')}` : 'Not specified'}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200/80 space-y-1">
                  <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                    <Building className="w-3.5 h-3.5 text-blue-600" />
                    <span>Social Category</span>
                  </div>
                  <div className="text-base font-bold text-slate-900">
                    {profile.category || 'General'}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200/80 space-y-1">
                  <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                    <Briefcase className="w-3.5 h-3.5 text-blue-600" />
                    <span>Employment</span>
                  </div>
                  <div className="text-base font-bold text-slate-900">
                    {profile.employment_status || 'Not specified'}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200/80 space-y-1">
                  <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                    <GraduationCap className="w-3.5 h-3.5 text-blue-600" />
                    <span>Education Level</span>
                  </div>
                  <div className="text-base font-bold text-slate-900">
                    {profile.education_level || 'Not specified'}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200/80 space-y-1 sm:col-span-2">
                  <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                    <Heart className="w-3.5 h-3.5 text-blue-600" />
                    <span>Special Status</span>
                  </div>
                  <div className="text-base font-bold text-slate-900">
                    {profile.disability_status ? 'Person with Disability (PwD)' : 'None'}
                  </div>
                </div>

              </div>
            )}
          </div>
        ) : null}
      </div>

    </div>
  );
};
