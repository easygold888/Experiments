import { NextResponse } from 'next/server';
import { findProduct } from '@/data/products';

const WALLET = '0xF4C9D2A4B9a2fCb2a8bACf8eFb5f8268A4b27E93';

export async function POST(req) {
  try {
    const body = await req.json();
    const product = findProduct(body?.slug);

    if (!product) {
      return NextResponse.json({ error: 'Invalid product' }, { status: 400 });
    }

    const now = Date.now();
    const invoiceId = `EGG-${product.slug.toUpperCase()}-${now}`;
    const expiresAt = new Date(now + 15 * 60 * 1000).toISOString();

    return NextResponse.json({
      invoiceId,
      product: product.name,
      slug: product.slug,
      amountUsd: product.priceUsd,
      amountEth: product.priceEth,
      wallet: WALLET,
      network: 'Ethereum Mainnet',
      confirmationsRequired: 2,
      expiresAt,
      status: 'awaiting_payment',
      note: 'This is a deterministic invoice response. Connect on-chain listener for production settlement.'
    });
  } catch {
    return NextResponse.json({ error: 'Malformed request' }, { status: 400 });
  }
}
