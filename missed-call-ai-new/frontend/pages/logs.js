import { useState, useEffect, useMemo } from 'react';
import Sidebar from '../components/Sidebar';
import ShareModal from '../components/ShareModal';
import CallDetailModal from '../components/CallDetailModal';
import { LogsSkeleton } from '../components/LoadingSkeleton';
import { apiFetch } from '../lib/api';

const PER_PAGE = 15;

/* ─── badge helpers ─── */
const sentimentStyle = {
  Positive: 'bg-emerald-500/15 text-emerald-400 ring-emerald-500/30',
  Neutral: 'bg-blue-500/15 text-blue-400 ring-blue-500/30',
  Negative: 'bg-rose-500/15 text-rose-400 ring-rose-500/30',
};

function SentimentBadge({ value }) {
  const s = sentimentStyle[value] || sentimentStyle.Neutral;
  return (
    <span className={`inline-flex items-center text-xs font-semibold px-2.5 py-0.5 rounded-full ring-1 ${s}`}>
      {value || 'Unknown'}
    </span>
  );
}

function StatusDot({ status }) {
  const isSuccess = status?.toLowerCase() === 'success';
  return (
    <span className="flex items-center gap-1.5 text-xs font-medium">
      <span className={`w-2 h-2 rounded-full ${isSuccess ? 'bg-emerald-400' : 'bg-rose-400'}`} />
      <span className={isSuccess ? 'text-emerald-400' : 'text-rose-400'}>{status || '—'}</span>
    </span>
  );
}

export default function Logs() {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /* filters */
  const [search, setSearch] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');

  /* modals */
  const [shareOpen, setShareOpen] = useState(false);
  const [detailCall, setDetailCall] = useState(null);

  /* pagination */
  const [page, setPage] = useState(1);

  useEffect(() => {
    apiFetch('/api/logs')
      .then((data) => {
        setCalls(data);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  /* filtered list */
  const filtered = useMemo(() => {
    let list = calls;
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(
        (c) =>
          (c.customer_name || '').toLowerCase().includes(q) ||
          (c.phone_number || '').toLowerCase().includes(q) ||
          (c.intent || '').toLowerCase().includes(q) ||
          (c.summary_text || '').toLowerCase().includes(q)
      );
    }
    if (sentimentFilter !== 'All') {
      list = list.filter((c) => c.sentiment === sentimentFilter);
    }
    if (statusFilter !== 'All') {
      list = list.filter((c) => (c.status || '').toLowerCase() === statusFilter.toLowerCase());
    }
    return list;
  }, [calls, search, sentimentFilter, statusFilter]);

  /* reset page on filter change */
  useEffect(() => {
    setPage(1);
  }, [search, sentimentFilter, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  const start = (page - 1) * PER_PAGE;
  const pageItems = filtered.slice(start, start + PER_PAGE);

  const formatDate = (ts) => {
    if (!ts) return '—';
    const d = new Date(ts);
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) +
      ' ' +
      d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      <style jsx global>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(18px); }
          to { opacity: 1; transform: translateY(0); }
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

        <main className="flex-1 ml-64 p-8 overflow-y-auto" style={{ animation: 'fadeInUp 0.5s ease-out' }}>
          {/* ─── Header Bar ─── */}
          <div className="flex flex-wrap items-center gap-4 mb-8">
            <h1 className="text-3xl font-extrabold tracking-tight mr-auto">
              <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                Call Logs
              </span>
            </h1>

            {/* Search */}
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
              <input
                type="text"
                placeholder="Search calls…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 pr-4 py-2.5 w-64 rounded-xl bg-gray-800/60 backdrop-blur border border-white/10 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 transition"
              />
            </div>

            {/* Sentiment filter */}
            <select
              value={sentimentFilter}
              onChange={(e) => setSentimentFilter(e.target.value)}
              className="py-2.5 px-4 rounded-xl bg-gray-800/60 backdrop-blur border border-white/10 text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 appearance-none cursor-pointer"
            >
              <option value="All">All Sentiments</option>
              <option value="Positive">Positive</option>
              <option value="Neutral">Neutral</option>
              <option value="Negative">Negative</option>
            </select>

            {/* Status filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="py-2.5 px-4 rounded-xl bg-gray-800/60 backdrop-blur border border-white/10 text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 appearance-none cursor-pointer"
            >
              <option value="All">All Statuses</option>
              <option value="Success">Success</option>
              <option value="Failed">Failed</option>
            </select>

            {/* Share All */}
            <button
              onClick={() => setShareOpen(true)}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-sm font-semibold shadow-lg shadow-cyan-500/20 transition-all duration-200"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M7.217 10.907a2.25 2.25 0 100 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186l9.566-5.314m-9.566 7.5l9.566 5.314m0 0a2.25 2.25 0 103.935 2.186 2.25 2.25 0 00-3.935-2.186zm0-12.814a2.25 2.25 0 103.933-2.185 2.25 2.25 0 00-3.933 2.185z" />
              </svg>
              Share Logs
            </button>
          </div>

          {/* ─── Loading ─── */}
          {loading && <LogsSkeleton />}

          {/* ─── Error ─── */}
          {error && !loading && (
            <div className="glass-card p-6 border-l-4 border-rose-500 mb-6">
              <p className="text-rose-300 font-medium">Failed to load logs</p>
              <p className="text-gray-400 text-sm mt-1">{error}</p>
            </div>
          )}

          {/* ─── Table ─── */}
          {!loading && !error && (
            <>
              <div className="glass-card overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/5">
                        {['Customer', 'Phone', 'Intent', 'Summary', 'Sentiment', 'Status', 'Lead', 'Date'].map((h) => (
                          <th key={h} className="px-5 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {pageItems.length > 0 ? (
                        pageItems.map((call, idx) => (
                          <tr
                            key={call.id || idx}
                            onClick={() => setDetailCall(call)}
                            className={`border-b border-white/[0.03] cursor-pointer transition-colors hover:bg-white/[0.04] ${
                              idx % 2 === 0 ? 'bg-transparent' : 'bg-white/[0.015]'
                            }`}
                          >
                            <td className="px-5 py-3.5 text-gray-200 font-medium whitespace-nowrap">
                              {call.customer_name || '—'}
                            </td>
                            <td className="px-5 py-3.5 text-gray-300 whitespace-nowrap font-mono text-xs">
                              {call.phone_number || '—'}
                            </td>
                            <td className="px-5 py-3.5 text-gray-300 whitespace-nowrap">
                              {call.intent || '—'}
                            </td>
                            <td className="px-5 py-3.5 text-gray-400 max-w-[220px] truncate">
                              {call.summary_text || '—'}
                            </td>
                            <td className="px-5 py-3.5">
                              <SentimentBadge value={call.sentiment} />
                            </td>
                            <td className="px-5 py-3.5">
                              <StatusDot status={call.status} />
                            </td>
                            <td className="px-5 py-3.5">
                              {call.lead_json ? (
                                <span className="inline-flex items-center gap-1 text-xs font-semibold text-amber-400">
                                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                                  </svg>
                                  Lead
                                </span>
                              ) : (
                                <span className="text-gray-600 text-xs">—</span>
                              )}
                            </td>
                            <td className="px-5 py-3.5 text-gray-400 whitespace-nowrap text-xs">
                              {formatDate(call.timestamp)}
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={8} className="px-5 py-16 text-center">
                            <svg className="w-12 h-12 text-gray-700 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m6 4.125l2.25 2.25m0 0l2.25 2.25M12 13.875l2.25-2.25M12 13.875l-2.25 2.25M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
                            </svg>
                            <p className="text-gray-500 font-medium">No results found</p>
                            <p className="text-gray-600 text-xs mt-1">Try adjusting your search or filters</p>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* ─── Pagination Footer ─── */}
              <div className="flex items-center justify-between mt-5 px-1">
                <p className="text-sm text-gray-500">
                  Showing{' '}
                  <span className="text-gray-300 font-medium">{filtered.length > 0 ? start + 1 : 0}</span>
                  –
                  <span className="text-gray-300 font-medium">{Math.min(start + PER_PAGE, filtered.length)}</span>
                  {' '}of{' '}
                  <span className="text-gray-300 font-medium">{filtered.length}</span> results
                </p>
                <div className="flex items-center gap-2">
                  <button
                    disabled={page <= 1}
                    onClick={() => setPage((p) => p - 1)}
                    className="px-4 py-2 rounded-lg bg-gray-800/60 border border-white/10 text-sm font-medium text-gray-300 hover:bg-gray-700/60 disabled:opacity-30 disabled:cursor-not-allowed transition"
                  >
                    ← Prev
                  </button>
                  <span className="text-sm text-gray-400">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    disabled={page >= totalPages}
                    onClick={() => setPage((p) => p + 1)}
                    className="px-4 py-2 rounded-lg bg-gray-800/60 border border-white/10 text-sm font-medium text-gray-300 hover:bg-gray-700/60 disabled:opacity-30 disabled:cursor-not-allowed transition"
                  >
                    Next →
                  </button>
                </div>
              </div>
            </>
          )}
        </main>
      </div>

      {/* ─── Modals ─── */}
      <ShareModal isOpen={shareOpen} onClose={() => setShareOpen(false)} calls={filtered} />
      <CallDetailModal isOpen={!!detailCall} onClose={() => setDetailCall(null)} call={detailCall} />
    </>
  );
}
