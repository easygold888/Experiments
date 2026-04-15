# Next.js Landing (coexisting migration)

Este repositorio ahora incluye una versión Next.js de la landing premium en paralelo al stack heredado.

## Ejecutar Next.js

```bash
npm install
npm run dev
```

Abrir: `http://localhost:3000`

## Precio real de oro

Endpoint: `GET /api/gold`

- Fuente upstream: Yahoo Finance `GC=F`.
- Si el upstream falla en runtime, el endpoint devuelve payload de fallback con `source: unavailable`.
