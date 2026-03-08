/* global Cesium */

const statusEl = document.getElementById('status');
const countrySelect = document.getElementById('country-select');
const watchlistEl = document.getElementById('watchlist');
const assetContextEl = document.getElementById('asset-context');
const newsFeedEl = document.getElementById('news-feed');
const countryCardEl = document.getElementById('country-card');
const indicesEl = document.getElementById('indices');
const ribbonEl = document.getElementById('ribbon');
const clockLocalEl = document.getElementById('clock-local');
const clockUtcEl = document.getElementById('clock-utc');

let selectedAsset = 'XAUUSD';
let dashboardData = null;

const viewer = new Cesium.Viewer('globe', {
  imageryProvider: new Cesium.OpenStreetMapImageryProvider({ url: 'https://tile.openstreetmap.org/' }),
  animation: false,
  timeline: false,
  baseLayerPicker: false,
  geocoder: false,
  sceneModePicker: false,
  navigationHelpButton: false,
  homeButton: true,
  infoBox: false,
});

viewer.scene.globe.enableLighting = true;
viewer.scene.skyAtmosphere.show = true;
viewer.scene.backgroundColor = Cesium.Color.fromCssColorString('#05070a');
viewer.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(10, 24, 16_000_000) });

const eventEntities = [];
const routeEntities = [];
const chokepointEntities = [];

const routes = [
  { from: [56, 26], to: [67, 24] },
  { from: [32.5, 30], to: [14, 36] },
  { from: [101, 2], to: [113, 22] },
  { from: [78, 6], to: [45, 12] },
];

const chokepoints = [
  { name: 'Hormuz', lon: 56.2, lat: 26.5 },
  { name: 'Suez', lon: 32.3, lat: 30.6 },
  { name: 'Bab el-Mandeb', lon: 43.3, lat: 12.7 },
  { name: 'Malacca', lon: 101.5, lat: 2.5 },
];

function renderStaticGeoLayers() {
  routeEntities.forEach((e) => viewer.entities.remove(e));
  chokepointEntities.forEach((e) => viewer.entities.remove(e));
  routeEntities.length = 0;
  chokepointEntities.length = 0;

  routes.forEach((r) => {
    routeEntities.push(viewer.entities.add({
      polyline: {
        positions: Cesium.Cartesian3.fromDegreesArray([r.from[0], r.from[1], r.to[0], r.to[1]]),
        width: 2,
        material: Cesium.Color.fromCssColorString('#c89a4a').withAlpha(0.85),
      }
    }));
  });

  chokepoints.forEach((c) => {
    chokepointEntities.push(viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(c.lon, c.lat),
      point: { pixelSize: 8, color: Cesium.Color.fromCssColorString('#c89a4a') },
      label: {
        text: c.name,
        font: '11px sans-serif',
        fillColor: Cesium.Color.WHITE,
        showBackground: true,
        backgroundColor: Cesium.Color.fromCssColorString('#111827').withAlpha(0.85),
        pixelOffset: new Cesium.Cartesian2(8, 0),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 5_000_000),
      }
    }));
  });
}

function formatNum(v) {
  if (typeof v !== 'number') return 'N/A';
  if (Math.abs(v) >= 1_000_000_000) return `${(v / 1_000_000_000).toFixed(1)}B`;
  if (Math.abs(v) >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  return v.toFixed(2);
}

function updateClocks() {
  const now = new Date();
  clockLocalEl.textContent = `Local ${now.toLocaleTimeString()}`;
  clockUtcEl.textContent = `UTC ${now.toISOString().slice(11, 19)}`;
}

async function getJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function renderWatchlist(items) {
  watchlistEl.innerHTML = '';
  items.forEach((item) => {
    const row = document.createElement('div');
    row.className = `watch-row ${item.symbol === selectedAsset ? 'active' : ''}`;
    row.innerHTML = `
      <div class="watch-symbol">${item.symbol}</div>
      <div class="watch-price">${item.price}</div>
      <div class="watch-change ${item.direction === 'up' ? 'up' : 'down'}">${item.change_pct > 0 ? '+' : ''}${item.change_pct}%</div>
    `;
    row.addEventListener('click', async () => {
      selectedAsset = item.symbol;
      await refresh();
    });
    watchlistEl.appendChild(row);
  });
}

function renderAssetContext(ctx) {
  const r = ctx.returns || {};
  assetContextEl.innerHTML = `
    <div class="kv"><span class="k">Activo</span><span class="v">${ctx.symbol}</span></div>
    <div class="kv"><span class="k">Precio</span><span class="v">${ctx.price}</span></div>
    <div class="kv"><span class="k">Momentum</span><span class="v">${ctx.momentum}</span></div>
    <div class="kv"><span class="k">Volatilidad</span><span class="v">${ctx.volatility}</span></div>
    <div class="kv"><span class="k">1W</span><span class="v">${r['1W']}%</span></div>
    <div class="kv"><span class="k">1M</span><span class="v">${r['1M']}%</span></div>
    <div class="kv"><span class="k">3M</span><span class="v">${r['3M']}%</span></div>
    <div class="kv"><span class="k">YTD</span><span class="v">${r['YTD']}%</span></div>
    <div class="small">${ctx.note || ''}</div>
  `;
}

function renderNews(feed, selectedSymbol) {
  newsFeedEl.innerHTML = '';
  const events = feed.events || [];
  const filtered = selectedSymbol
    ? events.filter((e) => (e.market_impact || []).join(',').toUpperCase().includes(selectedSymbol.replace('/', '')) || selectedSymbol.includes('USD'))
    : events;

  (filtered.length ? filtered : events).slice(0, 10).forEach((n) => {
    const card = document.createElement('div');
    card.className = 'news-item';
    card.innerHTML = `
      <div class="news-head">
        <span class="news-tag">${n.category || 'News'}</span>
        <span class="news-sev">sev ${n.severity ?? 'n/a'}</span>
      </div>
      <div class="news-title">${n.title || 'Sin titular'}</div>
      <div class="small">${n.summary || ''}</div>
      <div class="news-meta">${n.location?.name || 'N/A'} · ${(n.market_impact || []).join(', ')} · ${n.bias || 'neutral'} · ${n.status || 'developing'}</div>
    `;

    card.addEventListener('click', () => {
      const lat = n.location?.lat;
      const lon = n.location?.lon;
      if (typeof lat === 'number' && typeof lon === 'number') {
        viewer.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(lon, lat, 2_500_000) });
      }
    });
    newsFeedEl.appendChild(card);
  });
}

function renderCountry(country) {
  const i = country.indicators || {};
  const sr = country.sovereign_risk || {};
  countryCardEl.innerHTML = `
    <div class="kv"><span class="k">ISO3</span><span class="v">${country.iso3 || 'N/A'}</span></div>
    <div class="kv"><span class="k">GDP growth</span><span class="v">${formatNum(i.gdp_growth?.value)}%</span></div>
    <div class="kv"><span class="k">Inflación</span><span class="v">${formatNum(i.inflation?.value)}%</span></div>
    <div class="kv"><span class="k">Deuda/PIB</span><span class="v">${formatNum(i.debt_gdp?.value)}%</span></div>
    <div class="kv"><span class="k">Reservas</span><span class="v">${formatNum(i.reserves?.value)}</span></div>
    <div class="kv"><span class="k">Balance comercial</span><span class="v">${formatNum(i.trade_balance?.value)}</span></div>
    <div class="kv"><span class="k">Riesgo soberano</span><span class="v">${sr.score} (${sr.bucket})</span></div>
  `;
}

function renderIndices(indices) {
  indicesEl.innerHTML = '';
  Object.entries(indices).forEach(([region, rows]) => {
    const block = document.createElement('div');
    block.className = 'indices-block';
    block.innerHTML = `<h4>${region}</h4>`;
    rows.forEach((r) => {
      const row = document.createElement('div');
      row.className = 'index-row';
      row.innerHTML = `<span>${r.name}</span><span class="${r.change_pct >= 0 ? 'up' : 'down'}">${r.change_pct > 0 ? '+' : ''}${r.change_pct}%</span>`;
      block.appendChild(row);
    });
    indicesEl.appendChild(block);
  });
}

function renderRibbon(items) {
  ribbonEl.innerHTML = '';
  items.forEach((x) => {
    const div = document.createElement('div');
    div.className = 'ribbon-item';
    div.innerHTML = `<span class="sym">${x.symbol}</span>: ${x.price} <span class="${x.change_pct >= 0 ? 'up' : 'down'}">${x.change_pct > 0 ? '+' : ''}${x.change_pct}%</span>`;
    ribbonEl.appendChild(div);
  });
}

function renderEventMarkers(feed) {
  eventEntities.forEach((e) => viewer.entities.remove(e));
  eventEntities.length = 0;

  (feed.events || []).slice(0, 20).forEach((evt) => {
    const lat = evt?.location?.lat;
    const lon = evt?.location?.lon;
    if (typeof lat !== 'number' || typeof lon !== 'number') return;
    const sev = evt.severity || 0;
    const color = sev >= 70 ? Cesium.Color.RED : sev >= 45 ? Cesium.Color.ORANGE : Cesium.Color.YELLOW;
    eventEntities.push(viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(lon, lat),
      point: { pixelSize: 7 + Math.floor(sev / 20), color: color.withAlpha(0.85) },
      label: {
        text: (evt.title || 'evento').slice(0, 25),
        font: '11px sans-serif',
        fillColor: Cesium.Color.CYAN,
        showBackground: true,
        backgroundColor: Cesium.Color.fromCssColorString('#111827').withAlpha(0.8),
        pixelOffset: new Cesium.Cartesian2(8, 0),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 3_000_000),
      }
    }));
  });
}

function renderFeedStatus(feeds) {
  const chips = Object.entries(feeds).map(([k, v]) => {
    const degraded = v.degraded;
    const lat = v.latency_ms ? `${v.latency_ms}ms` : 'n/a';
    return `<span class="feed-chip ${degraded ? 'degraded' : ''}">${k.toUpperCase()} ${lat}${degraded ? ' degraded' : ''}</span>`;
  }).join('');
  statusEl.innerHTML = `<div class="feed-chip-wrap">${chips}</div>`;
}

async function refresh() {
  updateClocks();
  const country = countrySelect.value;
  try {
    const data = await getJson(`/api/dashboard?country=${country}&asset=${selectedAsset}&base=USD`);
    dashboardData = data;

    renderFeedStatus(data.system_status.feeds);
    renderWatchlist(data.watchlist || []);
    renderAssetContext(data.asset_context || {});
    renderNews(data.news_feed || {}, selectedAsset);
    renderCountry(data.country || {});
    renderIndices(data.indices || {});
    renderRibbon(data.ribbon || []);
    renderEventMarkers(data.news_feed || {});
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  }
}

function bindControls() {
  countrySelect.addEventListener('change', refresh);

  document.getElementById('toggle-events').addEventListener('change', (e) => {
    eventEntities.forEach((ent) => { ent.show = e.target.checked; });
  });

  document.getElementById('toggle-routes').addEventListener('change', (e) => {
    routeEntities.forEach((ent) => { ent.show = e.target.checked; });
  });

  document.getElementById('toggle-chokepoints').addEventListener('change', (e) => {
    chokepointEntities.forEach((ent) => { ent.show = e.target.checked; });
  });
}

bindControls();
renderStaticGeoLayers();
refresh();
setInterval(refresh, 90_000);
setInterval(updateClocks, 1_000);
