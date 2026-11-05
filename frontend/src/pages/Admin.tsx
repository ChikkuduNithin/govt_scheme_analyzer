import React, { useState } from 'react';
import { api } from '../services/api';
import { Upload, Plus, FileText, Trash2 } from 'lucide-react';

interface RuleForm {
  rule_type: string;
  field: string;
  operator: string;
  value: string;
  description: string;
}

export const Admin: React.FC = () => {
  const [schemeName, setSchemeName] = useState('');
  const [department, setDepartment] = useState('');
  const [state, setState] = useState('Central');
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  // Rule Builder State
  const [rules, setRules] = useState<RuleForm[]>([]);
  const [ruleType, setRuleType] = useState('income');
  const [field, setField] = useState('annual_income');
  const [operator, setOperator] = useState('<=');
  const [ruleValue, setRuleValue] = useState('250000');
  const [ruleDesc, setRuleDesc] = useState('Family income must be below 2.5 Lakhs');

  const addRule = () => {
    if (!field || !operator || !ruleValue || !ruleDesc) {
      alert("Please fill all rule parameters before adding.");
      return;
    }
    setRules([...rules, {
      rule_type: ruleType,
      field,
      operator,
      value: ruleValue,
      description: ruleDesc
    }]);
    setRuleDesc('');
  };

  const removeRule = (index: number) => {
    setRules(rules.filter((_, i) => i !== index));
  };

  const handleFieldChange = (newField: string) => {
    setField(newField);
    if (newField === 'annual_income') {
      setRuleType('income');
      setOperator('<=');
      setRuleValue('250000');
      setRuleDesc('Family income must be below 2.5 Lakhs');
    } else if (newField === 'age') {
      setRuleType('age');
      setOperator('<=');
      setRuleValue('25');
      setRuleDesc('Age must be 25 or below');
    } else if (newField === 'category') {
      setRuleType('category');
      setOperator('IN');
      setRuleValue('SC,ST,OBC');
      setRuleDesc('Must belong to SC, ST, or OBC category');
    } else if (newField === 'state') {
      setRuleType('state');
      setOperator('==');
      setRuleValue('Telangana');
      setRuleDesc('Must be a resident of Telangana');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!schemeName || !department || !selectedFile) {
      setStatus("Please fill all fields and select a PDF.");
      return;
    }

    setLoading(true);
    setStatus("Creating scheme and rules...");

    try {
      // 1. Create Scheme with structured rules
      const schemeRes = await api.post('/admin/schemes/', {
        name: schemeName,
        department,
        state,
        description,
        rules: rules
      });
      
      const schemeId = schemeRes.data.scheme_id;
      
      // 2. Upload Document & trigger real FAISS ingestion
      setStatus("Uploading document and generating real embeddings in background...");
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      await api.post(`/admin/schemes/${schemeId}/documents/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setStatus(`Success! Scheme created with ${rules.length} rule(s) and document is being embedded into FAISS.`);
      setSchemeName('');
      setDepartment('');
      setDescription('');
      setSelectedFile(null);
      setRules([]);
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
          <Plus className="w-5 h-5"/> Add New Scheme & Rules
        </h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Scheme Name</label>
              <input type="text" className="w-full border rounded p-2" value={schemeName} onChange={e => setSchemeName(e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Department / Ministry</label>
              <input type="text" className="w-full border rounded p-2" value={department} onChange={e => setDepartment(e.target.value)} required />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">State / Jurisdiction</label>
            <select className="w-full border rounded p-2" value={state} onChange={e => setState(e.target.value)}>
              <option value="Central">Central Govt (All India)</option>
              <option value="Telangana">Telangana</option>
              <option value="Andhra Pradesh">Andhra Pradesh</option>
              <option value="Tamil Nadu">Tamil Nadu</option>
              <option value="Karnataka">Karnataka</option>
              <option value="Maharashtra">Maharashtra</option>
              <option value="West Bengal">West Bengal</option>
              <option value="Rajasthan">Rajasthan</option>
              <option value="Odisha">Odisha</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Brief Description</label>
            <textarea className="w-full border rounded p-2" rows={3} value={description} onChange={e => setDescription(e.target.value)} required />
          </div>

          {/* Interactive Rule Builder */}
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50 space-y-3">
            <h4 className="font-semibold text-gray-800 text-sm">Deterministic Eligibility Rule Builder</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
              <div>
                <label className="block font-medium mb-1">Field</label>
                <select className="w-full border rounded p-1.5 bg-white" value={field} onChange={e => handleFieldChange(e.target.value)}>
                  <option value="annual_income">Annual Income</option>
                  <option value="age">Age</option>
                  <option value="category">Category (Caste)</option>
                  <option value="state">State</option>
                  <option value="gender">Gender</option>
                  <option value="employment_status">Employment</option>
                </select>
              </div>
              <div>
                <label className="block font-medium mb-1">Operator</label>
                <select className="w-full border rounded p-1.5 bg-white" value={operator} onChange={e => setOperator(e.target.value)}>
                  <option value="<=">&le; (Less than or equal)</option>
                  <option value=">=">&ge; (Greater than or equal)</option>
                  <option value="==">== (Exact match)</option>
                  <option value="!=">!= (Not equal)</option>
                  <option value="IN">IN (One of values)</option>
                </select>
              </div>
              <div>
                <label className="block font-medium mb-1">Value</label>
                <input type="text" className="w-full border rounded p-1.5 bg-white" value={ruleValue} onChange={e => setRuleValue(e.target.value)} placeholder="e.g. 250000" />
              </div>
              <div>
                <label className="block font-medium mb-1">Rule Type</label>
                <input type="text" className="w-full border rounded p-1.5 bg-white" value={ruleType} onChange={e => setRuleType(e.target.value)} />
              </div>
            </div>
            <div>
              <label className="block font-medium text-xs mb-1">Description (shown to citizen)</label>
              <div className="flex gap-2">
                <input type="text" className="flex-1 border rounded p-1.5 text-xs bg-white" value={ruleDesc} onChange={e => setRuleDesc(e.target.value)} placeholder="e.g. Family income must be below 2.5 Lakhs" />
                <button type="button" onClick={addRule} className="bg-gray-800 text-white px-3 py-1.5 rounded text-xs font-medium hover:bg-black">
                  Add Rule
                </button>
              </div>
            </div>

            {/* List of configured rules */}
            {rules.length > 0 && (
              <div className="space-y-1.5 pt-2 border-t border-gray-200">
                <span className="text-xs font-semibold text-gray-600">Attached Rules ({rules.length}):</span>
                {rules.map((r, i) => (
                  <div key={i} className="flex justify-between items-center text-xs bg-white p-2 rounded border border-gray-200">
                    <div>
                      <span className="font-mono text-blue-600 mr-2">{r.field} {r.operator} {r.value}</span>
                      <span className="text-gray-700">{r.description}</span>
                    </div>
                    <button type="button" onClick={() => removeRule(i)} className="text-red-500 hover:text-red-700">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input 
              type="file" 
              accept=".pdf,.docx,.txt" 
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
                  <span className="text-sm font-medium text-gray-900">Click to upload official guidelines (PDF, DOCX, TXT)</span>
                  <span className="text-xs text-gray-500 mt-1">This document will be chunked and embedded via real Gemini AI into FAISS.</span>
                </>
              )}
            </label>
          </div>
          
          <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white font-medium py-2 rounded disabled:opacity-50 flex justify-center items-center gap-2">
            {loading ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div> : 'Publish Scheme & Embed in Vector Store'}
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
