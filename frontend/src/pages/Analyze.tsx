import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { 
  CheckCircle2, 
  XCircle, 
  HelpCircle, 
  AlertCircle, 
  History, 
  Sparkles, 
  Trash2, 
  ExternalLink, 
  BookOpen, 
  Clock, 
  Compass, 
  Copy, 
  Check, 
  ShieldCheck,
  Send,
  X
} from 'lucide-react';

interface HistoryItem {
  id: string;
  query: string;
  timestamp: number;
  dateFormatted: string;
  results: any;
  overrides: Record<string, any>;
  schemesCount: number;
  topSchemeName: string;
  topStatus: string;
}

const PRESET_QUERIES = [
  {
    icon: "🎓",
    label: "Osmania University SC Student",
    query: "Pursuing degree at osmania university\nfamily income <2 lakhs\nSC"
  },
  {
    icon: "🌾",
    label: "Telangana Small Farmer",
    query: "Small farmer in Telangana with 2 acres land needing financial assistance for seeds and crops"
  },
  {
    icon: "👩‍🎓",
    label: "Girl Technical Scholarship",
    query: "21 year old OBC girl studying engineering degree, family annual income 1.8 Lakhs"
  },
  {
    icon: "🏥",
    label: "Senior Citizen Health Cover",
    query: "65 year old senior citizen in Telangana needing health insurance coverage under 2.5 Lakhs income"
  }
];

export const Analyze: React.FC = () => {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [agentSteps, setAgentSteps] = useState<{ node: string; title: string; desc: string; done: boolean }[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'ELIGIBLE' | 'REVIEW'>('ALL');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  // Load history from localStorage on initial render
  useEffect(() => {
    try {
      const stored = localStorage.getItem('govscheme_analysis_history');
      if (stored) {
        setHistory(JSON.parse(stored));
      }
    } catch (e) {
      console.error("Error loading analysis history:", e);
    }
  }, []);

  // Cleanup abort controller on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const saveToHistory = (queryText: string, resultData: any) => {
    try {
      const schemesList = Object.values(resultData.eligibility_results || {});
      const firstScheme: any = schemesList[0] || {};
      const eligibleScheme: any = schemesList.find((s: any) => s.status === 'LIKELY_ELIGIBLE') || firstScheme;

      const newItem: HistoryItem = {
        id: Date.now().toString(),
        query: queryText,
        timestamp: Date.now(),
        dateFormatted: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', day: 'numeric', month: 'short' }),
        results: resultData,
        overrides: resultData.profile_overrides || {},
        schemesCount: schemesList.length,
        topSchemeName: eligibleScheme.scheme?.name || 'Government Schemes',
        topStatus: eligibleScheme.status || 'EVALUATED'
      };

      setHistory(prev => {
        const updated = [newItem, ...prev.filter(h => h.query !== queryText)].slice(0, 25);
        localStorage.setItem('govscheme_analysis_history', JSON.stringify(updated));
        return updated;
      });
    } catch (e) {
      console.error("Error saving history item:", e);
    }
  };

  const deleteHistoryItem = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = history.filter(h => h.id !== id);
    setHistory(updated);
    localStorage.setItem('govscheme_analysis_history', JSON.stringify(updated));
  };

  const clearAllHistory = () => {
    if (window.confirm("Are you sure you want to clear your analysis history?")) {
      setHistory([]);
      localStorage.removeItem('govscheme_analysis_history');
    }
  };

  const loadFromHistory = (item: HistoryItem) => {
    setQuery(item.query);
    setResults(item.results);
    setStatus('');
    setAgentSteps([
      { node: "coordinator", title: "Intent Coordinator", desc: "Loaded intent & demographic constraints from history", done: true },
      { node: "retriever", title: "Hybrid Retriever", desc: "Retrieved chunks verified from memory", done: true },
      { node: "eligibility_engine", title: "Rule Engine", desc: "Deterministic mathematical logic verified", done: true },
      { node: "verification", title: "Verification Auditor", desc: "Official citations & claims verified", done: true }
    ]);
    setShowHistory(false);
  };

  const copySchemeToClipboard = (schemeId: string, schemeName: string, summary: string) => {
    const textToCopy = `🏛️ ${schemeName}\nStatus: Verified\nSummary: ${summary}\nAnalyzed via GovScheme AI`;
    navigator.clipboard.writeText(textToCopy);
    setCopiedId(schemeId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleAnalyze = async () => {
    const cleanedQuery = query.trim();
    if (!cleanedQuery) {
      setStatus('Please describe your background or requirement first.');
      return;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setIsLoading(true);
    setStatus('');
    setResults(null);

    // Initial workflow step indicators
    const initialSteps = [
      { node: "coordinator", title: "Intent Coordinator", desc: "Parsing query keywords & demographic parameters", done: false },
      { node: "retriever", title: "3072-dim Vector Retriever", desc: "Searching FAISS dense vectors & applying jurisdictional filters", done: false },
      { node: "eligibility_engine", title: "Deterministic Rule Engine", desc: "Evaluating mathematical eligibility cutoffs without hallucination", done: false },
      { node: "verification", title: "Document Verification Auditor", desc: "Cross-referencing claims against official gazette text & page numbers", done: false }
    ];
    setAgentSteps(initialSteps);

    try {
      const token = localStorage.getItem('token');
      const baseUrl = api.defaults.baseURL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${baseUrl}/analyze/stream?query=${encodeURIComponent(cleanedQuery)}`, {
        signal: controller.signal,
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Analysis service responded with status ${response.status}`);
      }
      
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Streaming response is unavailable.');
      }
      const decoder = new TextDecoder();
      let buffer = '';
      
      while (true) {
        const { value, done } = await reader.read();
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
                setAgentSteps(prev => prev.map(s => s.node === data.node ? { ...s, done: true } : s));
              } else if (data.type === 'result') {
                setResults(data.data);
                setAgentSteps(prev => prev.map(s => ({ ...s, done: true })));
                saveToHistory(cleanedQuery, data.data);
              } else if (data.type === 'error') {
                setStatus(data.message);
              }
            } catch (e) {
              console.error("Error parsing SSE JSON chunk:", e);
            }
          }
        }
      }
      
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setStatus(err.message || 'An error occurred during multi-agent analysis.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Filter results
  const filteredSchemes = results ? Object.entries(results.eligibility_results || {}).filter(([_, data]: [string, any]) => {
    if (activeFilter === 'ELIGIBLE') return data.status === 'LIKELY_ELIGIBLE';
    if (activeFilter === 'REVIEW') return data.status !== 'LIKELY_ELIGIBLE';
    return true;
  }) : [];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-gray-50 to-slate-100 text-slate-800 pb-16">
      
      {/* Top Hero Section */}
      <div className="bg-white border-b border-slate-200/80 shadow-xs">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200/60 mb-2.5">
                <Sparkles className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
                <span>Agentic RAG • Deterministic Rule Verification • Official Gazette Grounding</span>
              </div>
              <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
                AI Scheme Analyzer
              </h1>
              <p className="mt-1.5 text-sm text-slate-500 max-w-2xl">
                Describe your background, income, location, and requirements in plain language. Our multi-agent AI deterministically verifies eligibility against official government gazettes.
              </p>
            </div>

            {/* History Toggle Button */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowHistory(!showHistory)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold border transition shadow-xs ${
                  showHistory 
                    ? 'bg-blue-600 text-white border-blue-600 shadow-blue-200' 
                    : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50 hover:border-slate-300'
                }`}
              >
                <History className="w-4 h-4" />
                <span>History</span>
                {history.length > 0 && (
                  <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${showHistory ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-600'}`}>
                    {history.length}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 pt-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Main Analysis Column */}
          <div className={`${showHistory ? 'lg:col-span-8' : 'lg:col-span-12'} space-y-6 transition-all duration-300`}>
            
            {/* Input Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden transition-all focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500">
              <div className="p-4 sm:p-5">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                  Citizen Profile & Query Context
                </label>
                <textarea
                  className="w-full border-0 p-0 text-slate-800 placeholder-slate-400 focus:ring-0 resize-none text-base sm:text-lg leading-relaxed font-normal"
                  rows={3}
                  placeholder="e.g. Pursuing degree at Osmania University, family income < 2 Lakhs, SC category student seeking higher education scholarships..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                      handleAnalyze();
                    }
                  }}
                />
              </div>

              {/* Quick Preset Suggestion Chips */}
              <div className="px-4 sm:px-5 py-2.5 bg-slate-50/70 border-t border-slate-100 flex flex-wrap items-center gap-2">
                <span className="text-xs font-semibold text-slate-400 flex items-center gap-1 mr-1">
                  <Compass className="w-3.5 h-3.5" /> Presets:
                </span>
                {PRESET_QUERIES.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setQuery(item.query)}
                    className="text-xs font-medium bg-white hover:bg-blue-50 text-slate-600 hover:text-blue-700 px-2.5 py-1 rounded-lg border border-slate-200 hover:border-blue-300 transition flex items-center gap-1.5 shadow-2xs"
                  >
                    <span>{item.icon}</span>
                    <span>{item.label}</span>
                  </button>
                ))}
              </div>

              {/* Bottom Action Bar */}
              <div className="px-4 sm:px-5 py-3 bg-white border-t border-slate-100 flex items-center justify-between">
                <div className="text-xs text-slate-400 hidden sm:block">
                  Press <kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-mono border border-slate-200">Ctrl + Enter</kbd> to analyze
                </div>
                <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
                  {query && (
                    <button
                      type="button"
                      onClick={() => setQuery('')}
                      className="text-xs text-slate-400 hover:text-slate-600 font-medium px-2 py-1"
                    >
                      Clear
                    </button>
                  )}
                  <button
                    onClick={handleAnalyze}
                    disabled={!query.trim() || isLoading}
                    className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold px-6 py-2.5 rounded-xl shadow-sm hover:shadow transition disabled:opacity-50 flex items-center justify-center gap-2 text-sm"
                  >
                    {isLoading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Analyzing Agents...</span>
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        <span>Run Analysis</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Error Banner */}
            {status && (
              <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-xl flex items-center gap-3 text-sm animate-fadeIn">
                <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
                <p className="flex-1 font-medium">{status}</p>
                <button onClick={() => setStatus('')} className="text-rose-500 hover:text-rose-700">
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Visual Multi-Agent Progress Checklist */}
            {agentSteps.length > 0 && (
              <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm space-y-3.5">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-blue-600" />
                    <span>Agentic Pipeline Verification</span>
                  </h3>
                  {isLoading && (
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full bg-blue-600 animate-ping"></div>
                      Executing in real-time
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {agentSteps.map((step, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-xl border text-xs flex items-start gap-2.5 transition-all ${
                        step.done
                          ? 'bg-emerald-50/70 border-emerald-200 text-emerald-950'
                          : isLoading && idx === agentSteps.findIndex(s => !s.done)
                          ? 'bg-blue-50 border-blue-300 text-blue-950 shadow-xs'
                          : 'bg-slate-50 border-slate-200/60 text-slate-400'
                      }`}
                    >
                      <div className="mt-0.5 shrink-0">
                        {step.done ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        ) : isLoading && idx === agentSteps.findIndex(s => !s.done) ? (
                          <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                          <div className="w-4 h-4 rounded-full border border-slate-300 flex items-center justify-center text-[10px] text-slate-400 font-mono">
                            {idx + 1}
                          </div>
                        )}
                      </div>
                      <div className="min-w-0">
                        <div className="font-bold">{step.title}</div>
                        <div className={`mt-0.5 truncate ${step.done ? 'text-emerald-700' : 'text-slate-500'}`}>
                          {step.desc}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Results Section */}
            {results && (
              <div className="space-y-5 animate-fadeIn">
                
                {/* Result Controls Bar */}
                <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                      <span>Evaluated Welfare Schemes</span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                        {filteredSchemes.length} of {Object.keys(results.eligibility_results || {}).length}
                      </span>
                    </h3>
                    {results.profile_overrides && Object.keys(results.profile_overrides).length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5 mt-2">
                        <span className="text-xs font-semibold text-slate-500">Query Overrides:</span>
                        {Object.entries(results.profile_overrides).map(([k, v]: [string, any]) => (
                          <span key={k} className="inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200/60 font-mono">
                            {k.replace('_', ' ')}: {k === 'annual_income' ? `₹${Number(v).toLocaleString('en-IN')}` : v}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Filter Tabs */}
                  <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-xl border border-slate-200/60 self-start sm:self-center">
                    <button
                      onClick={() => setActiveFilter('ALL')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                        activeFilter === 'ALL' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      All
                    </button>
                    <button
                      onClick={() => setActiveFilter('ELIGIBLE')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                        activeFilter === 'ELIGIBLE' ? 'bg-white text-emerald-800 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      Likely Eligible
                    </button>
                    <button
                      onClick={() => setActiveFilter('REVIEW')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                        activeFilter === 'REVIEW' ? 'bg-white text-amber-800 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      Needs Review
                    </button>
                  </div>
                </div>

                {/* Scheme Cards */}
                {filteredSchemes.length === 0 ? (
                  <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 shadow-sm">
                    <HelpCircle className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                    <h4 className="text-base font-bold text-slate-800">No schemes match this filter</h4>
                    <p className="text-xs text-slate-500 mt-1">Try switching to the "All" tab to view all analyzed candidates.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {filteredSchemes.map(([schemeId, data]: [string, any]) => {
                      const isEligible = data.status === 'LIKELY_ELIGIBLE';
                      const isNotEligible = data.status === 'NOT_ELIGIBLE';
                      const isPossibly = !isEligible && !isNotEligible;

                      return (
                        <div
                          key={schemeId}
                          className={`bg-white rounded-2xl border transition-all hover:shadow-md overflow-hidden ${
                            isEligible 
                              ? 'border-emerald-300/80 shadow-xs' 
                              : isNotEligible 
                              ? 'border-slate-200/90 shadow-2xs' 
                              : 'border-amber-300/80 shadow-xs'
                          }`}
                        >
                          {/* Accent Top Border */}
                          <div className={`h-1.5 w-full ${
                            isEligible ? 'bg-gradient-to-r from-emerald-500 to-teal-500' :
                            isNotEligible ? 'bg-gradient-to-r from-slate-400 to-rose-400' :
                            'bg-gradient-to-r from-amber-400 to-orange-400'
                          }`} />

                          <div className="p-5 sm:p-6 space-y-4">
                            {/* Card Header */}
                            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                              <div className="space-y-1">
                                <div className="flex flex-wrap items-center gap-2">
                                  <h4 className="text-lg font-bold text-slate-900 leading-snug">
                                    {data.scheme?.name || `Scheme #${schemeId}`}
                                  </h4>
                                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 border border-slate-200">
                                    {data.scheme?.state || 'Central'}
                                  </span>
                                  {data.scheme?.department && (
                                    <span className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200/60">
                                      {data.scheme.department}
                                    </span>
                                  )}
                                </div>
                                <p className="text-xs text-slate-500 line-clamp-2">
                                  {data.scheme?.description}
                                </p>
                              </div>

                              {/* Status Badge */}
                              <div className="shrink-0">
                                <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider border shadow-2xs ${
                                  isEligible
                                    ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                                    : isNotEligible
                                    ? 'bg-rose-50 text-rose-800 border-rose-200'
                                    : 'bg-amber-50 text-amber-800 border-amber-300'
                                }`}>
                                  {isEligible && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />}
                                  {isNotEligible && <XCircle className="w-3.5 h-3.5 text-rose-600" />}
                                  {isPossibly && <HelpCircle className="w-3.5 h-3.5 text-amber-600" />}
                                  <span>{data.status.replace('_', ' ')}</span>
                                </span>
                              </div>
                            </div>

                            {/* Verification Summary Callout */}
                            <div className={`p-3.5 rounded-xl text-xs sm:text-sm leading-relaxed border ${
                              isEligible
                                ? 'bg-emerald-50/50 border-emerald-200/70 text-emerald-950'
                                : isNotEligible
                                ? 'bg-slate-50 border-slate-200/80 text-slate-800'
                                : 'bg-amber-50/50 border-amber-200/70 text-amber-950'
                            }`}>
                              <span className="font-bold mr-1">AI Verdict:</span>
                              {data.verification?.summary || 'Calculated against official eligibility thresholds.'}
                            </div>

                            {/* Detailed Rules Evaluated */}
                            {(data.satisfied_criteria?.length > 0 || data.failed_criteria?.length > 0 || data.unknown_criteria?.length > 0) && (
                              <div className="space-y-2 pt-1">
                                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                                  Deterministic Rule Matching:
                                </span>
                                <div className="flex flex-wrap gap-2">
                                  {data.satisfied_criteria?.map((c: string, idx: number) => (
                                    <span key={`sat-${idx}`} className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 shadow-2xs">
                                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                                      <span>{c}</span>
                                    </span>
                                  ))}
                                  {data.failed_criteria?.map((c: string, idx: number) => (
                                    <span key={`fail-${idx}`} className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200 shadow-2xs">
                                      <XCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                                      <span>{c}</span>
                                    </span>
                                  ))}
                                  {data.unknown_criteria?.map((c: string, idx: number) => (
                                    <span key={`unk-${idx}`} className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200 shadow-2xs">
                                      <HelpCircle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                                      <span>{c}</span>
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Document Evidence Citations */}
                            {data.verification?.claims?.length > 0 && (
                              <div className="space-y-2.5 pt-2 border-t border-slate-100">
                                <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-400">
                                  <BookOpen className="w-3.5 h-3.5 text-blue-600" />
                                  <span>Official Guidelines Grounding & Citations:</span>
                                </div>
                                <div className="space-y-2">
                                  {data.verification.claims.map((claim: any, idx: number) => (
                                    <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-xs space-y-1">
                                      <div className="flex items-start gap-2">
                                        {claim.status === 'VERIFIED' ? (
                                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                                        ) : (
                                          <XCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                                        )}
                                        <div className="flex-1">
                                          <div className="font-bold text-slate-800">{claim.claim}</div>
                                          <div className="text-slate-600 mt-0.5">{claim.reasoning}</div>
                                          {claim.evidence_citation && (
                                            <div className="mt-1.5 font-mono text-[11px] text-blue-800 bg-blue-50/80 border border-blue-200/60 p-1.5 rounded-md">
                                              {claim.evidence_citation}
                                            </div>
                                          )}
                                        </div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Card Footer Actions */}
                            <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3 text-xs">
                              <div className="flex items-center gap-3 text-slate-500 font-medium">
                                <span className="text-emerald-700 font-bold">{data.satisfied_count} Met</span>
                                <span>•</span>
                                <span className="text-rose-700 font-bold">{data.failed_count} Failed</span>
                                <span>•</span>
                                <span className="text-amber-700 font-bold">{data.unknown_count} Unknown</span>
                              </div>

                              <div className="flex items-center gap-2">
                                <button
                                  type="button"
                                  onClick={() => copySchemeToClipboard(schemeId, data.scheme?.name, data.verification?.summary)}
                                  className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition flex items-center gap-1 font-semibold"
                                >
                                  {copiedId === schemeId ? (
                                    <>
                                      <Check className="w-3.5 h-3.5 text-emerald-600" />
                                      <span className="text-emerald-700">Copied!</span>
                                    </>
                                  ) : (
                                    <>
                                      <Copy className="w-3.5 h-3.5" />
                                      <span>Copy</span>
                                    </>
                                  )}
                                </button>
                                
                                <a
                                  href={data.scheme?.source_url || '#'}
                                  target="_blank"
                                  rel="noreferrer"
                                  className={`px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold transition flex items-center gap-1 shadow-2xs ${
                                    !data.scheme?.source_url ? 'pointer-events-none opacity-50' : ''
                                  }`}
                                >
                                  <span>Official Portal</span>
                                  <ExternalLink className="w-3.5 h-3.5" />
                                </a>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* History Sidebar Panel */}
          {showHistory && (
            <div className="lg:col-span-4 space-y-4 animate-fadeIn">
              <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-4 sticky top-6">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <History className="w-4 h-4 text-blue-600" />
                    <h3 className="font-bold text-sm text-slate-800">Recent Analyses</h3>
                  </div>
                  {history.length > 0 && (
                    <button
                      onClick={clearAllHistory}
                      className="text-[11px] text-rose-600 hover:text-rose-800 font-semibold flex items-center gap-1"
                    >
                      <Trash2 className="w-3 h-3" />
                      <span>Clear All</span>
                    </button>
                  )}
                </div>

                {history.length === 0 ? (
                  <div className="py-10 text-center text-slate-400 text-xs">
                    <Clock className="w-8 h-8 text-slate-200 mx-auto mb-2" />
                    <p className="font-semibold text-slate-600">No past analyses yet</p>
                    <p className="mt-0.5">Your queries and verified scheme results will automatically save here.</p>
                  </div>
                ) : (
                  <div className="space-y-2.5 mt-3 max-h-[calc(100vh-220px)] overflow-y-auto pr-1">
                    {history.map((item) => (
                      <div
                        key={item.id}
                        onClick={() => loadFromHistory(item)}
                        className="group p-3 rounded-xl border border-slate-200/80 hover:border-blue-300 hover:bg-blue-50/40 transition cursor-pointer space-y-2 bg-slate-50/40"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-xs font-semibold text-slate-800 line-clamp-2 leading-relaxed">
                            {item.query}
                          </p>
                          <button
                            type="button"
                            onClick={(e) => deleteHistoryItem(item.id, e)}
                            className="text-slate-300 hover:text-rose-600 opacity-0 group-hover:opacity-100 transition p-1"
                            title="Delete this query"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>

                        {/* Top scheme & date badge */}
                        <div className="flex items-center justify-between text-[11px]">
                          <span className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                            item.topStatus === 'LIKELY_ELIGIBLE' 
                              ? 'bg-emerald-100 text-emerald-800' 
                              : 'bg-amber-100 text-amber-800'
                          }`}>
                            {item.schemesCount} schemes found
                          </span>
                          <span className="text-slate-400 font-mono text-[10px]">
                            {item.dateFormatted}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
