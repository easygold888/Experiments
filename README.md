# Experiments — Planetary Market Intelligence

Terminal web-first de inteligencia de mercados (Trading · Macro · FX) con mapa operativo 2D manual, feed editorial masivo y paneles operativos.

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
- `GET /api/intelligence/hub` (central de noticias con filtros por países/continentes/categorías)
- `GET /api/dashboard` (payload maestro para la UI)
- `GET /api/overview` (compatibilidad)

## Qué incluye (MVP operacional v0.4)
- Top bar institucional con estado de feeds, latencias y reloj local/UTC.
- Watchlist financiera interactiva con selección contextual.
- Asset Context Card (retornos, momentum, volatilidad, nota táctica).
- Mapa operativo 2D manual con marcadores de eventos y radar en vivo (sin dependencia de render 3D).
- Market Intelligence Feed editorial (categoría, severidad, bias, activos impactados).
- Country Intelligence Card con score de riesgo soberano.
- Global Indices por región (Américas, Europa, Asia).
- Ribbon inferior con instrumentos clave.
- Precios de watchlist y FX obtenidos de Yahoo Finance (fuente pública), sin datos sintéticos inventados.
- Filtro por defecto orientado a Colombia (`COL`).

## Documento de visión completa
- `docs/PLATFORM_BLUEPRINT.md`
- `docs/PMI_MVP_EXECUTION_PLAN.md`
