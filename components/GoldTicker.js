'use client';

import { useEffect, useState } from 'react';

export default function GoldTicker() {
  const [gold, setGold] = useState({ price: null, changePct: null, source: 'loading' });

  useEffect(() => {
    let live = true;
    async function pull() {
      try {
        const r = await fetch('/api/gold', { cache: 'no-store' });
        const j = await r.json();
        if (live) setGold(j);
      } catch {
        if (live) setGold({ price: null, changePct: null, source: 'unavailable' });
      }
    }
    pull();
    const id = setInterval(pull, 12000);
    return () => {
      live = false;
      clearInterval(id);
    };
  }, []);

  const has = gold.price != null && gold.changePct != null;
  const dir = has ? (gold.changePct >= 0 ? '▲' : '▼') : '•';
  const sign = has ? (gold.changePct >= 0 ? '+' : '') : '';

  return (
    <div className="ticker glass">
      <strong>XAUUSD {dir}</strong>{' '}
      {has ? `$${gold.price.toFixed(2)} ${sign}${gold.changePct.toFixed(2)}%` : 'Live feed connecting...'}
      <span className="muted small">Source: {gold.source}</span>
    </div>
  );
}
