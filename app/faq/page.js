const faqs = [
  ['¿Qué compro exactamente?', 'Un producto digital con entregables definidos por SKU (alertas, playbooks o blueprint).'],
  ['¿Hay ganancias garantizadas?', 'No. No prometemos rentabilidad. Ofrecemos estructura y contexto operativo.'],
  ['¿Cómo se verifica el pago?', 'Con invoice ID, wallet destino, red y estado de confirmaciones.'],
  ['¿Qué pasa después del pago?', 'Confirmación on-chain, activación y acceso digital según SLA del producto.'],
  ['¿Hay soporte?', 'Sí, vía canal de soporte con ticket ID vinculado a invoice.']
];

export default function FAQPage() {
  return (
    <main className="shell stack-xl">
      <section className="glass hero-sm"><h1>FAQ</h1></section>
      <section className="stack-md">
        {faqs.map(([q, a]) => (
          <article key={q} className="glass card stack-sm">
            <h3>{q}</h3>
            <p>{a}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
