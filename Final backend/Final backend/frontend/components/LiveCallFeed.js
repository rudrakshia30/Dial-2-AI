import { useState, useEffect, useRef } from 'react';
import { apiFetch } from '../lib/api';

/* ─── sentiment → emoji helper ─── */
const sentimentEmoji = (s) => {
  if (!s) return '💬';
  const lower = s.toLowerCase();
  if (lower.includes('positive')) return '😊';
  if (lower.includes('negative')) return '😞';
  if (lower.includes('neutral')) return '😐';
  return '💬';
};

/* ─── intent → color map ─── */
const intentColor = (intent) => {
  if (!intent) return 'text-gray-400';
  const lower = intent.toLowerCase();
  if (lower.includes('weather')) return 'text-cyan-400';
  if (lower.includes('scheme') || lower.includes('government')) return 'text-violet-400';
  if (lower.includes('mandi') || lower.includes('price')) return 'text-amber-400';
  if (lower.includes('health')) return 'text-rose-400';
  if (lower.includes('education')) return 'text-blue-400';
  return 'text-emerald-400';
};

/* ─── time ago formatter ─── */
const timeAgo = (timestamp) => {
  if (!timestamp) return '';
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return 'Just now';
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  return `${Math.floor(diffHr / 24)}d ago`;
};

/* ─── mask phone number ─── */
const maskPhone = (phone) => {
  if (!phone || phone.length < 4) return phone || 'Unknown';
  return '•••• ' + phone.slice(-4);
};

export default function LiveCallFeed({ calls: externalCalls, pollInterval = 15000 }) {
  const [calls, setCalls] = useState([]);
  const [newIds, setNewIds] = useState(new Set());
  const feedRef = useRef(null);
  const prevIdsRef = useRef(new Set());

  // Use external calls if provided, otherwise poll independently
  useEffect(() => {
    if (externalCalls && externalCalls.length > 0) {
      // Detect new calls by comparing IDs
      const currentIds = new Set(externalCalls.map((c) => c.id));
      const freshIds = new Set();
      currentIds.forEach((id) => {
        if (!prevIdsRef.current.has(id)) freshIds.add(id);
      });

      if (freshIds.size > 0 && prevIdsRef.current.size > 0) {
        setNewIds(freshIds);
        // Clear the "new" highlight after 3 seconds
        setTimeout(() => setNewIds(new Set()), 3000);
      }

      prevIdsRef.current = currentIds;
      setCalls(externalCalls.slice(0, 15)); // Show last 15 calls
      return;
    }

    // Independent polling mode
    let cancelled = false;
    const fetchLogs = async () => {
      try {
        const data = await apiFetch('/api/logs');
        if (cancelled) return;
        const currentIds = new Set(data.map((c) => c.id));
        const freshIds = new Set();
        currentIds.forEach((id) => {
          if (!prevIdsRef.current.has(id)) freshIds.add(id);
        });

        if (freshIds.size > 0 && prevIdsRef.current.size > 0) {
          setNewIds(freshIds);
          setTimeout(() => setNewIds(new Set()), 3000);
        }

        prevIdsRef.current = currentIds;
        setCalls(data.slice(0, 15));
      } catch {
        // Silently fail — the dashboard already shows errors
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, pollInterval);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [externalCalls, pollInterval]);

  if (calls.length === 0) {
    return (
      <div className="glass-card p-6" style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '500ms' }}>
        <div className="flex items-center gap-2 mb-4">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
          </span>
          <h2 className="text-lg font-semibold text-white">Live Activity</h2>
        </div>
        <p className="text-gray-500 text-sm text-center py-6">Waiting for incoming calls…</p>
      </div>
    );
  }

  return (
    <div className="glass-card p-6" style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '500ms' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
          </span>
          <h2 className="text-lg font-semibold text-white">Live Activity</h2>
        </div>
        <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20">
          Live
        </span>
      </div>

      {/* Feed */}
      <div
        ref={feedRef}
        className="space-y-2 max-h-[380px] overflow-y-auto pr-1"
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: 'rgba(255,255,255,0.08) transparent',
        }}
      >
        {calls.map((call, idx) => {
          const isNew = newIds.has(call.id);
          return (
            <div
              key={call.id}
              className={`relative flex items-center gap-3 p-3 rounded-xl transition-all duration-500 ${
                isNew
                  ? 'bg-emerald-500/10 border border-emerald-500/20'
                  : 'bg-gray-800/30 border border-white/[0.03] hover:border-white/[0.08]'
              }`}
              style={{
                animation: isNew ? 'fadeInUp 0.4s ease-out both' : `fadeInUp 0.4s ease-out both`,
                animationDelay: isNew ? '0ms' : `${idx * 60}ms`,
              }}
            >
              {/* Sentiment Emoji */}
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gray-800/60 text-lg shrink-0">
                {sentimentEmoji(call.sentiment)}
              </div>

              {/* Details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-gray-200 truncate">
                    {call.customer_name || maskPhone(call.phone_number)}
                  </span>
                  {call.location && (
                    <span className="text-[10px] text-gray-500 truncate hidden sm:inline">
                      📍 {call.location}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  {call.intent && (
                    <span className={`text-xs font-medium ${intentColor(call.intent)} truncate`}>
                      {call.intent}
                    </span>
                  )}
                  {call.duration && (
                    <span className="text-[10px] text-gray-600">
                      {call.duration}s
                    </span>
                  )}
                </div>
              </div>

              {/* Status + Time */}
              <div className="flex flex-col items-end shrink-0 gap-1">
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                    call.status === 'success'
                      ? 'bg-emerald-500/15 text-emerald-400'
                      : call.status === 'failed'
                      ? 'bg-rose-500/15 text-rose-400'
                      : 'bg-gray-600/20 text-gray-400'
                  }`}
                >
                  {call.status || 'pending'}
                </span>
                <span className="text-[10px] text-gray-600 tabular-nums">
                  {timeAgo(call.timestamp)}
                </span>
              </div>

              {/* New indicator pulse */}
              {isNew && (
                <span className="absolute top-1.5 right-1.5 flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400" />
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="mt-3 pt-3 border-t border-white/[0.04] flex items-center justify-between">
        <span className="text-[10px] text-gray-600">
          Showing {calls.length} most recent calls
        </span>
        <span className="text-[10px] text-gray-600 tabular-nums">
          Refreshes every {pollInterval / 1000}s
        </span>
      </div>
    </div>
  );
}
