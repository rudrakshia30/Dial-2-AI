import '../styles/globals.css';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';

export default function App({ Component, pageProps }) {
  const router = useRouter();
  const [transitioning, setTransitioning] = useState(false);

  useEffect(() => {
    const handleStart = () => setTransitioning(true);
    const handleComplete = () => {
      setTransitioning(false);
    };
    router.events.on('routeChangeStart', handleStart);
    router.events.on('routeChangeComplete', handleComplete);
    router.events.on('routeChangeError', handleComplete);
    return () => {
      router.events.off('routeChangeStart', handleStart);
      router.events.off('routeChangeComplete', handleComplete);
      router.events.off('routeChangeError', handleComplete);
    };
  }, [router]);

  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Dial2AI — Base44 Console</title>
        <meta name="description" content="Dial2AI: AI Voice Assistant accessible through normal phone calls. Built on Base44 platform. No smartphone, no internet, no app required." />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </Head>
      <div style={{ fontFamily: "'Inter', sans-serif" }}>
        {/* Page transition overlay */}
        {transitioning && (
          <div className="fixed inset-0 z-[999] bg-black/60 backdrop-blur-sm flex items-center justify-center pointer-events-none">
            <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          </div>
        )}
        <Component {...pageProps} />
      </div>
    </>
  );
}