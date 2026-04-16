import Link from 'next/link';
import { products } from '@/data/products';

export const metadata = { title: 'Productos | EasyGoldGlitch' };

export default function ProductsPage() {
  return (
    <main className="shell stack-xl">
      <section className="glass hero-sm">
        <h1>Product Matrix</h1>
        <p>Comparativa clara para decidir sin fricción.</p>
      </section>

      <section className="grid cards-3">
        {products.map((p) => (
          <article key={p.slug} className="glass card stack-sm">
            <p className="tier">{p.tier}</p>
            <h2>{p.name}</h2>
            <p>{p.bestFor}</p>
            <p className="price">${p.priceUsd} · {p.priceEth} ETH</p>
            <ul className="list compact">
              {p.includes.slice(0, 3).map((x) => <li key={x}>{x}</li>)}
            </ul>
            <div className="row gap-sm">
              <Link className="btn ghost" href={`/products/${p.slug}`}>Detalle</Link>
              <Link className="btn" href={`/checkout/${p.slug}`}>Comprar</Link>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
