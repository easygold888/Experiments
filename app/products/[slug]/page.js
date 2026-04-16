import Link from 'next/link';
import { notFound } from 'next/navigation';
import { findProduct, products } from '@/data/products';

export function generateStaticParams() {
  return products.map((p) => ({ slug: p.slug }));
}

export default function ProductDetail({ params }) {
  const product = findProduct(params.slug);
  if (!product) notFound();

  return (
    <main className="shell stack-xl">
      <section className="glass hero-sm stack-sm">
        <p className="tier">{product.tier}</p>
        <h1>{product.name}</h1>
        <p>{product.bestFor}</p>
        <p className="price">${product.priceUsd} · {product.priceEth} ETH</p>
        <div className="row gap-sm">
          <Link href={`/checkout/${product.slug}`} className="btn">Comprar ahora</Link>
          <Link href="/products" className="btn ghost">Volver al catálogo</Link>
        </div>
      </section>

      <section className="grid cards-2">
        <article className="glass card stack-sm">
          <h3>Incluye</h3>
          <ul className="list">{product.includes.map((x) => <li key={x}>{x}</li>)}</ul>
        </article>
        <article className="glass card stack-sm">
          <h3>No incluye</h3>
          <ul className="list">{product.excludes.map((x) => <li key={x}>{x}</li>)}</ul>
        </article>
      </section>

      <section className="glass card stack-sm">
        <h3>Compatibilidad</h3>
        <p>{product.compatibility.join(' · ')}</p>
        <h3>Delivery</h3>
        <p>{product.delivery}</p>
        <h3>Risk note</h3>
        <p className="muted">{product.riskNote}</p>
      </section>
    </main>
  );
}
