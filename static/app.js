/* global Cesium */
const statusEl = document.getElementById('status');
const fxJson = document.getElementById('fx-json');
const countryJson = document.getElementById('country-json');
const eventsEl = document.getElementById('events');
const fxList = document.getElementById('fx-list');

const viewer = new Cesium.Viewer('globe', {
  animation: false,
  timeline: false,
  baseLayerPicker: false,
  geocoder: false,
  homeButton: true,
  sceneModePicker: false,
  navigationHelpButton: false,
});

viewer.scene.globe.enableLighting = true;
viewer.scene.skyBox.show = true;
viewer.scene.backgroundColor = Cesium.Color.fromCssColorString('#0b0d10');

const eventEntities = [];

async function getJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function addEventMarker(evt) {
  const lat = evt?.location?.lat;
  const lon = evt?.location?.lon;
  if (typeof lat !== 'number' || typeof lon !== 'number') return;

  const entity = viewer.entities.add({
    position: Cesium.Cartesian3.fromDegrees(lon, lat),
    point: { pixelSize: 8, color: Cesium.Color.RED.withAlpha(0.8) },
    label: {
      text: (evt.title || 'evento').slice(0, 32),
      font: '11px sans-serif',
      fillColor: Cesium.Color.CYAN,
      showBackground: true,
      horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
      pixelOffset: new Cesium.Cartesian2(10, 0),
      distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 3000000),
    },
  });
  eventEntities.push(entity);
}

function renderEvents(events) {
  eventsEl.innerHTML = '';
  eventEntities.forEach((e) => viewer.entities.remove(e));
  eventEntities.length = 0;

  events.slice(0, 15).forEach((evt) => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = evt.url || '#';
    a.target = '_blank';
    a.rel = 'noreferrer';
    a.textContent = evt.title || 'Sin título';
    const span = document.createElement('span');
    span.textContent = ` ${evt.location?.name || 'N/A'} · ${evt.seendate || ''}`;
    li.appendChild(a);
    li.appendChild(span);
    eventsEl.appendChild(li);
    addEventMarker(evt);
  });
}

function renderFx(rates) {
  fxList.innerHTML = '';
  Object.entries(rates).forEach(([symbol, value]) => {
    const li = document.createElement('li');
    li.textContent = `${symbol}: ${value}`;
    fxList.appendChild(li);
  });
}

async function refresh() {
  statusEl.textContent = 'Sincronizando…';
  try {
    const data = await getJson('/api/overview?base=USD&country=MEX');
    fxJson.textContent = JSON.stringify(data.fx, null, 2);
    countryJson.textContent = JSON.stringify(data.country, null, 2);

    if (data.fx?.rates) renderFx(data.fx.rates);
    if (data.events?.events) renderEvents(data.events.events);

    statusEl.textContent = `OK · ${new Date().toLocaleTimeString()}`;
  } catch (err) {
    statusEl.textContent = `Error de datos: ${err.message}`;
  }
}

function hookToggles() {
  document.getElementById('toggle-events').addEventListener('change', (e) => {
    const show = e.target.checked;
    eventsEl.parentElement.style.display = show ? 'block' : 'none';
    eventEntities.forEach((ent) => {
      ent.show = show;
    });
  });

  document.getElementById('toggle-fx').addEventListener('change', (e) => {
    document.getElementById('fx-panel').style.display = e.target.checked ? 'block' : 'none';
  });

  document.getElementById('toggle-country').addEventListener('change', (e) => {
    document.getElementById('country-panel').style.display = e.target.checked ? 'block' : 'none';
  });
}

hookToggles();
refresh();
setInterval(refresh, 120000);
