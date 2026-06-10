import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const navItems = [
  {
    label: 'Dashboard',
    href: '/',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1h-2z" />
      </svg>
    ),
  },
  {
    label: 'Call Logs',
    href: '/logs',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
      </svg>
    ),
  },
  {
    label: 'Analytics',
    href: '/logs',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
  },
  {
    label: 'Settings',
    href: '/settings',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
  },
];

export default function Sidebar() {
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [dateTime, setDateTime] = useState('');

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setDateTime(
        now.toLocaleDateString('en-IN', {
          weekday: 'short',
          day: 'numeric',
          month: 'short',
          year: 'numeric',
        }) +
          '  •  ' +
          now.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
          })
      );
    };
    update();
    const interval = setInterval(update, 60000);
    return () => clearInterval(interval);
  }, []);

  const isActive = (href) => {
    if (href === '/') return router.pathname === '/';
    return router.pathname.startsWith(href);
  };

  const sidebarContent = (
    <>
      {/* Brand */}
      <div className="p-6 pb-2">
        <h1 className="text-xl font-extrabold gradient-text tracking-tight">
          AI Call Center
        </h1>
        <div className="mt-3 flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-live-pulse absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500" style={{ boxShadow: '0 0 8px rgba(34,197,94,0.5)' }}></span>
          </span>
          <span className="text-xs font-semibold text-green-400 tracking-widest uppercase">
            Live
          </span>
        </div>
      </div>

      {/* Divider */}
      <div className="mx-5 my-4 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-1">
        {navItems.map((item) => {
          const active = isActive(item.href);
          return (
            <Link key={item.label} href={item.href} legacyBehavior>
              <a
                onClick={() => setMobileOpen(false)}
                className={`
                  group flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium
                  transition-all duration-200 relative overflow-hidden
                  ${
                    active
                      ? 'bg-brand-500/10 text-brand-400 border-l-[3px] border-brand-500'
                      : 'text-gray-400 hover:text-white hover:bg-white/5 border-l-[3px] border-transparent'
                  }
                `}
              >
                {/* Hover gradient bg */}
                {!active && (
                  <span className="absolute inset-0 opacity-0 group-hover:opacity-100 bg-gradient-to-r from-brand-500/5 to-accent-500/5 transition-opacity duration-300 rounded-xl" />
                )}
                <span className={`relative z-10 transition-colors duration-200 ${active ? 'text-brand-400' : 'text-gray-500 group-hover:text-brand-400'}`}>
                  {item.icon}
                </span>
                <span className="relative z-10">{item.label}</span>
                {active && (
                  <span className="ml-auto relative z-10 w-1.5 h-1.5 rounded-full bg-brand-400" style={{ boxShadow: '0 0 6px rgba(6,182,212,0.6)' }} />
                )}
              </a>
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="p-4 mt-auto">
        <div className="mx-1 mb-3 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        <div className="flex items-center gap-2 px-2">
          <svg className="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-xs text-gray-500 font-medium">
            {dateTime}
          </span>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed top-4 left-4 z-50 lg:hidden glass-card p-2.5 rounded-xl text-gray-400 hover:text-white transition-colors"
        aria-label="Toggle sidebar"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          {mobileOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`
          fixed lg:relative z-40 top-0 left-0 h-screen w-64
          flex flex-col
          glass-card border-r border-white/[0.06] rounded-none
          transition-transform duration-300 ease-out
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
        style={{
          background: 'rgba(10, 10, 18, 0.85)',
          backdropFilter: 'blur(24px)',
        }}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
