# PMI // Trading · Macro · FX — Plan Maestro de Ejecución MVP Institucional

## 1) Concepto maestro de producto (narrativa del sistema)
PMI es una **central operativa macro-financiera**: una terminal que fusiona mundo físico (geo / tráfico / disrupciones), mercado (FX/commodities/índices), y capa editorial de inteligencia accionable en una sola superficie de decisión.

### Propuesta de valor
- **Ver** dónde está el riesgo (mapa/globo + hotspots + flujos).
- **Entender** qué activo puede moverse y por qué (narrativas causales).
- **Actuar** con watchlists, alertas y paneles operativos conectados.

### North Star de producto
En menos de 20 segundos, el usuario debe poder responder:
1. ¿Qué está moviendo mercado ahora?
2. ¿Qué región/evento explica la presión de riesgo?
3. ¿Qué instrumentos vigilar de inmediato?

---

## 2) Principios rectores del MVP premium
1. **Institucional antes que decorativo**: estética premium al servicio de claridad.
2. **Densidad con jerarquía**: mucha info, lectura inmediata.
3. **Selección sincronizada**: activo/país/evento seleccionado actualiza toda la UI.
4. **Verdad operacional**: estados de latencia y degradación visibles.
5. **Realtime pragmático**: live-ish confiable > “real-time” falso.
6. **Escalabilidad modular**: paneles desacoplados por dominio.

---

## 3) Arquitectura de información (IA)

## Top Bar (global control)
- Branding: `PMI // Trading · Macro · FX`
- Reloj UTC + local
- Estado feeds (FX, News, Geo, Country)
- Latencia p95
- Alert center (contador severidad)
- Modo de vista: `Overview`, `Analysis`, `Alert-Heavy`, `Executive`

## Left Rail (Financial Terminal)
1. **Watchlist principal** (asset rows)
2. **Asset Context Card** (retornos, volatilidad, momentum, micro-comentario)
3. **Quick filters** (FX, Commodities, Indices, Crypto, Rates, Risk)
4. **Quick actions** (Layouts, Radar, Noticias, Alertas, Heatmap, Calendar)

## Center Stage (Geo-Operational)
- Globo/Mapa interactivo + capas:
  - vuelos en vivo
  - rutas energéticas
  - chokepoints
  - eventos geopolíticos
  - clusters de tensión
- tooltips premium y click-to-focus

## Right Rail (Intelligence Stack)
1. **Market Intelligence Feed** (editorial)
2. **Country Intelligence Card**
3. **Global Indices / Regional Overview**
4. **Transmission Map (evento → activo)**

## Bottom Ribbon
- SPX, DXY, GOLD, OIL, BTC, EURUSD, USDJPY, VIX, UST10Y

---

## 4) Wireframe funcional (desktop ultra-wide)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ TOP BAR: brand · clocks · feed status · latency · alerts · profile · mode  │
├───────────────┬──────────────────────────────────────┬───────────────────────┤
│ LEFT RAIL     │ CENTER: WORLD OPS GLOBE/MAP         │ RIGHT RAIL            │
│ Watchlist     │ - flights/live tracks               │ Market Intelligence    │
│ Asset card    │ - geopolitics/events                │ Country card           │
│ Filters       │ - chokepoints/routes                │ Indices overview       │
│ Shortcuts     │ - contextual selection              │ Transmission map       │
├───────────────┴──────────────────────────────────────┴───────────────────────┤
│ BOTTOM RIBBON: SPX | DXY | GOLD | OIL | BTC | EURUSD | USDJPY | VIX | UST10Y│
└──────────────────────────────────────────────────────────────────────────────┘
```

### Variantes
- 16:9: sidebars colapsables + density presets.
- Ultra-wide: paneles completos y simultáneos.

---

## 5) Sistema visual detallado

## Paleta
- Base: `#070A0F`, `#0B111A`, `#101826`
- Texto: `#E5E7EB`, `#93A3B8`
- Acento frío: `#20C6E8`
- Premium macro/gold: `#CA9A46`
- Up/Down: `#22C55E` / `#EF4444`
- Alerta: `#F59E0B` + rojo controlado

## Tipografía
- Primaria: `Inter` (UI), fallback `Segoe UI/Roboto`
- Números tabulares recomendados en módulos market
- Escala compacta: 11 / 12 / 13 / 16 / 20 / 24

## Superficies
- Panel semi-opaco sólido (evitar glass excesivo)
- Borde fino con contraste + sombra suave
- Glow mínimo y dirigido a elementos clave

## Motion
- Transiciones 120–220ms
- Hover con elevación micro + border accent
- Cambios de estado sin jump (layout estable)

---

## 6) Diseño de pantalla principal (hero)

## Centro
- Globo visible siempre (nunca fondo negro)
- Arcos/rutas energéticas y nodos de chokepoints
- Marcadores de eventos con severidad y clustering
- Selection focus (evento/país/activo)

## Derecha superior: Market Intelligence Feed
Cada card de noticia incluye:
- categoría, titular, one-liner
- región
- activos impactados
- severidad
- bias (`risk-on/off`, `USD+`, `gold+`, `oil-sensitive`)
- estado (`developing`, `confirmed`, `market-moving`)

## Derecha media: Country Intelligence
- GDP, inflación, deuda/PIB, reservas
- score soberano + bucket
- lectura táctica en una línea

## Derecha inferior: Global Indices
- América / Europa / Asia
- top movers
- mini tendencia

---

## 7) Estados del sistema
1. **Normal Market Mode**: densidad balanceada.
2. **Breaking Event Mode**: feed editorial priorizado + resaltado mapa.
3. **High Alert Mode**: foco en severidad y activos en riesgo.
4. **Selected Asset Mode**: contexto de activo domina paneles.
5. **Selected Region Mode**: país/región filtra news + transmisión.

---

## 8) Component library inicial
1. `TopStatusChip`
2. `WatchlistRow`
3. `SparkCell`
4. `AssetContextCard`
5. `LayerToggle`
6. `GeoEventMarker`
7. `FlightMarker`
8. `HeadlineCard`
9. `CountryMetricRow`
10. `RiskBadge`
11. `TransmissionItem`
12. `RibbonTickerItem`

Todos con estados: `default`, `hover`, `selected`, `loading`, `stale`, `error`.

---

## 9) Guía de interacción (synchronized selection)

## Reglas
- Selección de **asset** → filtra news, resalta transmisión, actualiza asset card.
- Selección de **country** → actualiza country card + eventos regionales + activos expuestos.
- Selección de **evento** → centra mapa + muestra activos impactados + bias.
- Selección de **vuelo/disrupción** → foco regional + posibles impactos logísticos.

## Drilldown
- `Global` → `Region` → `Country` → `Event` → `Impacted Assets`

---

## 10) Arquitectura frontend (implementación realista)

## Stack
- React + TypeScript (actual base estática migrable)
- Zustand/Redux Toolkit para state global
- React Query para data fetching/caching
- CesiumJS para globe + overlays
- (opcional) deck.gl para capas densas

## Estructura sugerida
- `shell/` (TopBar, LeftRail, RightRail, BottomRibbon)
- `modules/watchlist/`
- `modules/news-intelligence/`
- `modules/country-intelligence/`
- `modules/geo-ops/`
- `modules/risk-regime/`
- `services/api-client/`
- `state/selection-store.ts`

## Performance
- Virtualización para listas largas
- Clustering de marcadores en mapa
- Throttle en streams de alta frecuencia
- Memo + selective re-render por panel

---

## 11) Arquitectura backend (servicios y límites)

## Servicios base
1. `market-service`: FX/indices/commodities normalization
2. `news-service`: ingest + tagging + severity
3. `geo-service`: flights/events/chokepoints overlays
4. `country-service`: macro/soberano/country cards
5. `intelligence-service`: narrativas, régimen, transmisión
6. `status-service`: salud feeds, latencia, degradación

## API unificada (BFF)
- `GET /api/overview`
- `GET /api/watchlist`
- `GET /api/news/intelligence`
- `GET /api/country/{iso3}`
- `GET /api/map/layers`
- `GET /api/regime`

## Streaming
- SSE para headline/ribbon/status (MVP)
- WS para alta frecuencia en V2

---

## 12) Data engineering blueprint (canónico)

## Entidades
- `MarketTick`
- `NewsItem`
- `GeoEvent`
- `FlightEntity`
- `CountrySnapshot`
- `AssetExposure`

## Timestamp discipline
- `provider_time`
- `ingest_time`
- `processed_time`
- `served_time`

## Calidad
- dedup fingerprint (`title+time+source`)
- `confidence_score`
- `freshness_seconds`
- `stale_flag`

## Linkage
- `news -> impacted_assets`
- `news -> region/country`
- `country -> sensitive_assets`
- `geo_event -> transmission_assets`

---

## 13) Plan de evolución por fases

## Fase A (2–3 semanas)
- consolidar shell premium
- Market Intelligence Feed real
- country card robusta
- ribbon + watchlist institucional

## Fase B (3–5 semanas)
- flights live (fuente abierta)
- clustering en mapa
- selección sincronizada completa
- status/latency panel real

## Fase C (4–6 semanas)
- alert engine básico
- workspace presets
- replay corto (24–72h)
- panel correlaciones rápidas

---

## 14) Criterios de aceptación MVP premium
1. UI responde en < 3s FMP en entorno estándar.
2. Selección de activo/país/evento sincroniza al menos 3 paneles.
3. Feed editorial muestra categoría + severidad + activos impactados.
4. Mapa central mantiene legibilidad con > 300 marcadores (clustering activo).
5. Estado de degradación y frescura visible en top bar.
6. Watchlist y ribbon se actualizan sin congelar UI.

---

## 15) Backlog priorizado inmediato (engineering-ready)

## P0
- Renombrar FX panel a **Market Intelligence Feed**
- Watchlist rows con sparkline + selected state
- Country card con layout de métricas (no JSON)
- Ribbon inferior con 8–10 instrumentos
- Feed status chips (FX/News/Geo/Country)

## P1
- Ingesta flight feed + marker pooling
- News dedup + severity/bias classification
- Transmission map con links evento->activo
- Presets de densidad visual (Overview/Analysis/Alert)

## P2
- Alert rules y notificación en UI
- Replay timeline
- Correlation explorer ligero

---

## 16) UX writing institucional (naming)
- `Market Intelligence Feed`
- `Macro & Geopolitical Briefing`
- `Country Intelligence`
- `Global Risk Regime`
- `Operational Layer Controls`
- `Transmission Paths`

---

## 17) Riesgos y mitigaciones
1. **Demasiada densidad visual** → presets de densidad + colapsables.
2. **Ruido de eventos** → scoring + dedup + confidence.
3. **Mapa bonito pero no útil** → vínculos explícitos evento->activo.
4. **Latencia/free-tier** → TTL + stale badges + fallback transparente.
5. **Escalabilidad UI** → virtualización + render budgets.

---

## 18) Decisión ejecutiva para el siguiente sprint
**Meta sprint:** pasar de “prototipo visible” a “terminal operativa”.

Entregables no negociables:
1. Market Intelligence Feed editorial completo.
2. Watchlist institucional con estado seleccionado.
3. Ribbon inferior de mercado.
4. Country card táctica (score + lectura).
5. Selection sync entre mapa, news y market modules.
