import { useState } from 'react';

export default function CallTable({ calls }) {
  const [hoveredRow, setHoveredRow] = useState(null);

  if (!calls || calls.length === 0) {
    return (
      <div className="glass-card p-12 text-center">
        <div className="text-4xl mb-4 opacity-30">📞</div>
        <p className="text-gray-500 text-sm font-medium">No recent calls to display</p>
        <p className="text-gray-600 text-xs mt-1">Calls will appear here once they come in</p>
      </div>
    );
  }

  const getStatusBadge = (status) => {
    const s = (status || '').toLowerCase();
    if (s === 'success' || s === 'completed') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-green-500/10 text-green-400 border border-green-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
          Success
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
        <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
        Failed
      </span>
    );
  };

  const getSentimentBadge = (sentiment) => {
    const s = (sentiment || 'Neutral').toLowerCase();
    if (s === 'positive') {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-green-500/10 text-green-400 border border-green-500/20">
          Positive
        </span>
      );
    }
    if (s === 'negative') {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
          Negative
        </span>
      );
    }
    return (
      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-brand-500/10 text-brand-400 border border-brand-500/20">
        Neutral
      </span>
    );
  };

  return (
    <div className="glass-card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-white/[0.06]">
              <th className="px-5 py-4 text-[10px] font-semibold uppercase tracking-widest text-gray-500">
                Phone
              </th>
              <th className="px-5 py-4 text-[10px] font-semibold uppercase tracking-widest text-gray-500">
                Transcript
              </th>
              <th className="px-5 py-4 text-[10px] font-semibold uppercase tracking-widest text-gray-500">
                Intent
              </th>
              <th className="px-5 py-4 text-[10px] font-semibold uppercase tracking-widest text-gray-500">
                Sentiment
              </th>
              <th className="px-5 py-4 text-[10px] font-semibold uppercase tracking-widest text-gray-500">
                Status
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-white/[0.04]">
            {calls.map((call, idx) => (
              <tr
                key={call.id || idx}
                className={`
                  transition-all duration-200 cursor-default
                  ${hoveredRow === idx
                    ? 'bg-gradient-to-r from-brand-500/[0.04] via-accent-500/[0.02] to-transparent'
                    : 'hover:bg-white/[0.02]'
                  }
                `}
                onMouseEnter={() => setHoveredRow(idx)}
                onMouseLeave={() => setHoveredRow(null)}
              >
                <td className="px-5 py-4">
                  <span className="text-sm font-mono text-gray-300">{call.phone_number}</span>
                </td>

                <td className="px-5 py-4 max-w-[200px]">
                  <div className="group relative">
                    <span className="text-sm text-gray-400 truncate block">
                      {call.transcript
                        ? call.transcript.length > 50
                          ? call.transcript.slice(0, 50) + '…'
                          : call.transcript
                        : '—'}
                    </span>
                    {call.transcript && call.transcript.length > 50 && (
                      <div className="absolute left-0 bottom-full mb-2 w-72 p-3 glass-card text-xs text-gray-300 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200 z-20 shadow-xl">
                        {call.transcript}
                      </div>
                    )}
                  </div>
                </td>

                <td className="px-5 py-4">
                  <span className="text-sm text-gray-300 capitalize">{call.intent || '—'}</span>
                </td>

                <td className="px-5 py-4">
                  {getSentimentBadge(call.sentiment)}
                </td>

                <td className="px-5 py-4">
                  {getStatusBadge(call.status)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}