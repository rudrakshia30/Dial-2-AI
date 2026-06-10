import { useState, useEffect, useCallback } from 'react';
import Sidebar from '../components/Sidebar';
import StatCard from '../components/StatCard';
import CallTable from '../components/CallTable';
import { DashboardSkeleton } from '../components/LoadingSkeleton';
import { apiFetch } from '../lib/api';
import {
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

/* ───────── custom recharts tooltip ───────── */
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900/90 backdrop-blur-xl border border-white/10 rounded-xl px-4 py-3 shadow-2xl">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-sm font-semibold text-cyan-400">{payload[0].value} calls</p>
    </div>
  );
}

/* ───────── inline SVG icons ───────── */
const PhoneIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 01-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z" />
  </svg>
);
const CheckIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);
const XIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);
const ClockIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);
const StarIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
  </svg>
);

/* ───────── animation wrapper ───────── */
function FadeIn({ delay = 0, children, className = '' }) {
  return (
    <div
      className={className}
      style={{
        animation: 'fadeInUp 0.6s ease-out both',
        animationDelay: `${delay}ms`,
      }}
    >
      {children}
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const [statsData, logsData] = await Promise.all([
        apiFetch('/api/stats'),
        apiFetch('/api/logs'),
      ]);
      setStats(statsData);
      setCalls(logsData);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  /* ─── sentiment helpers ─── */
  const sentimentTotal = stats
    ? (stats.sentiment_dist?.Positive || 0) +
      (stats.sentiment_dist?.Neutral || 0) +
      (stats.sentiment_dist?.Negative || 0)
    : 0;

  const sentimentPct = (key) =>
    sentimentTotal > 0
      ? Math.round(((stats?.sentiment_dist?.[key] || 0) / sentimentTotal) * 100)
      : 0;

  /* ─── top intents max ─── */
  const maxIntentCount = stats?.top_intents?.length
    ? Math.max(...stats.top_intents.map((i) => i.count))
    : 1;

  return (
    <>
      {/* keyframe injection */}
      <style jsx global>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(18px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes growWidth {
          from { width: 0%; }
        }
        .glass-card {
          background: rgba(17, 24, 39, 0.6);
          backdrop-filter: blur(16px);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 1rem;
        }
      `}</style>

      <div className="flex min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
        <Sidebar />

        <main className="flex-1 ml-64 p-8 overflow-y-auto">
          {/* Header */}
          <FadeIn>
            <div className="mb-8">
              <h1 className="text-3xl font-extrabold tracking-tight">
                <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                  Dashboard
                </span>
              </h1>
              <p className="text-gray-400 mt-1 text-sm">
                Real-time overview of your missed call AI system
              </p>
            </div>
          </FadeIn>

          {/* Loading */}
          {loading && <DashboardSkeleton />}

          {/* Error */}
          {error && !loading && (
            <FadeIn>
              <div className="glass-card p-6 border-l-4 border-rose-500 mb-8">
                <div className="flex items-center gap-3">
                  <svg className="w-6 h-6 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                  </svg>
                  <div>
                    <h3 className="text-rose-300 font-semibold">Connection Error</h3>
                    <p className="text-gray-400 text-sm mt-0.5">{error}</p>
                  </div>
                  <button
                    onClick={fetchData}
                    className="ml-auto px-4 py-2 rounded-lg bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 transition text-sm font-medium"
                  >
                    Retry
                  </button>
                </div>
              </div>
            </FadeIn>
          )}

          {/* Main content */}
          {!loading && stats && (
            <>
              {/* ─── Stat Cards ─── */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5 mb-8">
                <FadeIn delay={80}>
                  <StatCard
                    title="Total Calls"
                    value={stats.total_today ?? 0}
                    icon={PhoneIcon}
                    color="border-cyan-500"
                  />
                </FadeIn>
                <FadeIn delay={160}>
                  <StatCard
                    title="Successful"
                    value={stats.success_today ?? 0}
                    icon={CheckIcon}
                    color="border-emerald-500"
                    change={
                      stats.total_today
                        ? `${Math.round(((stats.success_today || 0) / stats.total_today) * 100)}%`
                        : undefined
                    }
                  />
                </FadeIn>
                <FadeIn delay={240}>
                  <StatCard
                    title="Failed"
                    value={stats.failed_today ?? 0}
                    icon={XIcon}
                    color="border-rose-500"
                  />
                </FadeIn>
                <FadeIn delay={320}>
                  <StatCard
                    title="Avg Duration"
                    value={`${stats.avg_duration ?? 0}s`}
                    icon={ClockIcon}
                    color="border-violet-500"
                  />
                </FadeIn>
                <FadeIn delay={400}>
                  <StatCard
                    title="Leads Generated"
                    value={stats.leads_count ?? 0}
                    icon={StarIcon}
                    color="border-amber-500"
                  />
                </FadeIn>
              </div>

              {/* ─── Charts Row ─── */}
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
                {/* Calls Per Hour Chart */}
                <FadeIn delay={480} className="xl:col-span-2">
                  <div className="glass-card p-6">
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-cyan-400" />
                      Calls Per Hour
                    </h2>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={stats.calls_per_hour || []} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                          <defs>
                            <linearGradient id="callsGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.4} />
                              <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis
                            dataKey="hour"
                            tick={{ fill: '#9ca3af', fontSize: 12 }}
                            axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
                            tickLine={false}
                          />
                          <YAxis
                            tick={{ fill: '#9ca3af', fontSize: 12 }}
                            axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
                            tickLine={false}
                            allowDecimals={false}
                          />
                          <Tooltip content={<CustomTooltip />} />
                          <Area
                            type="monotone"
                            dataKey="count"
                            stroke="#06b6d4"
                            strokeWidth={2.5}
                            fill="url(#callsGradient)"
                            dot={false}
                            activeDot={{ r: 5, fill: '#06b6d4', stroke: '#fff', strokeWidth: 2 }}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </FadeIn>

                {/* Sentiment Distribution */}
                <FadeIn delay={560}>
                  <div className="glass-card p-6 flex flex-col">
                    <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-violet-400" />
                      Sentiment Distribution
                    </h2>
                    <div className="space-y-5 flex-1 flex flex-col justify-center">
                      {[
                        { key: 'Positive', gradient: 'from-emerald-500 to-emerald-400', text: 'text-emerald-400' },
                        { key: 'Neutral', gradient: 'from-blue-500 to-blue-400', text: 'text-blue-400' },
                        { key: 'Negative', gradient: 'from-rose-500 to-rose-400', text: 'text-rose-400' },
                      ].map(({ key, gradient, text }) => (
                        <div key={key}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-300 font-medium">{key}</span>
                            <span className={`text-sm font-bold ${text}`}>{sentimentPct(key)}%</span>
                          </div>
                          <div className="w-full h-3 rounded-full bg-gray-800/80 overflow-hidden">
                            <div
                              className={`h-full rounded-full bg-gradient-to-r ${gradient}`}
                              style={{
                                width: `${sentimentPct(key)}%`,
                                animation: 'growWidth 1s ease-out both',
                                animationDelay: '0.6s',
                              }}
                            />
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {stats.sentiment_dist?.[key] ?? 0} calls
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </FadeIn>
              </div>

              {/* ─── Intents + Recent Calls ─── */}
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                {/* Top Intents */}
                <FadeIn delay={640}>
                  <div className="glass-card p-6">
                    <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-amber-400" />
                      Top Intents
                    </h2>
                    <div className="space-y-3">
                      {(stats.top_intents || []).map((item, idx) => (
                        <div
                          key={item.intent}
                          className="relative flex items-center justify-between py-2 px-3 rounded-lg bg-gray-800/40"
                          style={{ animation: 'fadeInUp 0.5s ease-out both', animationDelay: `${700 + idx * 80}ms` }}
                        >
                          {/* bar background */}
                          <div
                            className="absolute inset-0 rounded-lg bg-gradient-to-r from-amber-500/10 to-transparent"
                            style={{ width: `${(item.count / maxIntentCount) * 100}%` }}
                          />
                          <span className="relative text-sm text-gray-200 font-medium truncate mr-3">{item.intent}</span>
                          <span className="relative text-xs font-bold text-amber-400 bg-amber-500/15 rounded-full px-2.5 py-0.5 shrink-0">
                            {item.count}
                          </span>
                        </div>
                      ))}
                      {(!stats.top_intents || stats.top_intents.length === 0) && (
                        <p className="text-gray-500 text-sm text-center py-4">No intents recorded yet</p>
                      )}
                    </div>
                  </div>
                </FadeIn>

                {/* Recent Calls */}
                <FadeIn delay={720} className="xl:col-span-2">
                  <div className="glass-card p-6">
                    <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      Recent Calls
                    </h2>
                    {calls.length > 0 ? (
                      <CallTable calls={calls.slice(0, 5)} />
                    ) : (
                      <p className="text-gray-500 text-sm text-center py-8">No calls recorded yet</p>
                    )}
                  </div>
                </FadeIn>
              </div>
            </>
          )}
        </main>
      </div>
    </>
  );
}
