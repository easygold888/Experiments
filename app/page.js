'use client';

import { useEffect, useMemo, useRef, useState } from 'react';

const toastPool = [
  '🔔 @xau_hunter just joined VIP',
  '📈 EGG Signal: LONG fired · confidence 0.81',
  '💬 74 mensajes en #vip-news en la última hora',
  '⚡ Macro alert: DXY rejection posted in VIP',
  '🧠 NY session briefing dropped for VIP',
  '✅ Momentum filters aligned on Gold'
];

const rotatePhrases = [
  'Now accessible.',
  'Built for hunters, not spectators.',
  'Precision beats prediction.',
  'Alpha for people who move first.'
];

export default function Page() {
  const [gold, setGold] = useState({ symbol: 'XAUUSD', price: null, changePct: null });
  const [online, setOnline] = useState(870);
  const [rotateIdx, setRotateIdx] = useState(0);
  const [toasts, setToasts] = useState([]);
  const [progress, setProgress] = useState(0);
  const [stats, setStats] = useState({ members: 0, win: 0, pnl: 0, speed: 0 });
  const [feed, setFeed] = useState([
    '[LIVE] Liquidity sweep above Asia high detected.',
    '[LIVE] EGG model confidence: 0.81 · regime: trend continuation.',
    '[LIVE] VIP alert delivered · median reaction 43s.'
  ]);
  const howRef = useRef(null);
  const howTrackRef = useRef(null);

  const tickerText = useMemo(() => {
    const p = gold.price;
    const c = gold.changePct;
    if (p == null || c == null) return 'XAUUSD • Live feed connecting...';
    const dir = c >= 0 ? '▲' : '▼';
    const sign = c >= 0 ? '+' : '';
    return `XAUUSD ${dir} $${p.toFixed(2)} ${sign}${c.toFixed(2)}%`;
  }, [gold]);

  useEffect(() => {
    let mounted = true;

    async function pullGold() {
      try {
        const res = await fetch('/api/gold', { cache: 'no-store' });
        const data = await res.json();
        if (!mounted) return;
        setGold(data);
      } catch {
        // keep graceful fallback
      }
    }

    pullGold();
    const id = setInterval(pullGold, 15000);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, []);

  useEffect(() => {
    const id = setInterval(() => setOnline(840 + Math.floor(Math.random() * 80)), 2600);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const id = setInterval(() => setRotateIdx((p) => (p + 1) % rotatePhrases.length), 2600);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const id = setInterval(() => {
      const msg = toastPool[Math.floor(Math.random() * toastPool.length)];
      const k = crypto.randomUUID();
      setToasts((prev) => [{ id: k, msg }, ...prev].slice(0, 3));
      setTimeout(() => setToasts((prev) => prev.filter((x) => x.id !== k)), 4000);
    }, 6500);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const id = setInterval(() => {
      const dynamic = [
        `[LIVE] Gold at ${gold.price ? `$${gold.price.toFixed(2)}` : 'loading'} · flow skew: buyers`,
        '[LIVE] London handoff map refreshed in VIP dashboard.',
        '[LIVE] Event-risk monitor updated (Fed speakers / yields / DXY).'
      ];
      const msg = dynamic[Math.floor(Math.random() * dynamic.length)];
      setFeed((prev) => [...prev.slice(1), msg]);
    }, 3200);
    return () => clearInterval(id);
  }, [gold.price]);

  useEffect(() => {
    const onScroll = () => {
      const y = window.scrollY;
      const h = document.documentElement.scrollHeight - window.innerHeight;
      setProgress(h > 0 ? (y / h) * 100 : 0);

      document.body.style.setProperty('--mx', `${window.innerWidth / 2 + Math.sin(y * 0.005) * 200}px`);
      document.body.style.setProperty('--my', `${180 + (y % 500)}px`);

      if (window.innerWidth > 1024 && howRef.current && howTrackRef.current) {
        const rect = howRef.current.getBoundingClientRect();
        const total = rect.height - window.innerHeight;
        if (total > 0) {
          const p = Math.min(1, Math.max(0, -rect.top / total));
          const maxX = Math.max(0, howTrackRef.current.scrollWidth - howTrackRef.current.clientWidth);
          howTrackRef.current.style.transform = `translateX(${-maxX * p}px)`;
        }
      }
    };

    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => entry.isIntersecting && entry.target.classList.add('visible'));
    }, { threshold: 0.16 });
    document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    return () => {
      io.disconnect();
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
    };
  }, []);

  useEffect(() => {
    const target = { members: 2400, win: 78, pnl: 2.3, speed: 90 };
    const start = performance.now();
    const duration = 1500;
    let raf;

    const tick = (now) => {
      const p = Math.min(1, (now - start) / duration);
      const e = 1 - Math.pow(1 - p, 3);
      setStats({
        members: Math.round(target.members * e),
        win: Math.round(target.win * e),
        pnl: Number((target.pnl * e).toFixed(1)),
        speed: Math.round(target.speed * e)
      });
      if (p < 1) raf = requestAnimationFrame(tick);
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <div className="page">
      <div className="ambient" aria-hidden>
        <div className="blob gold" />
        <div className="blob amber" />
        <div className="blob teal" />
      </div>
      <div className="spotlight" aria-hidden />
      <div className="noise" aria-hidden />

      <div className="progress" style={{ '--progress': `${progress}%` }} />

      <header className="container glass topbar">
        <div className="ticker">{tickerText} · {tickerText}</div>
        <div className="live"><span className="dot" /> LIVE — {online} members online</div>
      </header>

      <main className="container">
        <section className="hero reveal">
          <div>
            <div className="eyebrow">EasyGoldGlitch / XAUUSD Intelligence</div>
            <h1 className="headline">STOP GUESSING, START PRINTING</h1>
            <p className="subline">Institutional-grade Gold signals. <span className="rotating">{rotatePhrases[rotateIdx]}</span></p>
            <a href="https://discord.gg/g7NkpsHT" target="_blank" rel="noopener noreferrer" className="cta">JOIN VIP CHANNEL FREE →</a>
            <div className="badge glass">🔐 Invite-only · 2,400+ traders · $0 forever</div>

            <div className="feed glass">
              <div className="feed-head">vip signal relay · encrypted feed</div>
              {feed.map((line, i) => <div className="feed-line" key={`${line}-${i}`}>{line}</div>)}
            </div>
          </div>
        </section>

        <section className="section marquee glass reveal">
          <div className="marquee-track">
            <span>📊 Signal accuracy 78.3%</span><span>··</span>
            <span>💰 Avg monthly alpha +4.1%</span><span>··</span>
            <span>⚡ Alerts in real-time</span><span>··</span>
            <span>🏆 #1 Gold channel on Discord</span><span>··</span>
            <span>📊 Signal accuracy 78.3%</span><span>··</span>
            <span>💰 Avg monthly alpha +4.1%</span><span>··</span>
            <span>⚡ Alerts in real-time</span><span>··</span>
            <span>🏆 #1 Gold channel on Discord</span>
          </div>
        </section>

        <section className="section reveal">
          <h2 className="section-title">THE NUMBERS</h2>
          <div className="grid-4">
            <article className="glass card"><div className="stat">{stats.members.toLocaleString()}+</div><div className="muted">Active Members</div></article>
            <article className="glass card"><div className="stat">{stats.win}%</div><div className="muted">Signal Win Rate</div></article>
            <article className="glass card"><div className="stat">${stats.pnl}M+</div><div className="muted">Community P&L Tracked</div></article>
            <article className="glass card"><div className="stat">&lt; {stats.speed}sec</div><div className="muted">Average Alert Speed</div></article>
          </div>
        </section>

        <section className="section reveal">
          <h2 className="section-title">WHAT YOU GET IN VIP</h2>
          <div className="grid-3">
            <article className="glass card"><div className="icon">🔔</div><strong>Real-Time News Alerts</strong><p className="muted">Market-moving gold news before it hits your feed.</p></article>
            <article className="glass card"><div className="icon">📡</div><strong>Algorithmic Signal Feed</strong><p className="muted">EGG system outputs, live with execution context.</p></article>
            <article className="glass card"><div className="icon">🧠</div><strong>Elite Analysis</strong><p className="muted">Weekly deep dives. No fluff. Just edge.</p></article>
          </div>
        </section>

        <section className="section how reveal" ref={howRef}>
          <div className="glass how-pin">
            <h2 className="section-title">HOW IT WORKS</h2>
            <div className="how-track" ref={howTrackRef}>
              <article className="glass card"><div className="step-no">01</div><p>Click the VIP link.</p></article>
              <article className="glass card"><div className="step-no">02</div><p>Join the Discord server.</p></article>
              <article className="glass card"><div className="step-no">03</div><p>Verify and unlock VIP access.</p></article>
              <article className="glass card"><div className="step-no">04</div><p>Receive first signal within 24h.</p></article>
            </div>
          </div>
        </section>

        <section className="final reveal">
          <div>
            <h2 className="headline">STOP TRADING BLIND.</h2>
            <p className="subline">The VIP channel is free. The edge is not.</p>
            <a href="https://discord.gg/g7NkpsHT" target="_blank" rel="noopener noreferrer" className="cta">JOIN VIP CHANNEL FREE →</a>
            <p className="muted">No credit card. No commitment. Just gold alpha.</p>
          </div>
        </section>

        <footer className="glass footer reveal">
          <div className="footer-top">
            <div className="logo">EGG</div>
            <nav className="links">
              <a href="https://discord.gg/g7NkpsHT" target="_blank" rel="noopener noreferrer">Discord</a>
              <a href="https://x.com" target="_blank" rel="noopener noreferrer">Twitter/X</a>
              <a href="https://www.easygoldglitch.com" target="_blank" rel="noopener noreferrer">easygoldglitch.com</a>
            </nav>
          </div>
          <p className="muted">Trading signals are for informational purposes only. Past performance does not guarantee future results.</p>
        </footer>
      </main>

      <div className="toast-wrap" aria-live="polite">
        {toasts.map((t) => <div key={t.id} className="glass toast show">{t.msg}</div>)}
      </div>
    </div>
  );
}
