import Link from 'next/link';
import GoldTicker from '@/components/GoldTicker';
import { products } from '@/data/products';

export default function HomePage() {
  return (
    <main className="shell stack-xl">
      <GoldTicker />

      <section className="hero glass">
        <p className="kicker">EASYGOLDGLITCH / CULT-PREMIUM EXECUTION</p>
        <h1>STOP GUESSING.<br />START EXECUTING.</h1>
        <p className="lead">Sistemas digitales para traders que quieren proceso, no ruido. Compra en ETH con invoice verificable y entrega estructurada.</p>
        <div className="hero-cta">
          <Link href="/products" className="btn">Ver productos</Link>
          <Link href="/risk" className="btn ghost">Riesgo y legal</Link>
        </div>
        <div className="trust-row">
          <span>Invoice ID</span><span>Expiración</span><span>Confirmaciones</span><span>Delivery SLA</span>
        </div>
      </section>

      <section className="grid cards-3">
        <article className="glass card"><h3>What you buy</h3><p>Entregables exactos, compatibilidad, incluye/no incluye, límites operativos.</p></article>
        <article className="glass card"><h3>How you pay</h3><p>Checkout ETH con invoice: wallet destino, monto, expiración y estado.</p></article>
        <article className="glass card"><h3>What happens next</h3><p>Confirmación on-chain, activación, acceso y soporte con ticket ID.</p></article>
      </section>

      <section className="stack-md">
        <h2>Productos</h2>
        <div className="grid cards-3">
          {products.map((p) => (
            <article key={p.slug} className="glass card product-card">
              <p className="tier">{p.tier}</p>
              <h3>{p.name}</h3>
              <p>{p.bestFor}</p>
              <p className="price">${p.priceUsd} · {p.priceEth} ETH</p>
              <Link href={`/products/${p.slug}`} className="text-link">Ver detalle →</Link>
            </article>
          ))}
        </div>
      </section>

      <section className="glass card stack-sm">
        <h2>Arquitectura de confianza</h2>
        <ul className="list">
          <li>Sin promesas de rentabilidad garantizada.</li>
          <li>Invoice verificable + estados transaccionales.</li>
          <li>Riesgos, límites y soporte visibles antes de pagar.</li>
          <li>Entrega digital con trazabilidad y evidencia.</li>
        </ul>
      </section>
    </main>
  );
}
