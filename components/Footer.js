import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="shell footer glass">
      <div className="footer-top">
        <strong>EasyGoldGlitch</strong>
        <div className="footer-links">
          <Link href="/products">Productos</Link>
          <Link href="/faq">FAQ</Link>
          <Link href="/risk">Risk</Link>
        </div>
      </div>
      <p className="muted small">Trading signals are for informational purposes only. Past performance does not guarantee future results.</p>
    </footer>
  );
}
