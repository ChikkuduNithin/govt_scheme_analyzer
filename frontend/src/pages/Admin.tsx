import React, { useState } from 'react';
import { api } from '../services/api';
import { Upload, Plus, FileText, CheckCircle2 } from 'lucide-react';

export const Admin: React.FC = () => {
  const [schemeName, setSchemeName] = useState('');
  const [department, setDepartment] = useState('');
  const [state, setState] = useState('Central');
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!schemeName || !department || !selectedFile) {
      setStatus("Please fill all fields and select a PDF.");
      return;
    }

    setLoading(true);
    setStatus("Creating scheme...");

    try {
      // 1. Create Scheme
      const schemeRes = await api.post('/admin/schemes/', {
        name: schemeName,
        department,
        state,
        description,
        rules: [] // Simplify for demo
      });
      
      const schemeId = schemeRes.data.scheme_id;
      
      // 2. Upload Document
      setStatus("Uploading document and processing in background...");
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      await api.post(`/admin/schemes/${schemeId}/documents/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setStatus("Success! Scheme created and document is processing in the background.");
      setSchemeName('');
      setDepartment('');
      setDescription('');
      setSelectedFile(null);
    } catch (err: any) {
      setStatus(err.response?.data?.detail || err.message || "Failed to create scheme");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">Admin Dashboard</h2>
      
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Plus className="w-5 h-5"/> Add New Scheme
        </h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Scheme Name</label>
              <input type="text" className="w-full border rounded p-2" value={schemeName} onChange={e => setSchemeName(e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
              <input type="text" className="w-full border rounded p-2" value={department} onChange={e => setDepartment(e.target.value)} required />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">State / Jurisdiction</label>
            <select className="w-full border rounded p-2" value={state} onChange={e => setState(e.target.value)}>
              <option value="Central">Central Govt</option>
              <option value="Telangana">Telangana</option>
              <option value="Maharashtra">Maharashtra</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Brief Description</label>
            <textarea className="w-full border rounded p-2" rows={3} value={description} onChange={e => setDescription(e.target.value)} required />
          </div>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input 
              type="file" 
              accept=".pdf" 
              className="hidden" 
              id="file-upload" 
              onChange={e => setSelectedFile(e.target.files?.[0] || null)}
            />
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center justify-center">
              {selectedFile ? (
                <>
                  <FileText className="w-8 h-8 text-blue-500 mb-2"/>
                  <span className="text-sm font-medium text-gray-900">{selectedFile.name}</span>
                </>
              ) : (
                <>
                  <Upload className="w-8 h-8 text-gray-400 mb-2"/>
                  <span className="text-sm font-medium text-gray-900">Click to upload official guidelines (PDF)</span>
                  <span className="text-xs text-gray-500 mt-1">This document will be chunked and embedded via AI.</span>
                </>
              )}
            </label>
          </div>
          
          <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white font-medium py-2 rounded disabled:opacity-50 flex justify-center items-center gap-2">
            {loading ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div> : 'Publish Scheme & Process Vectors'}
          </button>
        </form>
        
        {status && (
          <div className={`mt-4 p-3 rounded text-sm font-medium ${status.includes('Success') ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}`}>
            {status}
          </div>
        )}
      </div>
    </div>
  );
};
