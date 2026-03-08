# Experiments — Planetary Market Intelligence

Prototipo funcional web-first (backend + frontend) para una terminal de inteligencia de mercados con globo 3D y datos abiertos.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Abrir: `http://localhost:8000`

## Qué incluye (v0 funcional)
- Globo 3D interactivo (CesiumJS) con marcadores de eventos geopolíticos.
- `FX Command Center` con datos de Frankfurter (`/api/fx/latest`).
- `Country Intelligence Card` con indicadores World Bank (`/api/country/{iso3}`).
- `Global Event Stream` desde GDELT (`/api/events`).
- Endpoint agregado con degradación elegante: `/api/overview`.
- Caché TTL en backend para reducir latencia y rate-limit en fuentes gratuitas.

## Documento de visión completa
- `docs/PLATFORM_BLUEPRINT.md`
