import { NextResponse } from 'next/server';

export const revalidate = 20;

export async function GET() {
  try {
    const res = await fetch('https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=1d&interval=5m', {
      cache: 'no-store',
      headers: {
        'User-Agent': 'Mozilla/5.0'
      }
    });

    if (!res.ok) {
      throw new Error(`Yahoo HTTP ${res.status}`);
    }

    const data = await res.json();
    const result = data?.chart?.result?.[0];
    const meta = result?.meta;

    const price = Number(meta?.regularMarketPrice ?? meta?.previousClose ?? 0);
    const prevClose = Number(meta?.previousClose ?? price);
    const changePct = prevClose ? ((price - prevClose) / prevClose) * 100 : 0;

    return NextResponse.json({
      symbol: 'XAUUSD',
      price,
      changePct,
      source: 'Yahoo Finance (GC=F)',
      updatedAt: new Date().toISOString()
    });
  } catch (error) {
    return NextResponse.json(
      {
        symbol: 'XAUUSD',
        price: null,
        changePct: null,
        source: 'unavailable',
        updatedAt: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'unknown error'
      },
      { status: 200 }
    );
  }
}
