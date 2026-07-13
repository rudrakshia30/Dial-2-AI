import { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import { DashboardSkeleton } from '../components/LoadingSkeleton';
import { apiFetch } from '../lib/api';
import GraphVisualizer from '../components/GraphVisualizer';
import {
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  BarChart,
  Bar,
} from 'recharts';

/* ─── Custom tooltips ─── */
function AreaTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900/90 backdrop-blur-xl border border-white/10 rounded-xl px-4 py-3 shadow-2xl">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-sm font-semibold text-cyan-400">{payload[0].value} calls</p>
    </div>
  );
}

function PieTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900/90 backdrop-blur-xl border border-white/10 rounded-xl px-4 py-3 shadow-2xl">
      <p className="text-sm font-semibold" style={{ color: payload[0].payload.fill }}>
        {payload[0].name}: {payload[0].value}
      </p>
    </div>
  );
}

function BarTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900/90 backdrop-blur-xl border border-white/10 rounded-xl px-4 py-3 shadow-2xl">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-sm font-semibold text-amber-400">{payload[0].value} calls</p>
    </div>
  );
}

/* ─── Pie custom legend ─── */
function CustomLegend({ payload }) {
  return (
    <div className="flex items-center justify-center gap-6 mt-4">
      {(payload || []).map((entry) => (
        <div key={entry.value} className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-sm text-gray-300">{entry.value}</span>
        </div>
      ))}
    </div>
  );
}

/* ─── Metric card ─── */
function MetricCard({ title, value, subtitle, color, delay = 0 }) {
  return (
    <div
      className="glass-card p-6 flex flex-col"
      style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: `${delay}ms` }}
    >
      <p className="text-sm text-gray-400 font-medium mb-2">{title}</p>
      <p className={`text-3xl font-extrabold ${color}`}>{value}</p>
      {subtitle && <p className="text-xs text-gray-500 mt-2">{subtitle}</p>}
    </div>
  );
}

const SENTIMENT_COLORS = {
  Positive: '#10b981',
  Neutral: '#3b82f6',
  Negative: '#f43f5e',
};

export default function Analytics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [neo4jStats, setNeo4jStats] = useState(null);
  const [neo4jLoading, setNeo4jLoading] = useState(true);

  useEffect(() => {
    // Fetch SQLite metrics
    apiFetch('/api/stats')
      .then((data) => {
        setStats(data);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));

    // Fetch Neo4j AuraDB Live Graph metrics
    apiFetch('/api/neo4j/stats')
      .then((data) => {
        setNeo4jStats(data);
      })
      .catch((err) => console.error("Neo4j stats fetch error:", err))
      .finally(() => setNeo4jLoading(false));
  }, []);

  /* derived data */
  const sentimentData = stats
    ? Object.entries(stats.sentiment_dist || {}).map(([name, value]) => ({
      name,
      value,
      fill: SENTIMENT_COLORS[name] || '#6b7280',
    }))
    : [];

  const sentimentTotal = sentimentData.reduce((s, d) => s + d.value, 0);

  const intentData = (stats?.top_intents || []).map((i) => ({
    name: i.intent,
    count: i.count,
  }));

  const successRate =
    stats && stats.total_today > 0
      ? Math.round(((stats.success_today || 0) / stats.total_today) * 100)
      : 0;

  const leadConversionRate =
    stats && stats.total_today > 0
      ? Math.round(((stats.leads_count || 0) / stats.total_today) * 100)
      : 0;

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

        <main className="flex-1 ml-0 lg:ml-64 p-4 pt-16 lg:pt-8 lg:p-8 overflow-y-auto">
          {/* Header */}
          <div className="mb-8 flex items-end justify-between" style={{ animation: 'fadeInUp 0.5s ease-out' }}>
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight">
                <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                  Analytics
                </span>
              </h1>
              <p className="text-gray-400 mt-1 text-sm">Deep dive into your call data and performance metrics</p>
            </div>
            <span className="text-[10px] font-bold bg-violet-500/10 text-violet-400 px-2.5 py-1 rounded border border-violet-500/20 uppercase tracking-widest">
              Powered by Base44
            </span>
          </div>

          {loading && <DashboardSkeleton />}

          {error && !loading && (
            <div className="glass-card p-6 border-l-4 border-rose-500 mb-6" style={{ animation: 'fadeInUp 0.5s ease-out' }}>
              <p className="text-rose-300 font-medium">Failed to load analytics</p>
              <p className="text-gray-400 text-sm mt-1">{error}</p>
            </div>
          )}

          {!loading && stats && (
            <>
              {/* ─── Key Metrics ─── */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
                <MetricCard
                  title="Total Calls Today"
                  value={stats.total_today ?? 0}
                  subtitle="All incoming missed calls"
                  color="text-cyan-400"
                  delay={80}
                />
                <MetricCard
                  title="Success Rate"
                  value={`${successRate}%`}
                  subtitle={`${stats.success_today ?? 0} of ${stats.total_today ?? 0} calls`}
                  color="text-emerald-400"
                  delay={160}
                />
                <MetricCard
                  title="Avg Duration"
                  value={`${stats.avg_duration ?? 0}s`}
                  subtitle="Average call duration"
                  color="text-violet-400"
                  delay={240}
                />
                <MetricCard
                  title="Lead Conversion"
                  value={`${leadConversionRate}%`}
                  subtitle={`${stats.leads_count ?? 0} leads generated`}
                  color="text-amber-400"
                  delay={320}
                />
              </div>

              {/* ─── Charts Row 1 ─── */}
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
                {/* Call Volume */}
                <div
                  className="glass-card p-6 xl:col-span-2"
                  style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '400ms' }}
                >
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-cyan-400" />
                    Call Volume
                  </h2>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={stats.calls_per_hour || []} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                        <defs>
                          <linearGradient id="analyticsGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.35} />
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
                        <Tooltip content={<AreaTooltip />} />
                        <Area
                          type="monotone"
                          dataKey="count"
                          stroke="#06b6d4"
                          strokeWidth={2.5}
                          fill="url(#analyticsGradient)"
                          dot={false}
                          activeDot={{ r: 5, fill: '#06b6d4', stroke: '#fff', strokeWidth: 2 }}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Sentiment Pie */}
                <div
                  className="glass-card p-6"
                  style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '480ms' }}
                >
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-violet-400" />
                    Sentiment Breakdown
                  </h2>
                  {sentimentTotal > 0 ? (
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={sentimentData}
                            cx="50%"
                            cy="45%"
                            innerRadius={55}
                            outerRadius={90}
                            paddingAngle={4}
                            dataKey="value"
                            stroke="none"
                          >
                            {sentimentData.map((entry, index) => (
                              <Cell key={index} fill={entry.fill} />
                            ))}
                          </Pie>
                          <Tooltip content={<PieTooltip />} />
                          <Legend content={<CustomLegend />} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="h-72 flex items-center justify-center text-gray-500 text-sm">
                      No sentiment data available
                    </div>
                  )}
                </div>
              </div>

              {/* ─── Neo4j AuraDB Graph Analytics ─── */}
              <div className="mb-8" style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '520ms' }}>
                <div className="flex items-center gap-3 mb-6">
                  <span className="px-2.5 py-1 text-xs font-semibold tracking-wider text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
                    AuraDB Live Graph
                  </span>
                  <h2 className="text-xl font-bold text-white">Relationship-Based Call Analytics</h2>
                </div>

                {/* Graph Card Metrics */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
                  <div className="glass-card p-6 flex flex-col">
                    <p className="text-xs text-gray-400 font-medium mb-1 uppercase tracking-wider">Graph Nodes: Callers</p>
                    <p className="text-2xl font-extrabold text-cyan-400">{neo4jStats?.callers ?? 0}</p>
                    <p className="text-xs text-gray-500 mt-1">Unique Person nodes</p>
                  </div>
                  <div className="glass-card p-6 flex flex-col">
                    <p className="text-xs text-gray-400 font-medium mb-1 uppercase tracking-wider">Graph Nodes: Topics</p>
                    <p className="text-2xl font-extrabold text-violet-400">{neo4jStats?.topics ?? 0}</p>
                    <p className="text-xs text-gray-500 mt-1">Unique Topic nodes</p>
                  </div>
                  <div className="glass-card p-6 flex flex-col">
                    <p className="text-xs text-gray-400 font-medium mb-1 uppercase tracking-wider">Graph Nodes: Cities</p>
                    <p className="text-2xl font-extrabold text-amber-400">{neo4jStats?.cities ?? 0}</p>
                    <p className="text-xs text-gray-500 mt-1">Unique City nodes</p>
                  </div>
                  <div className="glass-card p-6 flex flex-col">
                    <p className="text-xs text-gray-400 font-medium mb-1 uppercase tracking-wider">Graph Edges: Relationships</p>
                    <p className="text-2xl font-extrabold text-emerald-400">{neo4jStats?.relationships ?? 0}</p>
                    <p className="text-xs text-gray-500 mt-1">LIVES_IN & INTERESTED_IN links</p>
                  </div>
                </div>

                {/* Interactive Network Graph Visualizer */}
                <div className="glass-card p-6 mb-6">
                  <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                    Interactive Neo4j Knowledge Graph (AuraDB Live Nodes & Edges)
                  </h3>
                  <GraphVisualizer />
                </div>

                {/* Graph Sub-breakdown lists */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Top Topics in Graph */}
                  <div className="glass-card p-6">
                    <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
                      Top Interests in Graph (INTERESTED_IN)
                    </h3>
                    {neo4jStats?.top_topics?.length > 0 ? (
                      <div className="space-y-3">
                        {neo4jStats.top_topics.map((topic, i) => (
                          <div key={i} className="flex items-center justify-between text-sm py-1 border-b border-white/5 last:border-0">
                            <span className="text-gray-200 font-medium">#{i + 1} {topic.name}</span>
                            <span className="text-violet-400 font-semibold">{topic.count} callers</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-xs py-4 text-center">No topic relationships mapped yet</p>
                    )}
                  </div>

                  {/* Top Cities in Graph */}
                  <div className="glass-card p-6">
                    <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                      Caller Distribution by City (LIVES_IN)
                    </h3>
                    {neo4jStats?.top_cities?.length > 0 ? (
                      <div className="space-y-3">
                        {neo4jStats.top_cities.map((city, i) => (
                          <div key={i} className="flex items-center justify-between text-sm py-1 border-b border-white/5 last:border-0">
                            <span className="text-gray-200 font-medium">{city.name}</span>
                            <span className="text-amber-400 font-semibold">{city.count} callers</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-xs py-4 text-center">No city relationships mapped yet</p>
                    )}
                  </div>
                </div>
              </div>

              {/* ─── Intent Distribution ─── */}
              <div
                className="glass-card p-6"
                style={{ animation: 'fadeInUp 0.6s ease-out both', animationDelay: '600ms' }}
              >
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400" />
                  Intent Distribution
                </h2>
                {intentData.length > 0 ? (
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={intentData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
                        <defs>
                          <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
                            <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.8} />
                            <stop offset="100%" stopColor="#f97316" stopOpacity={0.6} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                        <XAxis
                          type="number"
                          tick={{ fill: '#9ca3af', fontSize: 12 }}
                          axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
                          tickLine={false}
                          allowDecimals={false}
                        />
                        <YAxis
                          type="category"
                          dataKey="name"
                          tick={{ fill: '#d1d5db', fontSize: 12 }}
                          axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
                          tickLine={false}
                          width={120}
                        />
                        <Tooltip content={<BarTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                        <Bar dataKey="count" fill="url(#barGradient)" radius={[0, 6, 6, 0]} barSize={24} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-40 flex items-center justify-center text-gray-500 text-sm">
                    No intent data available
                  </div>
                )}
              </div>
            </>
          )}
        </main>
      </div>
    </>
  );
}
