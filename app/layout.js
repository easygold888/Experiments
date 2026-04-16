import './globals.css';
import NavBar from '@/components/NavBar';
import Footer from '@/components/Footer';

export const metadata = {
  title: 'EasyGoldGlitch | Precision Trading Systems',
  description: 'Premium digital trading systems with ETH invoice flow, delivery protocol and trust-first architecture.'
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        <div className="bg-layer" aria-hidden />
        <NavBar />
        {children}
        <Footer />
      </body>
    </html>
  );
}
