# Experiments — Planetary Market Intelligence

Prototipo funcional web-first (backend + frontend) para una terminal de inteligencia de mercados con globo 3D y datos abiertos.

## Quickstart (Linux/macOS)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Abrir: `http://localhost:8000`

## Quickstart (Windows PowerShell)
Desde la carpeta del proyecto:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\windows\start.ps1
```

También puedes cambiar puerto:

```powershell
.\scripts\windows\start.ps1 -Port 8010
```

## Verificación en Windows
Con el servidor corriendo en una terminal, en otra terminal ejecuta:

```powershell
.\scripts\windows\check.ps1 -Port 8000
```

## Solución a `ERR_CONNECTION_REFUSED`
Si ves `127.0.0.1 rechazó la conexión`, normalmente es porque el servidor no está activo.

Checklist:
1. Mantén abierta la terminal donde corre `uvicorn`.
2. Verifica puerto:
   ```powershell
   netstat -ano | findstr :8000
   ```
3. Prueba salud explícita:
   ```powershell
   curl.exe http://127.0.0.1:8000/api/health
   ```
4. Si el 8000 está ocupado, usa otro puerto:
   ```powershell
   .\scripts\windows\start.ps1 -Port 8010
   ```
   y abre `http://127.0.0.1:8010`.

## Qué incluye (v0 funcional)
- Globo 3D interactivo (CesiumJS) con marcadores de eventos geopolíticos.
- `FX Command Center` con datos de Frankfurter (`/api/fx/latest`).
- `Country Intelligence Card` con indicadores World Bank (`/api/country/{iso3}`).
- `Global Event Stream` desde GDELT (`/api/events`).
- Endpoint agregado con degradación elegante: `/api/overview`.
- Caché TTL en backend para reducir latencia y rate-limit en fuentes gratuitas.

## Documento de visión completa
- `docs/PLATFORM_BLUEPRINT.md`
