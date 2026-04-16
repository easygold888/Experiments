'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { findProduct } from '@/data/products';

export default function CheckoutPage({ params }) {
  const product = findProduct(params.slug);
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let on = true;
    async function createInvoice() {
      setLoading(true);
      const res = await fetch('/api/invoice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug: params.slug })
      });
      const data = await res.json();
      if (on) setInvoice(data);
      setLoading(false);
    }
    createInvoice();
    return () => { on = false; };
  }, [params.slug]);

  if (!product) {
    return <main className="shell"><p>Producto inválido.</p></main>;
  }

  return (
    <main className="shell stack-xl">
      <section className="glass hero-sm stack-sm">
        <h1>Checkout · {product.name}</h1>
        <p>Pago en ETH con invoice verificable. No custodial.</p>
      </section>

      <section className="grid cards-2">
        <article className="glass card stack-sm">
          <h3>Resumen</h3>
          <p><strong>Producto:</strong> {product.name}</p>
          <p><strong>Precio:</strong> ${product.priceUsd} · {product.priceEth} ETH</p>
          <p><strong>Entrega:</strong> {product.delivery}</p>
          <p className="muted small">Al pagar aceptas términos, riesgo y política de entrega digital.</p>
          <Link href="/risk" className="text-link">Leer Risk & Compliance</Link>
        </article>

        <article className="glass card stack-sm">
          <h3>Invoice</h3>
          {loading && <p>Generando invoice...</p>}
          {invoice?.error && <p className="danger">{invoice.error}</p>}
          {invoice && !invoice.error && (
            <>
              <p><strong>ID:</strong> {invoice.invoiceId}</p>
              <p><strong>Wallet:</strong> <code>{invoice.wallet}</code></p>
              <p><strong>Red:</strong> {invoice.network}</p>
              <p><strong>Monto exacto:</strong> {invoice.amountEth} ETH</p>
              <p><strong>Expira:</strong> {new Date(invoice.expiresAt).toLocaleString('es-CO')}</p>
              <p><strong>Confirmaciones:</strong> {invoice.confirmationsRequired}</p>
              <div className="row gap-sm">
                <Link href={`/invoice/${invoice.invoiceId}`} className="btn">Track invoice</Link>
              </div>
            </>
          )}
        </article>
      </section>
    </main>
  );
}
