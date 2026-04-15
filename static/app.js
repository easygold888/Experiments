const statusEl = document.getElementById('status');
const watchlistEl = document.getElementById('watchlist');
const assetContextEl = document.getElementById('asset-context');
const newsFeedEl = document.getElementById('news-feed');
const countryCardEl = document.getElementById('country-card');
const ribbonEl = document.getElementById('ribbon');
const aggregationsEl = document.getElementById('aggregations');
const eventRadarEl = document.getElementById('event-radar');
const opsMapEl = document.getElementById('ops-map');
const clockLocalEl = document.getElementById('clock-local');
const clockUtcEl = document.getElementById('clock-utc');

const countriesInput = document.getElementById('countries');
const continentsInput = document.getElementById('continents');
const categoriesInput = document.getElementById('categories');
const keywordInput = document.getElementById('keyword');
const limitInput = document.getElementById('limit');
const applyButton = document.getElementById('apply-filters');

let selectedAsset = 'XAUUSD';

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

function formatNum(v) {
  if (typeof v !== 'number') return 'N/A';
  if (Math.abs(v) >= 1_000_000_000) return `${(v / 1_000_000_000).toFixed(1)}B`;
  if (Math.abs(v) >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  return v.toFixed(2);
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
    row.addEventListener('click', () => {
      selectedAsset = item.symbol;
      refreshAll();
    });
    watchlistEl.appendChild(row);
  });
}

function renderAssetContext(ctx) {
  const r = ctx.returns || {};
  assetContextEl.innerHTML = `
    <div class="kv"><span class="k">Activo</span><span class="v">${ctx.symbol || 'N/A'}</span></div>
    <div class="kv"><span class="k">Precio</span><span class="v">${ctx.price || 'N/A'}</span></div>
    <div class="kv"><span class="k">Momentum</span><span class="v">${ctx.momentum || 'N/A'}</span></div>
    <div class="kv"><span class="k">Volatilidad</span><span class="v">${ctx.volatility || 'N/A'}</span></div>
    <div class="kv"><span class="k">1W</span><span class="v">${r['1W'] || 'N/A'}%</span></div>
    <div class="kv"><span class="k">1M</span><span class="v">${r['1M'] || 'N/A'}%</span></div>
    <div class="small">${ctx.note || ''}</div>
  `;
}

function lonLatToPoint(lon, lat, width, height) {
  const x = ((Number(lon) + 180) / 360) * width;
  const y = ((90 - Number(lat)) / 180) * height;
  return { x, y };
}

function renderOpsMap(events) {
  const width = opsMapEl.clientWidth || 760;
  const height = 280;
  opsMapEl.innerHTML = `<div class="map-grid"></div>`;

  events.slice(0, 80).forEach((evt) => {
    const lat = evt?.location?.lat;
    const lon = evt?.location?.lon;
    if (typeof lat !== 'number' || typeof lon !== 'number') return;
    const point = lonLatToPoint(lon, lat, width, height);
    const sev = evt.severity || 0;
    const marker = document.createElement('div');
    marker.className = `map-marker ${sev >= 70 ? 'hot' : sev >= 45 ? 'warm' : 'cold'}`;
    marker.style.left = `${point.x}px`;
    marker.style.top = `${point.y}px`;
    marker.title = `${evt.title} (${evt.location?.name || 'N/A'})`;
    opsMapEl.appendChild(marker);
  });
}

function renderNews(feed, selectedSymbol) {
  newsFeedEl.innerHTML = '';
  const events = feed.events || [];
  const filtered = selectedSymbol
    ? events.filter((e) => (e.market_impact || []).join(',').toUpperCase().includes(selectedSymbol.replace('/', '')) || selectedSymbol.includes('USD'))
    : events;

  (filtered.length ? filtered : events).slice(0, 120).forEach((n) => {
    const card = document.createElement('div');
    card.className = 'news-item';
    card.innerHTML = `
      <div class="news-head">
        <span class="news-tag">${n.category || 'general'}</span>
        <span class="news-sev">sev ${n.severity ?? 'n/a'}</span>
      </div>
      <div class="news-title">${n.title || 'Sin titular'}</div>
      <div class="small">${n.summary || ''}</div>
      <div class="news-meta">${n.location?.name || 'N/A'} · ${n.location?.continent || 'N/A'} · ${(n.market_impact || []).join(', ')} · ${n.bias || 'neutral'}</div>
    `;
    newsFeedEl.appendChild(card);
  });
}

function renderRadar(events) {
  eventRadarEl.innerHTML = '';
  events.slice(0, 40).forEach((evt, i) => {
    const row = document.createElement('div');
    row.className = 'radar-row';
    row.innerHTML = `<span>#${String(i + 1).padStart(2, '0')}</span><span>${evt.location?.name || 'N/A'}</span><span>${evt.category}</span><span class="${evt.severity >= 70 ? 'down' : evt.severity >= 45 ? 'warn' : 'up'}">${evt.severity}</span>`;
    eventRadarEl.appendChild(row);
  });
}

function renderAggregations(agg) {
  const renderBlock = (title, obj) => {
    const entries = Object.entries(obj || {}).sort((a, b) => b[1] - a[1]).slice(0, 10);
    return `
      <div class="agg-block">
        <h4>${title}</h4>
        ${entries.map(([k, v]) => `<div class="agg-row"><span>${k}</span><span>${v}</span></div>`).join('')}
      </div>
    `;
  };
  aggregationsEl.innerHTML = renderBlock('Por país', agg.countries)
    + renderBlock('Por continente', agg.continents)
    + renderBlock('Por categoría', agg.categories)
    + renderBlock('Por activo', agg.assets);
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
    <div class="kv"><span class="k">Riesgo soberano</span><span class="v">${sr.score} (${sr.bucket})</span></div>
  `;
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

async function refreshAll() {
  updateClocks();
  statusEl.textContent = 'Cargando central...';
  const countries = countriesInput.value;
  const continents = continentsInput.value;
  const categories = categoriesInput.value;
  const keyword = keywordInput.value;
  const limit = Math.max(20, Math.min(250, Number(limitInput.value) || 120));

  try {
    const [dashboard, hub] = await Promise.all([
      getJson(`/api/dashboard?country=COL&asset=${selectedAsset}&base=USD`),
      getJson(`/api/intelligence/hub?countries=${encodeURIComponent(countries)}&continents=${encodeURIComponent(continents)}&categories=${encodeURIComponent(categories)}&keyword=${encodeURIComponent(keyword)}&limit=${limit}`),
    ]);

    renderWatchlist(dashboard.watchlist || []);
    renderAssetContext(dashboard.asset_context || {});
    renderCountry(dashboard.country || {});
    renderRibbon(dashboard.ribbon || []);

    const feed = hub.feed || { events: [], aggregations: {} };
    const events = feed.events || [];

    renderNews(feed, selectedAsset);
    renderRadar(events);
    renderAggregations(feed.aggregations || {});
    renderOpsMap(events);

    statusEl.textContent = `Operando | noticias=${feed.count || events.length} | proveedor=${feed.provider || 'n/a'} | query=${hub.request?.query || 'n/a'}`;
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  }
}

applyButton.addEventListener('click', refreshAll);
updateClocks();
refreshAll();
setInterval(updateClocks, 1000);
setInterval(refreshAll, 120000);
