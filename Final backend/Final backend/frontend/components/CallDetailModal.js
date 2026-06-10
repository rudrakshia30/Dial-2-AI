import { useEffect, useRef } from 'react';

export default function CallDetailModal({ isOpen, onClose, call }) {
  const overlayRef = useRef(null);

  // Close on Escape
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen || !call) return null;

  // Parse lead info
  let lead = {};
  try {
    lead = JSON.parse(call.lead_json || '{}');
  } catch {}
  const hasLead =
    (lead.name && lead.name !== 'Unknown') ||
    (lead.interest && lead.interest !== 'Unknown');

  const getSentimentColor = (sentiment) => {
    const s = (sentiment || '').toLowerCase();
    if (s === 'positive') return 'text-green-400 bg-green-500/10 border-green-500/20';
    if (s === 'negative') return 'text-red-400 bg-red-500/10 border-red-500/20';
    return 'text-brand-400 bg-brand-500/10 border-brand-500/20';
  };

  const InfoRow = ({ label, value }) => (
    <div className="flex flex-col sm:flex-row sm:items-start gap-1 sm:gap-4 py-2.5">
      <span className="text-xs font-medium uppercase tracking-wider text-gray-500 sm:w-28 flex-shrink-0">
        {label}
      </span>
      <span className="text-sm text-gray-300 leading-relaxed">
        {value || '—'}
      </span>
    </div>
  );

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose();
      }}
      style={{
        background: 'rgba(0, 0, 0, 0.6)',
        backdropFilter: 'blur(8px)',
      }}
    >
      <div
        className="glass-card w-full max-w-2xl max-h-[85vh] overflow-y-auto p-6 animate-fade-in relative"
        style={{
          background: 'rgba(12, 12, 22, 0.95)',
          border: '1px solid rgba(255,255,255,0.08)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors p-1.5 rounded-lg hover:bg-white/5 z-10"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-brand-500/10 flex items-center justify-center">
              <svg className="w-5 h-5 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">
                {call.customer_name || 'Unknown Caller'}
              </h2>
              <p className="text-xs text-gray-500 font-mono">
                {call.phone_number || 'N/A'}
              </p>
            </div>
          </div>
        </div>

        {/* Call Info Section */}
        <div className="space-y-0 divide-y divide-white/[0.04]">
          <InfoRow
            label="Date & Time"
            value={call.timestamp ? new Date(call.timestamp).toLocaleString('en-IN', {
              weekday: 'short',
              day: 'numeric',
              month: 'short',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            }) : null}
          />
          <InfoRow label="Duration" value={call.duration ? `${call.duration}s` : null} />
          <InfoRow label="Intent" value={call.intent} />

          {/* Sentiment badge */}
          <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4 py-2.5">
            <span className="text-xs font-medium uppercase tracking-wider text-gray-500 sm:w-28 flex-shrink-0">
              Sentiment
            </span>
            <span
              className={`inline-flex w-fit px-3 py-1 rounded-full text-xs font-semibold border ${getSentimentColor(call.sentiment)}`}
            >
              {call.sentiment || 'Neutral'}
            </span>
          </div>

          <InfoRow label="Status" value={call.status} />
        </div>

        {/* Divider */}
        <div className="my-5 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

        {/* Transcript */}
        <div className="mb-5">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
            Full Transcript
          </h3>
          <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.04] text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
            {call.transcript || 'No transcript available.'}
          </div>
        </div>

        {/* AI Response */}
        {call.ai_response && (
          <div className="mb-5">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
              AI Response
            </h3>
            <div className="p-4 rounded-xl bg-brand-500/[0.04] border border-brand-500/10 text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
              {call.ai_response}
            </div>
          </div>
        )}

        {/* Summary */}
        {call.summary_text && (
          <div className="mb-5">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
              Summary
            </h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              {call.summary_text}
            </p>
          </div>
        )}

        {/* Outcome */}
        {call.outcome && (
          <div className="mb-5">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
              Outcome
            </h3>
            <p className="text-sm text-gray-400">{call.outcome}</p>
          </div>
        )}

        {/* Lead Info Card */}
        {hasLead && (
          <>
            <div className="my-5 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
            <div className="p-4 rounded-xl border border-amber-500/20 bg-amber-500/[0.05]">
              <div className="flex items-center gap-2 mb-3">
                <svg className="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
                <h3 className="text-sm font-semibold text-amber-400">
                  Lead Information
                </h3>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                {lead.name && lead.name !== 'Unknown' && (
                  <div>
                    <span className="text-[10px] uppercase tracking-wider text-gray-500">Name</span>
                    <p className="text-gray-300 font-medium">{lead.name}</p>
                  </div>
                )}
                {lead.interest && lead.interest !== 'Unknown' && (
                  <div>
                    <span className="text-[10px] uppercase tracking-wider text-gray-500">Interest</span>
                    <p className="text-gray-300 font-medium">{lead.interest}</p>
                  </div>
                )}
                {lead.city && (
                  <div>
                    <span className="text-[10px] uppercase tracking-wider text-gray-500">City</span>
                    <p className="text-gray-300 font-medium">{lead.city}</p>
                  </div>
                )}
                {lead.email && (
                  <div>
                    <span className="text-[10px] uppercase tracking-wider text-gray-500">Email</span>
                    <p className="text-gray-300 font-medium">{lead.email}</p>
                  </div>
                )}
                {lead.phone && (
                  <div>
                    <span className="text-[10px] uppercase tracking-wider text-gray-500">Phone</span>
                    <p className="text-gray-300 font-medium">{lead.phone}</p>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
