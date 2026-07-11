import { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import { apiFetch } from '../lib/api';

/* ─── config items ─── */
const configItems = [
  {
    label: 'AI Model',
    value: 'GPT-4o Mini',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
      </svg>
    ),
  },
  {
    label: 'TTS Engine',
    value: 'ElevenLabs',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z" />
      </svg>
    ),
  },
  {
    label: 'STT Engine',
    value: 'Deepgram',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
      </svg>
    ),
  },
  {
    label: 'Telephony',
    value: 'Twilio',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 01-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z" />
      </svg>
    ),
  },
  {
    label: 'Database',
    value: 'Supabase / PostgreSQL',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
      </svg>
    ),
  },
  {
    label: 'Language',
    value: 'Hindi + English (Auto)',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 21l5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 016-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 01-3.827-5.802" />
      </svg>
    ),
  },
  {
    label: 'Graph Database',
    value: 'Neo4j AuraDB',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
      </svg>
    ),
  },
  {
    label: 'Platform',
    value: 'Base44',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 7.125C2.25 6.504 2.754 6 3.375 6h6c.621 0 1.125.504 1.125 1.125v3.75c0 .621-.504 1.125-1.125 1.125h-6a1.125 1.125 0 01-1.125-1.125v-3.75zM14.25 8.625c0-.621.504-1.125 1.125-1.125h5.25c.621 0 1.125.504 1.125 1.125v8.25c0 .621-.504 1.125-1.125 1.125h-5.25a1.125 1.125 0 01-1.125-1.125v-8.25zM3.75 16.125c0-.621.504-1.125 1.125-1.125h5.25c.621 0 1.125.504 1.125 1.125v2.25c0 .621-.504 1.125-1.125 1.125h-5.25a1.125 1.125 0 01-1.125-1.125v-2.25z" />
      </svg>
    ),
  },
];

/* ─── requirements ─── */
const requirements = [
  { label: 'Python 3.9+', status: true },
  { label: 'Node.js 18+', status: true },
  { label: 'Twilio Account', status: true },
  { label: 'OpenAI API Key', status: true },
  { label: 'ElevenLabs API Key', status: true },
  { label: 'Deepgram API Key', status: true },
  { label: 'Supabase Project', status: true },
];

/* ─── How it works steps ─── */
const steps = [
  { title: 'Missed Call Detected', desc: 'Twilio webhook triggers when a call is missed' },
  { title: 'AI Calls Back', desc: 'System initiates an outbound call using Twilio' },
  { title: 'Conversation', desc: 'GPT-4o conducts a natural voice conversation' },
  { title: 'Transcription', desc: 'Deepgram converts speech to text in real-time' },
  { title: 'Analysis', desc: 'AI extracts intent, sentiment, and lead information' },
  { title: 'Data Stored', desc: 'Results saved to database with full transcript' },
];

/* ─── Base44 mock roles ─── */
const roles = [
  { name: 'Admin', desc: 'Full system access, configuration management', color: 'cyan' },
  { name: 'Analyst', desc: 'View analytics, logs, and knowledge graph', color: 'violet' },
  { name: 'Viewer', desc: 'Read-only dashboard access', color: 'amber' },
];

export default function Settings() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [neo4jStatus, setNeo4jStatus] = useState(null);
  const [neo4jLoading, setNeo4jLoading] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [activeRole, setActiveRole] = useState('Admin');
  const [crudItems, setCrudItems] = useState([
    { id: 1, key: 'max_call_duration', value: '300', desc: 'Maximum call duration in seconds' },
    { id: 2, key: 'greeting_language', value: 'auto', desc: 'Default greeting language' },
    { id: 3, key: 'sentiment_threshold', value: '0.65', desc: 'Threshold for positive sentiment' },
  ]);
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');

  // Toast helpers
  const showToast = (message, type = 'success') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3000);
  };

  const checkHealth = async () => {
    setHealthLoading(true);
    setHealthStatus(null);
    try {
      const data = await apiFetch('/ping');
      setHealthStatus(data.status === 'ok' ? 'ok' : 'error');
      showToast(data.status === 'ok' ? 'Backend is healthy' : 'Backend check failed', data.status === 'ok' ? 'success' : 'error');
    } catch {
      setHealthStatus('error');
      showToast('Could not reach backend', 'error');
    } finally {
      setHealthLoading(false);
    }
  };

  const checkNeo4j = async () => {
    setNeo4jLoading(true);
    setNeo4jStatus(null);
    try {
      const data = await apiFetch('/api/neo4j/stats');
      setNeo4jStatus(data && data.total_nodes !== undefined ? 'ok' : 'error');
      showToast(`Neo4j: ${data.total_nodes} nodes, ${data.total_relationships} relationships`);
    } catch {
      setNeo4jStatus('error');
      showToast('Could not reach Neo4j AuraDB', 'error');
    } finally {
      setNeo4jLoading(false);
    }
  };

  // CRUD handlers
  const startEdit = (item) => {
    setEditingId(item.id);
    setEditValue(item.value);
  };

  const saveEdit = (id) => {
    setCrudItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, value: editValue } : item))
    );
    setEditingId(null);
    showToast('Configuration updated');
  };

  const deleteItem = (id) => {
    setCrudItems((prev) => prev.filter((item) => item.id !== id));
    showToast('Configuration removed', 'warning');
  };

  const addItem = () => {
    const newId = Math.max(0, ...crudItems.map((i) => i.id)) + 1;
    setCrudItems((prev) => [
      ...prev,
      { id: newId, key: `custom_param_${newId}`, value: '0', desc: 'Custom parameter' },
    ]);
    showToast('New configuration added');
  };

  return (
    <>
      <style jsx global>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(18px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse-ring {
          0% { transform: scale(0.8); opacity: 1; }
          100% { transform: scale(2.2); opacity: 0; }
        }
        .glass-card {
          background: rgba(17, 24, 39, 0.6);
          backdrop-filter: blur(16px);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 1rem;
        }
      `}</style>

      <div className="flex min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
        <Sidebar />

        <main className="flex-1 ml-64 p-8 overflow-y-auto">
          {/* Header */}
          <div className="mb-8" style={{ animation: 'fadeInUp 0.5s ease-out' }}>
            <h1 className="text-3xl font-extrabold tracking-tight">
              <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                Settings
              </span>
            </h1>
            <p className="text-gray-400 mt-1 text-sm">System configuration and health monitoring</p>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {/* ─── Current Configuration ─── */}
            <div className="glass-card p-6" style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '100ms' }}>
              <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-cyan-400" />
                Current Configuration
              </h2>
              <div className="space-y-3">
                {configItems.map((item) => (
                  <div
                    key={item.label}
                    className="flex items-center gap-4 p-3.5 rounded-xl bg-gray-800/40 border border-white/[0.03] hover:border-white/[0.08] transition"
                  >
                    <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20 text-cyan-400 shrink-0">
                      {item.icon}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs text-gray-500 font-medium uppercase tracking-wider">{item.label}</p>
                      <p className="text-sm text-gray-200 font-semibold mt-0.5 truncate">{item.value}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* ─── Health Check ─── */}
            <div className="space-y-6">
              <div className="glass-card p-6" style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '200ms' }}>
                <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  Health Check
                </h2>
                <div className="flex items-center gap-6">
                  <button
                    onClick={checkHealth}
                    disabled={healthLoading}
                    className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-sm font-semibold shadow-lg shadow-cyan-500/20 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {healthLoading ? (
                      <>
                        <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                        Checking…
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4" />
                        </svg>
                        Run Health Check
                      </>
                    )}
                  </button>

                  {healthStatus && (
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <span
                          className={`block w-4 h-4 rounded-full ${
                            healthStatus === 'ok' ? 'bg-emerald-400' : 'bg-rose-400'
                          }`}
                        />
                        <span
                          className={`absolute inset-0 rounded-full ${
                            healthStatus === 'ok' ? 'bg-emerald-400' : 'bg-rose-400'
                          }`}
                          style={{ animation: 'pulse-ring 1.5s ease-out infinite' }}
                        />
                      </div>
                      <div>
                        <p className={`text-sm font-semibold ${healthStatus === 'ok' ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {healthStatus === 'ok' ? 'All Systems Operational' : 'Connection Failed'}
                        </p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {healthStatus === 'ok' ? 'Backend is responding normally' : 'Could not reach the backend server'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* ─── System Requirements ─── */}
              <div className="glass-card p-6" style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '300ms' }}>
                <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-violet-400" />
                  System Requirements
                </h2>
                <div className="space-y-2.5">
                  {requirements.map((req) => (
                    <div key={req.label} className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-gray-800/40 transition">
                      <div className={`flex items-center justify-center w-6 h-6 rounded-full ${
                        req.status ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                      }`}>
                        {req.status ? (
                          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                          </svg>
                        ) : (
                          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        )}
                      </div>
                      <span className="text-sm text-gray-300">{req.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* ─── How It Works ─── */}
          <div
            className="glass-card p-6 mt-6"
            style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '400ms' }}
          >
            <h2 className="text-lg font-semibold text-white mb-8 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              How It Works
            </h2>
            <div className="relative">
              {/* connecting line */}
              <div className="absolute left-6 top-6 bottom-6 w-px bg-gradient-to-b from-cyan-500/40 via-blue-500/40 to-violet-500/40" />

              <div className="space-y-8">
                {steps.map((step, idx) => (
                  <div key={idx} className="relative flex items-start gap-5 pl-0">
                    {/* numbered circle */}
                    <div className="relative z-10 flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 shrink-0">
                      <span className="text-sm font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                        {idx + 1}
                      </span>
                    </div>
                    <div className="pt-2">
                      <h3 className="text-sm font-semibold text-gray-200">{step.title}</h3>
                      <p className="text-xs text-gray-500 mt-1">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ─── Base44 Features ─── */}
          <div className="mt-6 space-y-6">
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">
                Base44 Platform Features
              </h2>
              <span className="text-[10px] font-bold bg-violet-500/10 text-violet-400 px-2 py-0.5 rounded border border-violet-500/20 uppercase tracking-widest">
                Enterprise
              </span>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              {/* Role-Based Access Control */}
              <div className="glass-card p-6" style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '500ms' }}>
                <h3 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400" />
                  Role-Based Access
                </h3>
                <div className="space-y-3">
                  {roles.map((role) => (
                    <button
                      key={role.name}
                      onClick={() => {
                        setActiveRole(role.name);
                        showToast(`Switched to ${role.name} role`);
                      }}
                      className={`w-full flex items-center gap-4 p-3.5 rounded-xl border transition ${
                        activeRole === role.name
                          ? `bg-${role.color}-500/10 border-${role.color}-500/30`
                          : 'bg-gray-800/40 border-white/[0.03] hover:border-white/[0.08]'
                      }`}
                    >
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold ${
                        activeRole === role.name
                          ? `bg-${role.color}-500/20 text-${role.color}-400`
                          : 'bg-gray-700/40 text-gray-500'
                      }`}>
                        {role.name[0]}
                      </div>
                      <div className="text-left flex-1">
                        <p className={`text-sm font-semibold ${activeRole === role.name ? 'text-white' : 'text-gray-300'}`}>{role.name}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{role.desc}</p>
                      </div>
                      {activeRole === role.name && (
                        <span className={`text-[10px] font-bold bg-${role.color}-500/20 text-${role.color}-400 px-2 py-0.5 rounded-full uppercase`}>
                          Active
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              </div>

              {/* Neo4j Health Check */}
              <div className="glass-card p-6" style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '600ms' }}>
                <h3 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-orange-400" />
                  Neo4j AuraDB Health
                </h3>
                <div className="flex items-center gap-6">
                  <button
                    onClick={checkNeo4j}
                    disabled={neo4jLoading}
                    className="px-6 py-3 rounded-xl bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-sm font-semibold shadow-lg shadow-orange-500/20 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {neo4jLoading ? (
                      <>
                        <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                        Checking…
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
                        </svg>
                        Test Graph DB
                      </>
                    )}
                  </button>

                  {neo4jStatus && (
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <span className={`block w-4 h-4 rounded-full ${neo4jStatus === 'ok' ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                        <span className={`absolute inset-0 rounded-full ${neo4jStatus === 'ok' ? 'bg-emerald-400' : 'bg-rose-400'}`}
                          style={{ animation: 'pulse-ring 1.5s ease-out infinite' }} />
                      </div>
                      <div>
                        <p className={`text-sm font-semibold ${neo4jStatus === 'ok' ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {neo4jStatus === 'ok' ? 'AuraDB Connected' : 'Connection Failed'}
                        </p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {neo4jStatus === 'ok' ? 'Knowledge graph is accessible' : 'Could not reach Neo4j AuraDB'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* CRUD Configuration Table */}
            <div className="glass-card p-6" style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '700ms' }}>
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-violet-400" />
                  Base44 CRUD Configuration
                </h3>
                <button
                  onClick={addItem}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-xs font-semibold shadow-lg shadow-violet-500/20 transition-all duration-200 flex items-center gap-1.5"
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                  </svg>
                  Add Parameter
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/5">
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Key</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Value</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Description</th>
                      <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {crudItems.map((item) => (
                      <tr key={item.id} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition">
                        <td className="px-4 py-3 font-mono text-xs text-cyan-400">{item.key}</td>
                        <td className="px-4 py-3">
                          {editingId === item.id ? (
                            <input
                              type="text"
                              value={editValue}
                              onChange={(e) => setEditValue(e.target.value)}
                              onKeyDown={(e) => e.key === 'Enter' && saveEdit(item.id)}
                              className="w-24 px-2 py-1 rounded bg-gray-800 border border-cyan-500/30 text-xs text-gray-200 focus:outline-none focus:ring-1 focus:ring-cyan-500/40"
                              autoFocus
                            />
                          ) : (
                            <span className="text-xs text-gray-200 font-semibold">{item.value}</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-500">{item.desc}</td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            {editingId === item.id ? (
                              <button
                                onClick={() => saveEdit(item.id)}
                                className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 text-[10px] font-bold hover:bg-emerald-500/30 transition"
                              >
                                Save
                              </button>
                            ) : (
                              <button
                                onClick={() => startEdit(item)}
                                className="px-2.5 py-1 rounded-lg bg-blue-500/20 text-blue-400 text-[10px] font-bold hover:bg-blue-500/30 transition"
                              >
                                Edit
                              </button>
                            )}
                            <button
                              onClick={() => deleteItem(item.id)}
                              className="px-2.5 py-1 rounded-lg bg-rose-500/20 text-rose-400 text-[10px] font-bold hover:bg-rose-500/30 transition"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {crudItems.length === 0 && (
                      <tr>
                        <td colSpan={4} className="text-center py-8 text-gray-500 text-sm">No configurations. Click "Add Parameter" to create one.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* ─── Toast Notifications ─── */}
          <div className="fixed bottom-6 right-6 z-50 space-y-3" style={{ pointerEvents: 'none' }}>
            {toasts.map((toast) => (
              <div
                key={toast.id}
                className={`flex items-center gap-3 px-5 py-3 rounded-xl border shadow-2xl backdrop-blur-xl text-sm font-semibold pointer-events-auto ${
                  toast.type === 'success'
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                    : toast.type === 'warning'
                    ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                    : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                }`}
                style={{ animation: 'fadeInUp 0.3s ease-out both' }}
              >
                {toast.type === 'success' ? (
                  <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                ) : toast.type === 'warning' ? (
                  <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
                {toast.message}
              </div>
            ))}
          </div>
        </main>
      </div>
    </>
  );
}
