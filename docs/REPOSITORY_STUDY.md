# Estudio del repositorio `Experiments`

## 1) Resumen ejecutivo

Este repositorio implementa un **MVP web** de "Planetary Market Intelligence" con:

- Backend en **FastAPI** que agrega datos de FX, macro país y eventos geopolíticos.
- Frontend estático (HTML/CSS/JS) con visualización central en **CesiumJS**.
- Enfoque en resiliencia operativa: si los proveedores externos fallan, el sistema entrega datos `fallback` degradados.

En términos de madurez, el proyecto está bien orientado para una **demo funcional de inteligencia de mercado** y como base para evolucionar a arquitectura modular (tal como lo describen los documentos de blueprint).

## 2) Estructura del repositorio

```text
app/
  main.py                  # API FastAPI y composición del dashboard
static/
  index.html               # Shell principal de UI
  app.js                   # Renderizado y wiring del cliente
  styles.css               # Sistema visual base
scripts/windows/
  start.ps1                # Arranque del servidor en PowerShell
  check.ps1                # Smoke checks de endpoints
docs/
  PLATFORM_BLUEPRINT.md    # Visión de plataforma objetivo
  PMI_MVP_EXECUTION_PLAN.md# Plan de ejecución del MVP
README.md                  # Quickstart y overview
requirements.txt           # Dependencias Python
```

## 3) Arquitectura actual (cómo funciona hoy)

## Backend (FastAPI)

`app/main.py` concentra toda la lógica:

- Inicializa FastAPI y sirve estáticos.
- Implementa un `TTLCache` en memoria para reducir llamadas externas.
- Consume tres fuentes externas:
  - Frankfurter (FX)
  - World Bank (indicadores macro)
  - GDELT (eventos/noticias)
- Construye un payload maestro en `/api/dashboard` con:
  - estado de feeds
  - régimen de riesgo
  - watchlist
  - contexto del activo seleccionado
  - país
  - feed de noticias
  - mapa de transmisión
  - índices por región
  - ribbon inferior

Fortalezas observadas:

- Excelente postura de **degradación controlada** ante fallos de red/proveedor.
- Endpoints coherentes para UI (`/api/dashboard`) y compatibilidad (`/api/overview`).
- Heurísticas de severidad/impacto suficientes para un MVP narrativo.

Limitaciones técnicas:

- Archivo monolítico (560 líneas): mezcla adquisición de datos, reglas de dominio y ensamblado de respuesta.
- Cache local no compartido entre procesos/instancias.
- Sin suite de tests automática dentro del repo.

## Frontend (estático + Cesium)

`static/index.html` define un layout de tres columnas (left rail, globo central, right rail) con topbar y ribbon.

`static/app.js`:

- Inicializa el viewer de Cesium.
- Dibuja rutas energéticas y chokepoints.
- Hace polling de `/api/dashboard` cada 90s.
- Renderiza watchlist, asset card, feed, país, índices y ribbon.
- Añade interacciones de selección de activo y toggles de capas.

`static/styles.css` aplica el tema institucional oscuro con acentos cian/dorado y componentes de panel compactos.

Fortalezas observadas:

- UX clara para objetivo operativo.
- Integración geoespacial ya funcional sin framework adicional.
- Curva de despliegue simple (sin build step).

Limitaciones técnicas:

- JS vanilla en un único archivo: coste de mantenimiento crecerá con nuevas capacidades.
- Sin tipado/validación de contrato API en cliente.
- Polling fijo (90s) en lugar de SSE/WebSocket para updates incrementales.

## 4) APIs y modelo de datos (visión práctica)

Endpoints expuestos:

- `GET /api/health`
- `GET /api/fx/latest`
- `GET /api/country/{iso3}`
- `GET /api/news/intelligence`
- `GET /api/events`
- `GET /api/dashboard`
- `GET /api/overview` (compat)

Patrones de diseño detectados:

- **BFF único** (`/api/dashboard`) para simplificar consumo del frontend.
- Campos `degraded`, `provider`, `latency_ms` para observabilidad básica.
- `watchpoints` y `risk_regime` orientados a narrativa táctica.

## 5) Coherencia con la documentación estratégica

Los documentos de `docs/` plantean una evolución hacia:

- shell modular,
- servicios especializados,
- streaming,
- y una capa de inteligencia más rica.

El estado actual sí está alineado con ese rumbo: el MVP ya implementa piezas clave (feed editorial, country intelligence, globe operacional y ribbon). La principal brecha no es conceptual sino de **modularización e ingeniería** para escalar.

## 6) Riesgos técnicos prioritarios

1. **Mantenibilidad**: backend y frontend en archivos únicos grandes.
2. **Confiabilidad de datos**: dependencia de APIs públicas sin SLA.
3. **Observabilidad limitada**: no hay métricas estructuradas ni tracing.
4. **Calidad**: ausencia de tests unitarios/integración en CI.
5. **Escalado**: cache local y polling pueden volverse cuellos de botella.

## 7) Recomendaciones accionables (orden sugerido)

1. **Refactor backend por dominios**:
   - `services/fx.py`, `services/country.py`, `services/events.py`, `services/dashboard.py`.
2. **Añadir modelos Pydantic** para contratos de respuesta críticos.
3. **Tests mínimos**:
   - unitarios para scoring/regime/risk,
   - integración para `/api/dashboard` en modo fallback.
4. **Observabilidad**:
   - logging estructurado, latencia por proveedor y flags de degradación.
5. **Evolución frontend gradual**:
   - modularizar `app.js` por funciones de render y data access,
   - evaluar migración a TypeScript + estado central en fase posterior.
6. **Streaming MVP**:
   - SSE para status/ribbon/feed y reducir polling completo.

## 8) Conclusión

El repositorio está **bien resuelto para su objetivo MVP**: entrega valor visual y operacional con un stack simple y resiliente a fallos externos. El siguiente salto de calidad debería enfocarse en **modularidad, testeo y observabilidad**, manteniendo la propuesta de producto actual.
