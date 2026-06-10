import { useEffect, useRef, useState } from 'react';

export default function StatCard({ title, value, color, icon, change }) {
  const [displayValue, setDisplayValue] = useState(value);
  const [animated, setAnimated] = useState(false);
  const cardRef = useRef(null);

  // Animate number entrance
  useEffect(() => {
    setAnimated(false);
    const timer = setTimeout(() => {
      setDisplayValue(value);
      setAnimated(true);
    }, 100);
    return () => clearTimeout(timer);
  }, [value]);

  // Map old color prop to new accent border colors
  const borderColorMap = {
    'bg-blue-700': 'border-l-brand-500',
    'bg-green-700': 'border-l-green-500',
    'bg-red-700': 'border-l-red-500',
    'bg-purple-700': 'border-l-accent-500',
    'bg-amber-700': 'border-l-amber-500',
  };
  const borderClass = borderColorMap[color] || 'border-l-brand-500';

  const glowColorMap = {
    'bg-blue-700': 'rgba(6,182,212,0.08)',
    'bg-green-700': 'rgba(34,197,94,0.08)',
    'bg-red-700': 'rgba(239,68,68,0.08)',
    'bg-purple-700': 'rgba(139,92,246,0.08)',
    'bg-amber-700': 'rgba(245,158,11,0.08)',
  };
  const glowColor = glowColorMap[color] || 'rgba(6,182,212,0.08)';

  return (
    <div
      ref={cardRef}
      className={`
        glass-card-hover relative overflow-hidden
        border-l-[3px] ${borderClass}
        p-5 group cursor-default
      `}
    >
      {/* Subtle gradient overlay */}
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
        style={{
          background: `radial-gradient(ellipse at top left, ${glowColor}, transparent 70%)`,
        }}
      />

      <div className="relative z-10">
        {/* Header row: icon + change */}
        <div className="flex items-center justify-between mb-3">
          {icon ? (
            <div className="text-gray-500 group-hover:text-brand-400 transition-colors duration-300">
              {icon}
            </div>
          ) : (
            <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">
              <div className={`w-2 h-2 rounded-full ${color || 'bg-brand-500'}`} />
            </div>
          )}

          {change !== undefined && change !== null && (
            <span
              className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                change >= 0
                  ? 'text-green-400 bg-green-500/10'
                  : 'text-red-400 bg-red-500/10'
              }`}
            >
              {change >= 0 ? '+' : ''}
              {change}%
            </span>
          )}
        </div>

        {/* Title */}
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mb-1">
          {title}
        </p>

        {/* Value */}
        <h2
          className={`text-2xl font-bold text-white transition-all duration-500 ${
            animated ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
          }`}
        >
          {displayValue}
        </h2>
      </div>
    </div>
  );
}