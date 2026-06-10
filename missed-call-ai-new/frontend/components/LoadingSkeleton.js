/**
 * Loading skeleton components with shimmer animations
 * Uses the shimmer animation defined in globals.css
 */

function SkeletonBlock({ className = '' }) {
  return <div className={`skeleton ${className}`} />;
}

/**
 * Dashboard loading skeleton
 * Mimics: stat cards row + chart + table
 */
export function DashboardSkeleton() {
  return (
    <div className="animate-fade-in space-y-8">
      {/* Heading skeleton */}
      <SkeletonBlock className="h-8 w-48" />

      {/* Stat cards row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="glass-card p-5 space-y-3"
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <div className="flex items-center justify-between">
              <SkeletonBlock className="h-8 w-8 rounded-lg" />
              <SkeletonBlock className="h-5 w-12 rounded-full" />
            </div>
            <SkeletonBlock className="h-3 w-20" />
            <SkeletonBlock className="h-7 w-16" />
          </div>
        ))}
      </div>

      {/* Two-column section (Sentiment + Intents) */}
      <div className="grid md:grid-cols-2 gap-8">
        <div className="glass-card p-6 space-y-4">
          <SkeletonBlock className="h-5 w-40" />
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="flex justify-between">
                  <SkeletonBlock className="h-3 w-16" />
                  <SkeletonBlock className="h-3 w-8" />
                </div>
                <SkeletonBlock className="h-2 w-full rounded-full" />
              </div>
            ))}
          </div>
        </div>
        <div className="glass-card p-6 space-y-4">
          <SkeletonBlock className="h-5 w-40" />
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex justify-between items-center py-2">
                <SkeletonBlock className="h-4 w-32" />
                <SkeletonBlock className="h-6 w-16 rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Chart area */}
      <div className="glass-card p-6 space-y-4">
        <SkeletonBlock className="h-5 w-36" />
        <SkeletonBlock className="h-64 w-full rounded-xl" />
      </div>

      {/* Table */}
      <div className="glass-card p-6 space-y-4">
        <SkeletonBlock className="h-5 w-32" />
        <div className="space-y-0">
          {/* Table header */}
          <div className="flex gap-4 pb-3 border-b border-white/[0.06]">
            {[80, 180, 80, 80, 80].map((w, i) => (
              <SkeletonBlock key={i} className="h-3" style={{ width: w }} />
            ))}
          </div>
          {/* Table rows */}
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="flex gap-4 py-4 border-b border-white/[0.03]"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <SkeletonBlock className="h-4 w-24" />
              <SkeletonBlock className="h-4 w-44" />
              <SkeletonBlock className="h-4 w-20" />
              <SkeletonBlock className="h-5 w-16 rounded-full" />
              <SkeletonBlock className="h-5 w-16 rounded-full" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * Logs page loading skeleton
 * Mimics: search bar + full table
 */
export function LogsSkeleton() {
  return (
    <div className="animate-fade-in space-y-6">
      {/* Heading */}
      <SkeletonBlock className="h-8 w-56" />

      {/* Search bar */}
      <SkeletonBlock className="h-12 w-full rounded-xl" />

      {/* Table */}
      <div className="glass-card overflow-hidden">
        {/* Header */}
        <div className="flex gap-6 px-5 py-4 border-b border-white/[0.06]">
          {['w-20', 'w-16', 'w-16', 'w-32', 'w-20', 'w-24', 'w-16'].map((w, i) => (
            <SkeletonBlock key={i} className={`h-3 ${w}`} />
          ))}
        </div>

        {/* Rows */}
        {[...Array(10)].map((_, i) => (
          <div
            key={i}
            className="flex gap-6 px-5 py-4 border-b border-white/[0.03]"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <SkeletonBlock className="h-4 w-24" />
            <SkeletonBlock className="h-4 w-28" />
            <SkeletonBlock className="h-4 w-20" />
            <SkeletonBlock className="h-4 w-40" />
            <SkeletonBlock className="h-5 w-16 rounded-full" />
            <SkeletonBlock className="h-10 w-28 rounded" />
            <SkeletonBlock className="h-4 w-24" />
          </div>
        ))}
      </div>
    </div>
  );
}
