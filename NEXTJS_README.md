# EasyGoldGlitch Next.js Suite

## Run

```bash
npm install
npm run dev
```

Open:
- Home: `http://localhost:3000/`
- Products: `http://localhost:3000/products`
- FAQ: `http://localhost:3000/faq`
- Risk: `http://localhost:3000/risk`

## API Routes

- `GET /api/gold` → real-time gold proxy from Yahoo (`GC=F`) with graceful fallback.
- `POST /api/invoice` → deterministic invoice payload for checkout flow scaffolding.

## Notes

- ETH checkout flow is structured for production extension (invoice id, wallet, expiry, confirmations).
- Replace deterministic invoice route with DB + on-chain listener for full production.
