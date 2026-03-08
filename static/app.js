/* global Cesium */
const statusEl = document.getElementById('status');
const fxList = document.getElementById('fx-list');
const eventsEl = document.getElementById('events');
const whatMovedEl = document.getElementById('what-moved');
const transmissionEl = document.getElementById('transmission-list');
const watchpointsEl = document.getElementById('watchpoints');
const countrySummaryEl = document.getElementById('country-summary');
const regimeEl = document.getElementById('regime');
const regimeMetaEl = document.getElementById('regime-meta');
const countrySelect = document.getElementById('country-select');

const OSM = new Cesium.OpenStreetMapImageryProvider({
  url: 'https://tile.openstreetmap.org/'
});

const viewer = new Cesium.Viewer('globe', {
  imageryProvider: OSM,
  baseLayerPicker: false,
  animation: false,
  timeline: false,
  geocoder: false,
  sceneModePicker: false,
  homeButton: true,
  navigationHelpButton: false,
  infoBox: false,
});

viewer.scene.globe.enableLighting = true;
viewer.scene.skyAtmosphere.show = true;
viewer.scene.globe.depthTestAgainstTerrain = false;
viewer.scene.backgroundColor = Cesium.Color.fromCssColorString('#05070a');

const eventEntities = [];
const routeEntities = [];
const chokepointEntities = [];

const routes = [
  { name: 'Hormuz Oil Route', from: [56, 26], to: [67, 24] },
  { name: 'Suez-LNG Corridor', from: [32.5, 30], to: [14, 36] },
  { name: 'Malacca Energy Lane', from: [101, 2], to: [113, 22] },
];

const chokepoints = [
  { name: 'Strait of Hormuz', lon: 56.2, lat: 26.5 },
  { name: 'Suez Canal', lon: 32.3, lat: 30.6 },
  { name: 'Bab el-Mandeb', lon: 43.3, lat: 12.7 },
  { name: 'Strait of Malacca', lon: 101.5, lat: 2.5 },
];

function renderStaticLayers() {
  routeEntities.forEach((r) => viewer.entities.remove(r));
  chokepointEntities.forEach((c) => viewer.entities.remove(c));
  routeEntities.length = 0;
  chokepointEntities.length = 0;

  routes.forEach((r) => {
    routeEntities.push(
      viewer.entities.add({
        polyline: {
          positions: Cesium.Cartesian3.fromDegreesArray([r.from[0], r.from[1], r.to[0], r.to[1]]),
          width: 2,
          material: Cesium.Color.fromCssColorString('#ca9a46').withAlpha(0.8),
          arcType: Cesium.ArcType.GEODESIC,
        },
      })
    );
  });

  chokepoints.forEach((cp) => {
    chokepointEntities.push(
      viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(cp.lon, cp.lat),
        point: { pixelSize: 9, color: Cesium.Color.fromCssColorString('#ca9a46') },
        label: {
          text: cp.name,
          font: '11px sans-serif',
          fillColor: Cesium.Color.fromCssColorString('#f1f5f9'),
          showBackground: true,
          backgroundColor: Cesium.Color.fromCssColorString('#111827').withAlpha(0.8),
          distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 5_000_000),
          pixelOffset: new Cesium.Cartesian2(8, 0),
        },
      })
    );
  });
}

function formatNumber(value) {
  if (typeof value !== 'number') return 'N/A';
  if (Math.abs(value) >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1)}B`;
  if (Math.abs(value) >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  return value.toFixed(2);
}

async function getJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function addEventMarker(evt) {
  const lat = evt?.location?.lat;
  const lon = evt?.location?.lon;
  if (typeof lat !== 'number' || typeof lon !== 'number') return;

  const severity = evt?.severity ?? 0;
  const color = severity >= 70 ? Cesium.Color.RED : severity >= 45 ? Cesium.Color.ORANGE : Cesium.Color.YELLOW;

  const entity = viewer.entities.add({
    position: Cesium.Cartesian3.fromDegrees(lon, lat),
    point: { pixelSize: 7 + Math.round(severity / 20), color: color.withAlpha(0.85) },
    label: {
      text: `${(evt.title || 'evento').slice(0, 28)} (${severity})`,
      font: '11px sans-serif',
      fillColor: Cesium.Color.CYAN,
      showBackground: true,
      backgroundColor: Cesium.Color.fromCssColorString('#111827').withAlpha(0.8),
      horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
      pixelOffset: new Cesium.Cartesian2(10, 0),
      distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 3_000_000),
    },
  });
  eventEntities.push(entity);
}

function renderEvents(events) {
  eventsEl.innerHTML = '';
  eventEntities.forEach((e) => viewer.entities.remove(e));
  eventEntities.length = 0;

  events.slice(0, 20).forEach((evt) => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = evt.url || '#';
    a.target = '_blank';
    a.rel = 'noreferrer';
    a.textContent = evt.title || 'Sin título';

    const sev = document.createElement('span');
    sev.className = 'severity';
    sev.textContent = `sev ${evt.severity ?? 'n/a'}`;

    const meta = document.createElement('div');
    meta.className = 'small';
    meta.textContent = `${evt.location?.name || 'N/A'} · ${(evt.market_impact || []).join(', ')}`;

    li.appendChild(a);
    li.appendChild(document.createTextNode(' '));
    li.appendChild(sev);
    li.appendChild(meta);
    eventsEl.appendChild(li);
    addEventMarker(evt);
  });
}

function renderFx(fx) {
  fxList.innerHTML = '';
  const rates = fx?.rates || {};
  const changes = fx?.changes_1d_pct || {};

  Object.entries(rates).forEach(([symbol, value]) => {
    const li = document.createElement('li');
    const ch = changes[symbol];
    const chText = typeof ch === 'number' ? ` (${ch > 0 ? '+' : ''}${ch.toFixed(2)}%)` : '';
    li.textContent = `${symbol}: ${value}${chText}`;
    fxList.appendChild(li);
  });
}

function renderWhatMoved(items) {
  whatMovedEl.innerHTML = '';
  items.forEach((it) => {
    const li = document.createElement('li');
    li.innerHTML = `<strong>${it.title}</strong><div class="small">${it.why_it_matters} · conf ${Math.round((it.confidence || 0) * 100)}%</div>`;
    whatMovedEl.appendChild(li);
  });
}

function renderTransmission(items) {
  transmissionEl.innerHTML = '';
  items.forEach((it) => {
    const li = document.createElement('li');
    const loc = it.location?.name || 'N/A';
    li.innerHTML = `<strong>${it.event || 'Evento'}</strong><div class="small">Sev ${it.severity} · ${loc} → ${(it.transmits_to || []).join(', ')}</div>`;
    transmissionEl.appendChild(li);
  });
}

function renderCountry(country) {
  const i = country?.indicators || {};
  const risk = country?.sovereign_risk || {};

  countrySummaryEl.innerHTML = `
    <div class="kv"><span class="k">ISO3</span><span class="v">${country.iso3 || 'N/A'}</span></div>
    <div class="kv"><span class="k">GDP growth</span><span class="v">${formatNumber(i.gdp_growth?.value)}%</span></div>
    <div class="kv"><span class="k">Inflación</span><span class="v">${formatNumber(i.inflation?.value)}%</span></div>
    <div class="kv"><span class="k">Deuda/PIB</span><span class="v">${formatNumber(i.debt_gdp?.value)}%</span></div>
    <div class="kv"><span class="k">Reservas</span><span class="v">${formatNumber(i.reserves?.value)}</span></div>
    <div class="kv"><span class="k">Sovereign risk</span><span class="v">${risk.score ?? 'N/A'} (${risk.bucket || 'N/A'})</span></div>
  `;
}

function renderRegime(riskRegime) {
  const regime = riskRegime?.regime || 'N/A';
  regimeEl.textContent = `${regime}`;
  regimeEl.className = 'regime';

  if (regime === 'Risk-Off') regimeEl.classList.add('risk-off');
  else if (regime === 'Risk-On') regimeEl.classList.add('risk-on');
  else regimeEl.classList.add('neutral');

  regimeMetaEl.textContent = `Score ${riskRegime?.composite_score ?? 'N/A'} · FXVol ${riskRegime?.components?.fx_vol_proxy ?? 'N/A'} · EventStress ${riskRegime?.components?.event_stress ?? 'N/A'}`;
}

function renderWatchpoints(points) {
  watchpointsEl.innerHTML = '';
  points.forEach((p) => {
    const li = document.createElement('li');
    li.textContent = p;
    watchpointsEl.appendChild(li);
  });
}

async function refresh() {
  statusEl.textContent = 'Sincronizando inteligencia…';
  const country = countrySelect.value;

  try {
    const data = await getJson(`/api/overview?base=USD&country=${country}`);

    renderFx(data.fx);
    renderEvents(data.events?.events || []);
    renderWhatMoved(data.what_moved || []);
    renderTransmission(data.transmission_map || []);
    renderCountry(data.country || {});
    renderRegime(data.risk_regime || {});
    renderWatchpoints(data.watchpoints || []);

    const degradedFlag = data.degradation?.active ? ' · DEGRADED' : '';
    statusEl.textContent = `OK ${new Date().toLocaleTimeString()}${degradedFlag}`;
  } catch (err) {
    statusEl.textContent = `Error de datos: ${err.message}`;
  }
}

function hookToggles() {
  document.getElementById('toggle-events').addEventListener('change', (e) => {
    const show = e.target.checked;
    eventEntities.forEach((ent) => {
      ent.show = show;
    });
    document.getElementById('events-panel').style.display = show ? 'block' : 'none';
  });

  document.getElementById('toggle-routes').addEventListener('change', (e) => {
    routeEntities.forEach((ent) => {
      ent.show = e.target.checked;
    });
  });

  document.getElementById('toggle-chokepoints').addEventListener('change', (e) => {
    chokepointEntities.forEach((ent) => {
      ent.show = e.target.checked;
    });
  });

  countrySelect.addEventListener('change', refresh);
}

viewer.camera.flyTo({
  destination: Cesium.Cartesian3.fromDegrees(10, 20, 16_000_000),
});

renderStaticLayers();
hookToggles();
refresh();
setInterval(refresh, 90_000);
