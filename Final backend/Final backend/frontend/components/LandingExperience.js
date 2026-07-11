import { useState, useEffect } from 'react';

export default function LandingExperience({ onLaunchDashboard }) {
  const [activeSection, setActiveSection] = useState(0);
  const [callButtonGlowing, setCallButtonGlowing] = useState(false);
  const [triggerTransition, setTriggerTransition] = useState(false);

  // Handle scroll trigger animations
  useEffect(() => {
    const handleScroll = () => {
      const scrollPos = window.scrollY;
      const height = window.innerHeight;
      const section = Math.round(scrollPos / height);
      setActiveSection(section);
      
      // Glow button on Section 4
      if (section === 3) {
        setCallButtonGlowing(true);
      } else {
        setCallButtonGlowing(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLaunch = () => {
    setTriggerTransition(true);
    setTimeout(() => {
      onLaunchDashboard();
    }, 900); // Allow camera-zoom animation to complete
  };

  return (
    <>
      <style jsx>{`
        .landing-container {
          background: #000000;
          color: #ffffff;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          overflow-x: hidden;
          scroll-snap-type: y mandatory;
        }
        .snap-section {
          scroll-snap-align: start;
          height: 100vh;
          width: 100vw;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          position: relative;
          overflow: hidden;
          background: #000000;
        }
        .hero-title {
          font-size: clamp(2.5rem, 5vw, 4.5rem);
          font-weight: 800;
          letter-spacing: -0.03em;
          line-height: 1.1;
        }
        .hero-subtitle {
          font-size: clamp(1.25rem, 2.5vw, 2.25rem);
          font-weight: 500;
          color: #a1a1a6;
          letter-spacing: -0.015em;
        }
        .nokia-phone {
          width: 140px;
          height: 280px;
          background: #111;
          border-radius: 20px;
          border: 3px solid #222;
          box-shadow: 0 25px 50px -12px rgba(255, 255, 255, 0.05), inset 0 2px 4px rgba(255, 255, 255, 0.1);
          display: flex;
          flex-direction: column;
          padding: 12px;
          position: relative;
          transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
          animation: floatPhone 6s ease-in-out infinite;
        }
        @keyframes floatPhone {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-12px) rotate(2deg); }
        }
        .nokia-screen {
          flex: 1.1;
          background: #050505;
          border-radius: 8px;
          border: 1px solid #1a1a1a;
          margin-bottom: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #22d3ee;
          font-family: monospace;
          font-size: 11px;
          text-shadow: 0 0 4px rgba(34, 211, 238, 0.3);
          overflow: hidden;
          position: relative;
        }
        .nokia-keypad {
          flex: 1.2;
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 6px;
        }
        .nokia-key {
          background: #1c1c1e;
          border-radius: 6px;
          border-bottom: 2px solid #0c0c0e;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 10px;
          font-weight: 600;
          color: #8e8e93;
        }
        .nokia-key.call-btn {
          background: ${callButtonGlowing ? '#166534' : '#1c1917'};
          color: ${callButtonGlowing ? '#4ade80' : '#8e8e93'};
          box-shadow: ${callButtonGlowing ? '0 0 15px rgba(74, 222, 128, 0.4)' : 'none'};
          border-bottom: 2px solid #15803d;
          transition: all 0.5s ease;
        }
        .wave {
          position: absolute;
          border: 1px solid rgba(34, 211, 238, 0.2);
          border-radius: 50%;
          animation: expandWave 4s linear infinite;
          pointer-events: none;
        }
        @keyframes expandWave {
          0% { width: 100px; height: 100px; opacity: 1; }
          100% { width: 800px; height: 800px; opacity: 0; }
        }
        .transition-zoom {
          transform: scale(25) translate3d(0, 50px, 0);
          opacity: 0;
          pointer-events: none;
        }
      `}</style>

      <div className={`landing-container min-h-screen bg-black text-white ${triggerTransition ? 'transition-zoom duration-1000' : ''}`}>
        
        {/* Navigation / Header */}
        <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-6 backdrop-blur-md bg-black/35 border-b border-white/5">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold bg-white/10 text-white px-2 py-0.5 rounded border border-white/10 tracking-widest uppercase">Base44 Project</span>
            <span className="text-lg font-bold tracking-tight text-white">Dial2AI</span>
          </div>
          <button
            onClick={handleLaunch}
            className="px-5 py-2 rounded-full bg-white text-black hover:bg-gray-200 transition text-xs font-semibold tracking-wide shadow-lg"
          >
            Launch Base44 Dashboard
          </button>
        </header>

        {/* SECTION 1: HERO */}
        <section className="snap-section">
          <div className="max-w-4xl text-center px-6 z-10 mb-8">
            <h1 className="hero-title mb-4">The World's Smartest AI</h1>
            <p className="hero-subtitle mb-8">Works On The Simplest Phone.</p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={handleLaunch}
                className="px-8 py-3.5 rounded-full bg-cyan-500 text-black hover:bg-cyan-400 transition text-sm font-bold tracking-wide shadow-lg shadow-cyan-500/20"
              >
                Experience Dial2AI
              </button>
              <button
                onClick={() => {
                  window.scrollTo({
                    top: window.innerHeight,
                    behavior: 'smooth'
                  });
                }}
                className="px-8 py-3.5 rounded-full border border-white/10 text-white hover:bg-white/5 transition text-sm font-semibold tracking-wide"
              >
                Learn More
              </button>
            </div>
          </div>

          {/* Interactive Nokia Phone Representation */}
          <div className="nokia-phone mt-6">
            <div className="nokia-screen">
              <div className="text-center">
                <p className="animate-pulse">SYSTEM OK</p>
                <p className="text-[9px] text-gray-500 mt-1">Dial: 09513886363</p>
              </div>
            </div>
            <div className="nokia-keypad">
              <div className="nokia-key call-btn">📞</div>
              <div className="nokia-key">▲</div>
              <div className="nokia-key">❌</div>
              <div className="nokia-key">1</div>
              <div className="nokia-key">2</div>
              <div className="nokia-key">3</div>
              <div className="nokia-key">4</div>
              <div className="nokia-key">5</div>
              <div className="nokia-key">6</div>
              <div className="nokia-key">7</div>
              <div className="nokia-key font-bold text-white">8</div>
              <div className="nokia-key">9</div>
              <div className="nokia-key">*</div>
              <div className="nokia-key">0</div>
              <div className="nokia-key">#</div>
            </div>
          </div>
        </section>

        {/* SECTION 2: THE PROBLEM */}
        <section className="snap-section px-8">
          <div className="max-w-3xl text-center space-y-12">
            <p className="text-2xl font-light text-gray-400">Artificial Intelligence changed the world.</p>
            <div className="text-gray-600 text-3xl">↓</div>
            <p className="text-4xl font-semibold leading-snug">But millions were left behind.</p>
            <div className="text-gray-600 text-3xl">↓</div>
            <p className="text-5xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              350 Million People still use feature phones.
            </p>
          </div>
        </section>

        {/* SECTION 3: DETAILED SHOWCASE */}
        <section className="snap-section bg-gradient-to-b from-black via-zinc-950 to-black px-6">
          <div className="max-w-5xl w-full grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-extrabold tracking-tight mb-6">Designed for accessibility.</h2>
              <div className="space-y-6 text-gray-400 text-sm">
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-white font-bold text-xs shrink-0">1</div>
                  <p><strong className="text-white">Matte Tactile Keypad</strong>: Built for simple physical navigation without touchscreens.</p>
                </div>
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-white font-bold text-xs shrink-0">2</div>
                  <p><strong className="text-white">Crisp Mono Speaker</strong>: High-output voice clarity designed for loud ambient village environments.</p>
                </div>
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-white font-bold text-xs shrink-0">3</div>
                  <p><strong className="text-white">One-Click Green Call Button</strong>: Press once, ask anything, hear immediate responses.</p>
                </div>
              </div>
            </div>
            <div className="flex justify-center">
              {/* Product Macro Showcase */}
              <div className="w-64 h-96 bg-zinc-900 border border-white/5 rounded-3xl p-8 relative flex flex-col justify-end shadow-2xl">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-zinc-800/50 via-transparent to-transparent pointer-events-none rounded-3xl" />
                <div className="space-y-4">
                  <span className="text-[10px] font-bold tracking-widest text-zinc-500 uppercase">Plastic Texture / Matte Finished</span>
                  <h3 className="text-2xl font-bold">Apple-Grade Keynote Product Design</h3>
                  <p className="text-xs text-zinc-400">Tactile responsiveness engineered for standard mobile calls.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 4: ONE BUTTON */}
        <section className="snap-section relative">
          {callButtonGlowing && (
            <>
              <div className="wave" style={{ animationDelay: '0s' }} />
              <div className="wave" style={{ animationDelay: '1.3s' }} />
              <div className="wave" style={{ animationDelay: '2.6s' }} />
            </>
          )}
          <div className="text-center z-10 space-y-6 max-w-2xl px-6">
            <div className="w-20 h-20 bg-green-500/10 border border-green-500/30 rounded-full flex items-center justify-center mx-auto shadow-[0_0_40px_rgba(34,197,94,0.15)] animate-pulse">
              <span className="text-4xl text-green-400">📞</span>
            </div>
            <h2 className="text-4xl font-extrabold tracking-tight">One Button. Infinite Intelligence.</h2>
            <p className="text-gray-400 text-sm max-w-md mx-auto">No apps to download. No accounts to configure. Press green to connect to Dial2AI.</p>
          </div>
        </section>

        {/* SECTION 5: WORLD TRANSFORMS */}
        <section className="snap-section bg-gradient-to-b from-black via-zinc-950 to-black px-6">
          <div className="max-w-4xl text-center space-y-8">
            <h2 className="text-3xl font-extrabold tracking-tight">The world forms around the phone.</h2>
            <p className="text-gray-400 text-sm max-w-lg mx-auto">Connecting simple GSM mobile calls to high-speed digital networks.</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
              {[
                { name: 'Telecom Grid', icon: '📡' },
                { name: 'Voice Cloud', icon: '☁️' },
                { name: 'Voice AI NLP', icon: '🧠' },
                { name: 'Real-time Weather', icon: '☀️' },
                { name: 'Healthcare Info', icon: '🏥' },
                { name: 'Govt Schemes', icon: '📜' },
                { name: 'Agriculture Data', icon: '🌾' },
                { name: 'Multi-lingual STT', icon: '🗣️' },
              ].map((item, idx) => (
                <div key={idx} className="glass-card p-6 border border-white/5 flex flex-col items-center justify-center gap-3">
                  <span className="text-3xl">{item.icon}</span>
                  <span className="text-xs font-semibold text-gray-300">{item.name}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* SECTION 6: INDIA MAP */}
        <section className="snap-section px-6">
          <div className="max-w-3xl text-center space-y-6">
            <h2 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
              Every Village. Every Language. Every Call.
            </h2>
            <p className="text-gray-400 text-sm max-w-md mx-auto">Deployable anywhere in India. Supporting English, Hindi, and Hinglish dialogue automatically.</p>
            
            {/* Glowing Map Container */}
            <div className="w-full max-w-md h-52 bg-zinc-900/50 border border-white/5 rounded-2xl mx-auto mt-6 flex items-center justify-center relative overflow-hidden">
              <div className="absolute w-2 h-2 rounded-full bg-cyan-400 animate-ping top-1/4 left-1/3" />
              <div className="absolute w-2 h-2 rounded-full bg-indigo-400 animate-ping top-2/3 left-1/2" />
              <div className="absolute w-2 h-2 rounded-full bg-violet-400 animate-ping top-1/2 left-2/3" />
              <span className="text-gray-600 text-xs font-mono uppercase tracking-widest">Active Call Map Pulses</span>
            </div>
          </div>
        </section>

        {/* SECTION 7: FLOW ANIMATION */}
        <section className="snap-section bg-gradient-to-b from-black via-zinc-950 to-black px-6">
          <div className="max-w-3xl w-full text-center space-y-8">
            <h2 className="text-3xl font-bold">Seamless Technology Path</h2>
            <div className="flex flex-col md:flex-row items-center justify-center gap-4 text-xs font-mono uppercase tracking-wider text-gray-400">
              <span className="px-3 py-1.5 bg-white/5 border border-white/5 rounded-lg text-white">1. Phone Call</span>
              <span>→</span>
              <span className="px-3 py-1.5 bg-white/5 border border-white/5 rounded-lg text-white">2. Telecom Grid</span>
              <span>→</span>
              <span className="px-3 py-1.5 bg-white/5 border border-white/5 rounded-lg text-white">3. Voice STT</span>
              <span>→</span>
              <span className="px-3 py-1.5 bg-white/5 border border-white/5 rounded-lg text-white">4. Groq LLM</span>
              <span>→</span>
              <span className="px-3 py-1.5 bg-white/5 border border-white/5 rounded-lg text-white">5. Knowledge Graph</span>
            </div>
            <div className="h-2 w-full max-w-lg bg-zinc-800/80 rounded-full mx-auto overflow-hidden relative">
              <div className="absolute h-full w-1/3 bg-cyan-500 rounded-full animate-bounce" style={{ animationDuration: '3s' }} />
            </div>
          </div>
        </section>

        {/* SECTION 8: STATS & IMPACT */}
        <section className="snap-section">
          <div className="max-w-4xl grid grid-cols-2 md:grid-cols-4 gap-8 text-center px-6">
            <div>
              <p className="text-4xl font-extrabold text-cyan-400">350M</p>
              <p className="text-xs text-gray-400 mt-2 uppercase tracking-widest font-semibold">Offline Users</p>
            </div>
            <div>
              <p className="text-4xl font-extrabold text-violet-400">24/7</p>
              <p className="text-xs text-gray-400 mt-2 uppercase tracking-widest font-semibold">Voice AI Service</p>
            </div>
            <div>
              <p className="text-4xl font-extrabold text-amber-400">Zero</p>
              <p className="text-xs text-gray-400 mt-2 uppercase tracking-widest font-semibold">Internet Needed</p>
            </div>
            <div>
              <p className="text-4xl font-extrabold text-emerald-400">One</p>
              <p className="text-xs text-gray-400 mt-2 uppercase tracking-widest font-semibold">Phone Call Connection</p>
            </div>
          </div>
        </section>

        {/* SECTION 9: TRANSITION */}
        <section className="snap-section bg-gradient-to-b from-black to-zinc-950">
          <div className="text-center space-y-6 max-w-xl px-6">
            <h2 className="text-3xl font-extrabold tracking-tight">Ready to explore?</h2>
            <p className="text-gray-400 text-sm">Step directly into the Base44-powered monitoring platform to observe live caller sessions, graph analytics, and system configurations.</p>
            <button
              onClick={handleLaunch}
              className="px-8 py-3.5 rounded-full bg-white text-black hover:bg-gray-200 transition text-sm font-bold tracking-wide shadow-2xl animate-bounce"
            >
              Launch Dashboard console
            </button>
          </div>
        </section>

      </div>
    </>
  );
}
