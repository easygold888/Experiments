# Plataforma Flagship de Inteligencia de Mercados (Trading / Macro / FX)

## 1. Tesis del producto
Construimos una **terminal planetaria de lectura de mercados**: un sistema web-first donde el globo 3D no “visualiza datos”, sino que **explica causalidad de precio** entre geopolítica, energía, deuda soberana, macro y FX. El producto prioriza decisión operativa (trade/risk/watch) sobre estética, y usa datos abiertos con degradación elegante para mantener utilidad aun sin feeds institucionales de pago.

## 2. Norte estratégico
- **Norte funcional:** responder en <30s “qué mueve este símbolo y qué vigilar después”.
- **Norte de producto:** unificar en una sola consola: mapa, stream de eventos, estructura macro y señal cross-asset.
- **Norte técnico:** web moderna con baja latencia percibida vía edge caching, precomputación y streaming incremental.
- **Norte de negocio:** operar sin dependencia crítica de vendors premium cerrados.

## 3. Usuarios objetivo
1. **FX / Macro Trader discrecional** (primario)
   - Necesita contexto causal rápido para entrada/salida y sizing.
2. **Analista de riesgo soberano / country risk**
   - Necesita vigilar deterioro por país y contagio regional.
3. **PM multi-asset / commodity strategist**
   - Necesita enlaces energía-rutas-conflicto-precio.
4. **Equipo de inteligencia geopolítica financiera**
   - Necesita trazabilidad, confianza de fuente y alertas accionables.
5. **CIO / comité de inversión (modo briefing)**
   - Necesita síntesis de alto impacto con drill-down profundo.

## 4. Casos de uso prioritarios
1. **“¿Qué mueve EURUSD ahora?”**
   - Inputs: diferencial de tasas, sorpresas macro, eventos UE/US, riesgo energético.
   - Salida: ranking de drivers + mapa de exposición + próximos watchpoints.
2. **“¿Qué conflicto puede contagiar Brent y divisas EM?”**
   - Inputs: eventos georreferenciados, chokepoints, rutas de energía, dependencia de importación.
   - Salida: cadena de transmisión conflicto→supply→precio→FX.
3. **“¿Qué monedas están frágiles por soberano + reservas?”**
   - Inputs: deuda/PIB, reservas, yield spreads, inflación, calendario macro.
   - Salida: matriz de vulnerabilidad y alertas tempranas.
4. **“¿Qué cambió desde ayer en risk-on/risk-off?”**
   - Inputs: índice compuesto cross-asset + eventos + correlaciones.
   - Salida: panel comparativo con explicaciones causales.

## 5. Visión UX/UI
- **Lenguaje visual:** obsidiana + grafito; acentos ámbar/cobre para estructura, cian técnico para información activa, rojo quirúrgico para riesgo.
- **Densidad controlada:** mucha información, jerarquía estricta por tamaño, contraste y motion mínimo.
- **Interacciones clave:** hover intelligence, click-to-focus, compare mode, time scrub, explainability pane.
- **Principio rector:** “cada píxel debe servir una decisión de mercado”.

## 6. Arquitectura conceptual
Sistema de 5 planos:
1. **Data Sensing Plane:** conectores a APIs abiertas (market, macro, geopolítica, geoespacial).
2. **Intelligence Plane:** normalización, resolución de entidades, scoring de severidad/impacto/confianza.
3. **Knowledge Plane:** ontología + grafo causal + series temporales.
4. **Experience Plane:** globo 3D + paneles analíticos + stream + alertas.
5. **Reliability Plane:** caché multinivel, observabilidad, auditoría, controles de seguridad.

## 7. Arquitectura técnica concreta
### Frontend
- Next.js (App Router) + React + TypeScript.
- Motor geoespacial híbrido:
  - **CesiumJS** para globo 3D, cámara, terreno, time dynamic layers.
  - **deck.gl** para capas analíticas (arcos, hex/cluster, heatmaps).
  - **MapLibre** para vistas 2D tácticas en panel secundario.

### Edge/API
- Cloudflare Workers como BFF (backend-for-frontend), auth gate, rate-limit shield, caching inteligente.
- Cloudflare KV + Cache API para respuestas “live-ish”.
- Durable Objects para sesiones de stream/watchlists compartidas.

### Core backend
- Servicios (Node.js/Fastify o Python/FastAPI) para ingestión, enriquecimiento y explainability.
- Postgres + PostGIS para entidades, geometrías y queries espaciales.
- TimescaleDB (extensión sobre Postgres) para series temporales.
- OpenSearch para búsqueda semántica/keyword híbrida.
- Neo4j Community (o Apache AGE sobre Postgres) para relaciones causales profundas.

### Streaming y jobs
- NATS/Redpanda (self-host) como event bus.
- Workers batch (Temporal/Celery/Arq) para refresh por frecuencia.
- SSE para stream de UI (menos fricción que WebSockets en MVP), WebSockets en flagship para canales interactivos.

### Almacenamiento
- Object storage S3-compatible (R2/MinIO) para snapshots, tiles, replay bundles.

## 8. Ontología de entidades y relaciones
### Modelo lógico
Entidades mínimas (todas versionadas):
- Country, Region, Bloc, Asset, Symbol, Currency, Commodity, CentralBank, MacroIndicator, Event, Conflict, Sanction, Route, Chokepoint, Port, Pipeline, Reserve, ResourceCluster, DebtProfile, YieldCurve, TradeFlow, Alert, Watchlist, Scenario.

Relaciones mínimas:
- affects, affected_by, priced_against, correlated_with, exposed_to, located_in, depends_on, routes_through, threatens, supports, imports, exports, produces, stores, finances, sanctions, escalates, transmits_to, hedges, substitutes.

### Modelo temporal
- **Bitemporal:** `valid_time` (cuándo fue verdad en el mundo) + `system_time` (cuándo lo conocimos).
- Permite replay histórico y auditoría de revisiones.

### Trazabilidad y confianza
- Cada hecho: `source_id`, `source_url`, `ingested_at`, `confidence_score`, `method` (directo/inferido).
- Confidence compuesto:
  - fiabilidad base de fuente,
  - corroboración cruzada,
  - frescura,
  - consistencia histórica.

### Explainability
- Toda afirmación causal debe devolver: “señales usadas”, “peso por señal”, “lag temporal”, “grado de incertidumbre”.

## 9. Mapa 3D y capas geoespaciales
### Capacidades del globo
- Vista global, zoom multi-escala, slider temporal, playback, comparación T0 vs T1.
- Pulsos de eventos, arcos de flujo (energía/comercio), heatmaps de stress, clusters dinámicos.

### Capas mínimas (activables)
- Países/bloques, capitales financieras, puertos, chokepoints marítimos.
- Rutas energéticas, pipelines gas/petróleo, dependencia energética.
- Clusters de oro y minerales estratégicos.
- Deuda/riesgo soberano, stress macro regional.
- Conflictos, sanciones, protestas/inestabilidad.
- Exposición a commodities, sensibilidad FX geográfica.
- Supply chain routes, eventos georreferenciados, watchpoints.

### Estrategia visual de capas
- LOD estricto: país/región en zoom alto; rutas/puertos al acercar.
- Capas de alto ruido (eventos) con agregación temporal y clustering adaptativo.

## 10. Módulos funcionales de trading / macro / forex
1. **FX Command Center**
   - Objetivo: monitor de pares G10/EM + drivers.
   - Inputs: FX spot/ref, tasas, macro surprise, eventos.
   - Output: ranking drivers + alertas de ruptura.
   - Riesgo: sobreajuste causal.
   - Complejidad: media-alta.
2. **Macro Pulse**
   - Objetivo: pulso macro global por región.
   - Inputs: inflación, crecimiento, actividad, liquidez.
   - Output: mapa de stress y divergencia.
   - Complejidad: media.
3. **Sovereign Risk Monitor**
   - Objetivo: detectar deterioro de solvencia/financiación.
   - Inputs: deuda, reservas, yields, FX pressure.
   - Output: score soberano + semáforos.
   - Complejidad: media-alta.
4. **Commodity & Resource Map**
   - Objetivo: producción, rutas, shocks de oferta.
   - Inputs: EIA/USGS/trade flows/eventos.
   - Output: mapa de exposición por commodity.
   - Complejidad: alta.
5. **Energy Security Panel**
   - Objetivo: vulnerabilidad energética regional.
   - Inputs: imports/exports, inventarios, chokepoints.
   - Output: matriz de dependencia + riesgo logístico.
   - Complejidad: alta.
6. **Country Intelligence Card**
   - Objetivo: ficha integral país.
   - Output: macro+soberano+eventos+alertas en una vista.
   - Complejidad: media.
7. **Symbol Intelligence Card**
   - Objetivo: ficha integral símbolo.
   - Output: precio, drivers, correlaciones, geografía y watchpoints.
   - Complejidad: media.
8. **What Moved Markets? Engine**
   - Objetivo: explicar cambios por ventana temporal.
   - Output: top narrativas causales con confianza.
   - Complejidad: alta.
9. **Conflict-to-Market Transmission Map**
   - Objetivo: cadena de contagio geopolítico.
   - Output: rutas/activos en riesgo y escenarios.
   - Complejidad: alta.
10. **Risk-On / Risk-Off Matrix**
    - Objetivo: régimen de mercado actual.
    - Output: heat matrix cross-asset.
    - Complejidad: media.
11. **Global Event Stream**
    - Objetivo: feed filtrable por severidad/impacto.
    - Complejidad: media.
12. **Alert Watchtower**
    - Objetivo: alertas accionables y auditables.
    - Complejidad: media-alta.
13. **Historical Replay**
    - Objetivo: reconstrucción de episodios.
    - Complejidad: alta.
14. **Scenario Builder**
    - Objetivo: simulaciones de shocks (tasas/conflicto/sanción).
    - Complejidad: alta.
15. **Cross-Asset Correlation Explorer**
    - Objetivo: correlaciones dinámicas por régimen.
    - Complejidad: media-alta.

## 11. Estrategia de fuentes de datos 100% gratis
### Taxonomía de frescura
- **L1 Live-ish (30s–5m)**: FX referencia, eventos calientes, alertas.
- **L2 Intra-day (15m–6h)**: energía selecta, macro rápida, agregados de noticias.
- **L3 Daily/Weekly/Monthly**: soberano, reservas, estructura país.
- **L4 Structural/Base**: cartografía, rutas, recursos, fronteras.

### Fuentes y uso
1. **Frankfurter (FX)**
   - Aporta: FX spot de referencia ECB.
   - Latencia: no tick; actualización periódica.
   - Limitación: no HFT, no profundidad.
   - Cache: 1–5 min edge + stale-while-revalidate.
2. **ECB Data Portal**
   - Aporta: tipos y series europeas.
   - Latencia: diaria/periodic.
   - Fiabilidad: alta institucional.
   - Cache: fuerte (horas-día).
3. **FRED**
   - Aporta: macro, tasas, spreads.
   - Latencia: depende de serie (diaria-mensual).
   - Limitación: no global completo en todo.
   - Cache: por release calendar.
4. **World Bank Indicators API**
   - Aporta: estructura país largo plazo.
   - Latencia: baja frecuencia (anual/trimestral según indicador).
   - Uso: baseline de vulnerabilidad estructural, no señal táctica.
5. **GDELT**
   - Aporta: eventos geopolíticos OSINT geolocalizados.
   - Latencia: casi continua en lotes.
   - Limitaciones: ruido/falsos positivos; requiere NLP y scoring.
   - Cache: snapshots 5–15m + deduplicación.
6. **EIA**
   - Aporta: energía (producción, inventarios, flujos).
   - Latencia: diaria/semanal/mensual.
   - Fiabilidad: alta para energía US/global reportada.
7. **USGS / minerales abiertos**
   - Aporta: depósitos/clusters minerales.
   - Latencia: baja frecuencia.
8. **OpenStreetMap/Overpass**
   - Aporta: infraestructura (puertos/rutas selectas).
   - Limitación: heterogeneidad por región.
9. **Natural Earth**
   - Aporta: base cartográfica global consistente.
   - Uso: base L4 estable.
10. **Open-Meteo**
   - Aporta: clima para riesgo logístico/agro/energía.
   - Uso: capa contextual, no driver único.
11. **Alpha Vantage (opcional)**
   - Aporta: market free-tier complementario.
   - Limitación: cuotas estrictas.
   - Mitigación: polling escalonado + cache agresiva + priorización watchlist.

### Honestidad obligatoria
- No habrá tick-level institucional ni book depth real con fuentes 100% gratis.
- Parte de “tiempo real” será **near real time** (segundos/minutos).
- Cobertura geopolítica será potente pero imperfecta (ruido OSINT).
- Se necesita scoring e inferencia propia para convertir eventos en señal operativa.

## 12. Pipeline realtime y refresh por niveles
1. Ingestion (conectores pull/push según fuente).
2. Normalization (schema canónico por dominio).
3. Entity resolution (country/symbol/event linking).
4. Scoring (severidad, impacto mercado, confianza).
5. Enrichment (join con macro/soberano/energía).
6. Cache publish (edge + core redis-like).
7. Stream UI (SSE/WebSocket channels por watchlist).
8. Snapshotting (cada N min para replay).
9. Invalidation (TTL + event-driven busting).
10. Graceful degradation (fallback a último dato confiable con badge de frescura).

## 13. Estrategia de caché y edge
- **Edge-first read path** para vistas de alto tráfico (globo global, cards populares).
- TTL por clase:
  - L1: 30s–300s,
  - L2: 15m–2h,
  - L3: 1d–7d,
  - L4: 30d+.
- `stale-while-revalidate` para UX fluida.
- Presupuesto de cuota por fuente: token bucket por provider + priorización por watchlist activa.
- Prefetch de rutas de UI críticas (country/symbol cards más consultadas).

## 14. Paneles y vistas
### Layout maestro
- Centro: viewport globo 3D dominante.
- Sidebar izquierda: navegación, taxonomías, capas, watchlists, presets.
- Sidebar derecha: detalle entidad + causalidad + métricas + “what next”.
- Top bar: búsqueda universal semántica + filtros globales + estado de feeds.
- Bottom rail: timeline + stream + replay scrub.

### Modos de trabajo
- Global Pulse, FX Focus, Macro Stress, Sovereign Debt, Energy & Commodities, Conflict Monitor, Replay, Executive Briefing, Analyst Deep Work.
- Cada modo ajusta: densidad, capas por defecto, énfasis cromático, widgets y comportamiento del panel derecho.

## 15. Sistema de alertas
- Tipos: threshold, régimen, evento geopolítico, divergencia causal, deterioro soberano.
- Severidad: info / watch / warning / critical.
- Canal: in-app, email, webhook (Slack/Teams opcional).
- Reglas compuestas (ejemplo): “si conflicto↑ + chokepoint expuesto + Brent rompe nivel + moneda importadora débil => critical”.
- Cada alerta incluye: por qué, señales, confianza, historial similar, acción sugerida.

## 16. Seguridad y gobernanza
- Auth: OIDC/SAML para enterprise; JWT short-lived.
- AuthZ: RBAC + permisos por vista/capa/watchlist.
- Auditoría: log inmutable de alertas, cambios de reglas, accesos de datos.
- Rate limiting en edge por API key/usuario/IP.
- Gestión de secretos: vault + rotación automática.
- Provenance: toda métrica/alerta muestra fuente y timestamp.
- Data governance: clasificación de alertas y retención definida por tipo.

## 17. Performance y escalabilidad
Objetivos:
- First Meaningful Render: <2.5s en red corporativa estándar.
- Time To Interactive: <4s.
- FPS globo: 45–60 fps desktop, 30+ en laptop media.
- Latencia alerta L1: <10s desde ingestión en fuentes rápidas.
- Miles de eventos: clustering + windowing temporal + virtualización.

Técnicas:
- LOD geoespacial, teselado progresivo, instancing GPU, incremental rendering.
- Query budgets estrictos por vista (p95 <250ms en backend cache hit).
- Caching budgets y precomputation de métricas pesadas.

## 18. Roadmap
### Fase 0 — Research + design system
- Entregables: taxonomía visual, tokens, arquitectura de información, prototipo IA.
- Salida: blueprint UX validado con 5 journeys críticos.

### Fase 1 — Base web + globo + capas core
- Entregables: globo operativo, capas países/bloques/eventos básicos, layout maestro.
- Riesgo: rendimiento inicial.

### Fase 2 — Ingesta APIs + ontología
- Entregables: pipelines L1-L4, schema canónico, entidad-relación, search inicial.
- Riesgo: calidad de resolución de entidades.

### Fase 3 — Cards país/símbolo/evento
- Entregables: fichas completas con causalidad y watchpoints.
- Riesgo: sobrecarga de UI.

### Fase 4 — Alertas + replay
- Entregables: motor de alertas, timeline histórico, snapshots navegables.
- Riesgo: costo de almacenamiento/reproducibilidad.

### Fase 5 — Explainability + scenario engine
- Entregables: “what moved”, simulador de escenarios, confidence trails.
- Riesgo: interpretabilidad de modelos heurísticos.

### Fase 6 — Hardening + scaling + polish flagship
- Entregables: SRE, seguridad enterprise, optimizaciones GPU y UX final.
- Riesgo: complejidad operativa multicomponente.

## 19. Riesgos
### Riesgos mortales
1. **Prometer real-time absoluto con fuentes gratis** → pérdida de credibilidad.
2. **Mapa espectacular pero no analítico** → producto decorativo.
3. **No controlar ruido de GDELT** → alert fatigue y falsos positivos.
4. **Arquitectura sin caché/edge** → UX lenta + rate-limit failures.
5. **Explainability débil** → baja adopción en usuarios institucionales.

Mitigación: SLA de frescura explícito, scoring robusto, caching agresivo, etiquetado de confianza, QA de narrativas.

## 20. Criterios de aceptación
- 90% de consultas “qué mueve X” respondidas con 3+ drivers trazables y confianza.
- FMR <2.5s p75; TTI <4s p75.
- Alertas críticas con falsos positivos <20% tras calibración inicial.
- 100% de vistas con source attribution visible.
- Replay funcional en ventanas de 7/30/90 días.
- 0 dependencias obligatorias de vendors premium para operación base.

## 21. MVP funcional vs versión flagship
### MVP funcional real (12–16 semanas)
- Incluye: globo 3D base, FX Command Center, Macro Pulse, Country/Symbol/Event cards, Global Event Stream, Alert Watchtower v1.
- Fuentes: Frankfurter, FRED, ECB, World Bank, GDELT, Natural Earth, OSM básico.
- Sacrifica: scenario engine avanzado, correlaciones dinámicas complejas, cobertura energética profunda.
- Mantiene: valor operativo real de trading/macro con explainability inicial.

### Flagship (24–40 semanas)
- Incluye todos los módulos, replay avanzado, scenario builder, transmission map de alta fidelidad, optimizaciones visuales profundas.
- Fuentes ampliadas: EIA, USGS, Open-Meteo, capas energéticas/recursos densas.
- Riesgo: complejidad de data quality y tuning de performance.

## 22. Stack recomendado final
- **Frontend:** Next.js + React + TypeScript.
- **3D/Geo:** CesiumJS (núcleo) + deck.gl (analítica) + MapLibre (2D complementario).
- **Edge:** Cloudflare Workers + KV + Durable Objects + CDN Cache.
- **Backend:** FastAPI/Node Fastify microservices.
- **DB principal:** Postgres + PostGIS + Timescale.
- **Search:** OpenSearch.
- **Graph:** Neo4j Community (flagship) / AGE (alternativa integrada Postgres).
- **Streaming:** NATS/Redpanda + SSE/WebSockets.
- **Queue/Jobs:** Temporal (preferido) o Celery/Arq.
- **Storage:** R2/S3 para snapshots y replay.
- **Observabilidad:** OpenTelemetry + Prometheus + Grafana + Loki.
- **CI/CD:** GitHub Actions + IaC (Terraform).

## 23. Backlog inicial priorizado
### P0 (imprescindible)
1. Canonical schema + ontología base.
2. Ingestores Frankfurter/FRED/GDELT/Natural Earth.
3. Globo 3D con capas países/eventos + timeline.
4. Search universal (país/símbolo/evento).
5. Country & Symbol Intelligence Cards v1.
6. Alertas básicas por umbral/evento.
7. Capa de caché edge con TTL por frescura.

### P1 (alta)
8. Sovereign Risk Monitor v1.
9. What Moved Markets? Engine heurístico.
10. Conflict-to-Market map v1.
11. Replay 30/90 días.
12. Watchlists y saved views.

### P2 (siguiente)
13. Energy Security Panel completo (EIA).
14. Cross-Asset Correlation Explorer.
15. Scenario Builder v1.
16. Explainability pane avanzado con trazas causales.

## Demo journey irresistible (operativa real)
1. Abrir en **Global Pulse**: mapa muestra focos de conflicto y stress soberano.
2. Click en chokepoint crítico: se iluminan rutas energéticas y países expuestos.
3. Panel derecho explica impacto probable en Brent + divisas importadoras.
4. Salto por deep link a **USD/JPY Symbol Card** con drivers activos.
5. Activar compare T-24h vs now: “what changed” destaca shock + correlación rota.
6. Guardar vista y crear alerta compuesta con watchpoints de la próxima sesión.

---

## Decisiones duras y trade-offs
- Priorizamos **consistencia causal + trazabilidad** sobre pseudo-real-time.
- Priorizamos **latencia percibida** (edge cache + streaming incremental) sobre exactitud tick-by-tick inexistente en free-tier.
- Priorizamos **módulos de decisión de trading** sobre amplitud enciclopédica de datos.
- Priorizamos **arquitectura web-first** con opción híbrida de rendering, sin dependencia nativa obligatoria.
