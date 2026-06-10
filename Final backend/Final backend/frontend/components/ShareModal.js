import { useState, useEffect, useRef } from 'react';

export default function ShareModal({ isOpen, onClose, calls }) {
  const [copied, setCopied] = useState(false);
  const overlayRef = useRef(null);

  // Reset copied state when modal opens
  useEffect(() => {
    if (isOpen) setCopied(false);
  }, [isOpen]);

  // Close on Escape
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const callsData = calls || [];

  // Format calls as readable text
  const formatAsText = () => {
    if (callsData.length === 0) return 'No call logs available.';
    return callsData
      .map((c, i) => {
        const date = c.timestamp ? new Date(c.timestamp).toLocaleString('en-IN') : 'N/A';
        return [
          `── Call #${i + 1} ──`,
          `Customer: ${c.customer_name || 'Unknown'}`,
          `Phone: ${c.phone_number || 'N/A'}`,
          `Date: ${date}`,
          `Intent: ${c.intent || 'N/A'}`,
          `Sentiment: ${c.sentiment || 'Neutral'}`,
          `Summary: ${c.summary_text || 'N/A'}`,
          `Status: ${c.status || 'N/A'}`,
          '',
        ].join('\n');
      })
      .join('\n');
  };

  // Copy to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(formatAsText());
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = formatAsText();
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  // Download CSV
  const handleCSV = () => {
    const headers = ['Customer', 'Phone', 'Date', 'Intent', 'Sentiment', 'Summary', 'Status'];
    const rows = callsData.map((c) => [
      c.customer_name || 'Unknown',
      c.phone_number || '',
      c.timestamp ? new Date(c.timestamp).toLocaleString('en-IN') : '',
      c.intent || '',
      c.sentiment || 'Neutral',
      (c.summary_text || '').replace(/"/g, '""'),
      c.status || '',
    ]);
    const csv =
      headers.join(',') +
      '\n' +
      rows.map((r) => r.map((v) => `"${v}"`).join(',')).join('\n');
    downloadFile(csv, 'call-logs.csv', 'text/csv');
  };

  // Download JSON
  const handleJSON = () => {
    const json = JSON.stringify(callsData, null, 2);
    downloadFile(json, 'call-logs.json', 'application/json');
  };

  const downloadFile = (content, filename, mime) => {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Share via WhatsApp
  const handleWhatsApp = () => {
    const summary = `AI Call Center Report\n\nTotal Calls: ${callsData.length}\n\n` +
      callsData
        .slice(0, 5)
        .map((c) => `• ${c.customer_name || 'Unknown'} (${c.phone_number || 'N/A'}) - ${c.sentiment || 'Neutral'}`)
        .join('\n') +
      (callsData.length > 5 ? `\n\n... and ${callsData.length - 5} more calls` : '');
    window.open(`https://wa.me/?text=${encodeURIComponent(summary)}`, '_blank');
  };

  // Share via Email
  const handleEmail = () => {
    const subject = `AI Call Center - Call Logs Report (${new Date().toLocaleDateString('en-IN')})`;
    const body = formatAsText();
    window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  };

  const shareOptions = [
    {
      label: copied ? 'Copied!' : 'Copy to Clipboard',
      desc: 'Copy all logs as formatted text',
      onClick: handleCopy,
      color: 'brand',
      icon: copied ? (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      ) : (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      ),
    },
    {
      label: 'Download CSV',
      desc: 'Export as spreadsheet-compatible file',
      onClick: handleCSV,
      color: 'green',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
        </svg>
      ),
    },
    {
      label: 'Download JSON',
      desc: 'Export raw data as JSON',
      onClick: handleJSON,
      color: 'accent',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
      ),
    },
    {
      label: 'Share via WhatsApp',
      desc: 'Open WhatsApp with call summary',
      onClick: handleWhatsApp,
      color: 'green',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
        </svg>
      ),
    },
    {
      label: 'Share via Email',
      desc: 'Open email client with report',
      onClick: handleEmail,
      color: 'blue',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
    },
  ];

  const colorClasses = {
    brand: 'text-brand-400 bg-brand-500/10 border-brand-500/20 hover:bg-brand-500/20',
    green: 'text-green-400 bg-green-500/10 border-green-500/20 hover:bg-green-500/20',
    accent: 'text-accent-400 bg-accent-500/10 border-accent-500/20 hover:bg-accent-500/20',
    blue: 'text-blue-400 bg-blue-500/10 border-blue-500/20 hover:bg-blue-500/20',
  };

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
        className="glass-card w-full max-w-md p-6 animate-fade-in relative"
        style={{
          background: 'rgba(12, 12, 22, 0.92)',
          border: '1px solid rgba(255,255,255,0.08)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/5"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Header */}
        <h2 className="text-lg font-bold text-white mb-1">Share & Export</h2>
        <p className="text-xs text-gray-500 mb-6">
          {callsData.length} call log{callsData.length !== 1 ? 's' : ''} available
        </p>

        {/* Options */}
        <div className="space-y-2.5">
          {shareOptions.map((opt) => (
            <button
              key={opt.label}
              onClick={opt.onClick}
              className={`
                w-full flex items-center gap-4 p-4 rounded-xl border
                transition-all duration-200 text-left group
                ${colorClasses[opt.color]}
              `}
            >
              <div className="flex-shrink-0">{opt.icon}</div>
              <div className="min-w-0">
                <div className="text-sm font-semibold text-white group-hover:text-white">
                  {opt.label}
                </div>
                <div className="text-xs text-gray-500 mt-0.5">{opt.desc}</div>
              </div>
              <svg className="w-4 h-4 ml-auto flex-shrink-0 text-gray-600 group-hover:text-gray-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
