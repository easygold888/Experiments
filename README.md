# Experiments — Planetary Market Intelligence

Terminal web-first de inteligencia de mercados (Trading · Macro · FX) con núcleo geoespacial, feed editorial y paneles operativos.

## Quickstart (Linux/macOS)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Abrir: `http://localhost:8000`

## Quickstart (Windows PowerShell)
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\windows\start.ps1
```

## Endpoints clave
- `GET /api/health`
- `GET /api/fx/latest`
- `GET /api/country/{iso3}`
- `GET /api/news/intelligence`
- `GET /api/events`
- `GET /api/dashboard` (payload maestro para la UI)
- `GET /api/overview` (compatibilidad)

## Qué incluye (MVP operacional v0.3)
- Top bar institucional con estado de feeds, latencias y reloj local/UTC.
- Watchlist financiera interactiva con selección contextual.
- Asset Context Card (retornos, momentum, volatilidad, nota táctica).
- Globo con capas activables: eventos, rutas energéticas y chokepoints.
- Market Intelligence Feed editorial (categoría, severidad, bias, activos impactados).
- Country Intelligence Card con score de riesgo soberano.
- Global Indices por región (Américas, Europa, Asia).
- Ribbon inferior con instrumentos clave.

## Documento de visión completa
- `docs/PLATFORM_BLUEPRINT.md`
- `docs/PMI_MVP_EXECUTION_PLAN.md`
