import Link from 'next/link';

export default function NavBar() {
  return (
    <header className="nav-wrap">
      <div className="shell nav glass">
        <Link href="/" className="brand">EGG</Link>
        <nav className="nav-links">
          <Link href="/products">Productos</Link>
          <Link href="/faq">FAQ</Link>
          <Link href="/risk">Risk</Link>
          <Link href="/products" className="btn-sm">Comprar</Link>
        </nav>
      </div>
    </header>
  );
}
