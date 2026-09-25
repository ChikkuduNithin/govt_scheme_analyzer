import React, { useState } from 'react';
import { api } from '../services/api';
import { CheckCircle2, XCircle, HelpCircle, ChevronRight } from 'lucide-react';

export const Analyze: React.FC = () => {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [agentSteps, setAgentSteps] = useState<string[]>([]);

  const handleAnalyze = async () => {
    const cleanedQuery = query.trim();
    if (!cleanedQuery) {
      setStatus('Please enter a question first.');
      return;
    }

    setIsLoading(true);
    setStatus('');
    setResults(null);
    setAgentSteps([]);

    try {
      const token = localStorage.getItem('token');
      
      const response = await fetch(`http://localhost:8000/api/v1/analyze/stream?query=${encodeURIComponent(cleanedQuery)}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Analysis failed');
      }
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      let buffer = '';
      
      while (true) {
        const { value, done } = await reader!.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; 
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '');
            try {
              const data = JSON.parse(dataStr);
              if (data.type === 'step') {
                setAgentSteps(prev => [...prev, `Running Agent: ${data.node}...`]);
              } else if (data.type === 'result') {
                setResults(data.data);
                setAgentSteps(prev => [...prev, "Analysis Complete!"]);
              } else if (data.type === 'error') {
                setStatus(data.message);
              }
            } catch(e) {
                console.error("Error parsing SSE JSON:", e);
            }
          }
        }
      }
      
    } catch (err: any) {
      setStatus(err.message || 'An error occurred during analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">AI Scheme Analysis</h2>
      
      <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200 mb-6">
        <textarea 
          className="w-full border-0 p-2 focus:ring-0 resize-none" 
          rows={3} 
          placeholder="E.g. I am a 24 year old unemployed graduate from Telangana. My family income is 2.5 lakh per year. What schemes can I apply for?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="flex justify-end mt-2">
          <button onClick={handleAnalyze} disabled={!query.trim() || isLoading} className="bg-blue-600 text-white px-4 py-2 rounded font-medium disabled:opacity-50">
            Analyze
          </button>
        </div>
      </div>

      {agentSteps.length > 0 && !results && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-bold text-blue-900 mb-2 flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            Agentic Workflow in Progress...
          </h3>
          <ul className="space-y-1">
            {agentSteps.map((step, idx) => (
              <li key={idx} className="text-sm text-blue-800 font-mono">
                {`> ${step}`}
              </li>
            ))}
          </ul>
        </div>
      )}

      {status && agentSteps.length === 0 && (
        <div className="flex items-center gap-3 text-red-600 font-medium mb-6">
          <XCircle className="w-5 h-5"/>
          {status}
        </div>
      )}

      {results && (
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-bold">Recommended Schemes</h3>
            {results.profile_overrides && Object.keys(results.profile_overrides).length > 0 && (
              <p className="text-sm text-gray-600 mt-1">
                Used from your question: {Object.entries(results.profile_overrides).map(([key, value]: [string, any]) => `${key.replace('_', ' ')}: ${key === 'annual_income' ? `Rs. ${Number(value).toLocaleString('en-IN')}` : value}`).join(', ')}
              </p>
            )}
          </div>
          {Object.entries(results.eligibility_results).map(([schemeId, data]: [string, any]) => (
            <div key={schemeId} className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h4 className="text-lg font-bold text-gray-900">{data.scheme?.name || `Scheme ${schemeId}`}</h4>
                  <p className="text-sm text-gray-500">{[data.scheme?.department, data.scheme?.state].filter(Boolean).join(' • ')}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  data.status === 'LIKELY_ELIGIBLE' ? 'bg-green-100 text-green-800' :
                  data.status === 'NOT_ELIGIBLE' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {data.status.replace('_', ' ')}
                </span>
              </div>
              
              <p className="text-gray-700 mb-4">{data.verification?.summary || data.scheme?.description || 'Eligibility checked against available rules.'}</p>
              
              <div className="space-y-3 mb-6">
                {data.verification?.claims?.map((claim: any, idx: number) => (
                  <div key={idx} className="flex gap-3 bg-gray-50 p-3 rounded text-sm">
                    {claim.status === 'VERIFIED' ? <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0"/> : <XCircle className="w-5 h-5 text-red-500 shrink-0"/>}
                    <div>
                      <p className="font-medium text-gray-900">{claim.claim}</p>
                      <p className="text-gray-600 text-xs mt-1">{claim.reasoning}</p>
                      {claim.evidence_citation && (
                        <p className="text-blue-600 text-xs mt-1 font-mono">{claim.evidence_citation}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="flex justify-between items-center border-t pt-4">
                <div className="flex gap-4 text-sm text-gray-600">
                  <span className="flex items-center gap-1"><CheckCircle2 className="w-4 h-4"/> {data.satisfied_count} Matches</span>
                  <span className="flex items-center gap-1"><XCircle className="w-4 h-4"/> {data.failed_count} Fails</span>
                  <span className="flex items-center gap-1"><HelpCircle className="w-4 h-4"/> {data.unknown_count} Unknown</span>
                </div>
                <a href={data.scheme?.source_url || '#'} target="_blank" rel="noreferrer" className={`text-blue-600 hover:underline flex items-center gap-1 text-sm font-medium ${!data.scheme?.source_url ? 'pointer-events-none opacity-50' : ''}`}>
                  View Full Details <ChevronRight className="w-4 h-4"/>
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
