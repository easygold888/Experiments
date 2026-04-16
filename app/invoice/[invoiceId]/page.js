'use client';

import { useEffect, useState } from 'react';

const steps = ['awaiting_payment', 'pending_confirmations', 'confirmed', 'delivery_ready'];

export default function InvoiceStatus({ params }) {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setIdx((v) => Math.min(v + 1, steps.length - 1)), 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <main className="shell stack-xl">
      <section className="glass hero-sm stack-sm">
        <h1>Invoice Status</h1>
        <p>ID: <code>{params.invoiceId}</code></p>
      </section>

      <section className="glass card stack-sm">
        <h3>Estado transaccional</h3>
        <ol className="list">
          {steps.map((s, i) => (
            <li key={s}><strong>{i <= idx ? '✓' : '•'}</strong> {s}</li>
          ))}
        </ol>
        <p className="muted">Conecta aquí un listener on-chain real para estado productivo.</p>
      </section>
    </main>
  );
}
