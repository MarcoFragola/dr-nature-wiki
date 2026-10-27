/**
 * Geographic cover, separate from the interactive exploration map.
 *
 *   const cover = await mountCinematicCover(host, { lang: 'es' });
 *   await cover.ready;                 // true only after real imagery + DEM
 *   cover.setProgress(scrollFraction); // optional, on-demand camera change
 *   cover.setVisible(isIntersecting);
 *   cover.destroy();
 *
 * The host must have its own CSS dimensions and a positioning context. This
 * module owns only its appended element, never the surrounding HUD or layout.
 * MapLibre GL JS and its CSS must already be loaded from the local vendor copy.
 *
 * Options:
 * - demTiles: string/string[]; defaults to local IGN-derived Terrarium tiles.
 * - bounds: DEM coverage [west,south,east,north], not camera framing bounds.
 * - minzoom/maxzoom: DEM pyramid range; defaults 6..10.
 * - madridBounds: camera bounds; defaults to Madrid's official full extent.
 * - madridBoundaryUrl: official Madrid polygon GeoJSON.
 * - exaggeration, pitch, bearing: visual emphasis and camera, defaults 4.8/54/-12.
 * - padding: CSS-pixel object, or ({width,height}) => object. Default desktop
 *   reserves ~40% on the left and 8% on the right; mobile reserves title space.
 * - imageryTiles, imageryAttribution, demAttribution: explicit source overrides.
 *   Changing a source also requires updating its attribution/evidence.
 * - readyTimeoutMs, visible, labels, lang, onStatus: lifecycle/presentation.
 *
 * Default DEM: IGN WCS Elevacion4258_5 extraction, output grid 1024x1024 over
 * [-4.9,39.65,-2.75,41.45], resampled to a local Terrarium pyramid. Its output
 * sample spacing is approximately 177x196 m: this is NOT a 5 m rendered DEM.
 * Orthoimagery: PNOA/IGN WMTS. Boundaries: official IGN/CNIG geometries.
 * All geographic sources retain their IGN/CNIG CC BY 4.0 attribution.
 * Relief exaggeration changes presentation; no synthetic terrain is generated.
 */

import { installBoundaries, loadBoundaries } from './boundaries.js';

const PNOA_TILES = 'https://www.ign.es/wmts/pnoa-ma?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=OI.OrthoimageCoverage&STYLE=default&FORMAT=image/jpeg&TILEMATRIXSET=GoogleMapsCompatible&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}';
const DEM_TILES = 'data/terrain/tiles/{z}/{x}/{y}.png';
const DEM_BOUNDS = Object.freeze([-4.9, 39.65, -2.75, 41.45]);
const MADRID_BOUNDS = Object.freeze([-4.579076175, 39.884719334, -3.052983314, 41.165844755]);
const IMAGERY_ID = 'cover-orthoimage';
const DEM_ID = 'cover-elevation';
const SHADE_ID = 'cover-elevation-shade';
const IGN_ATTRIBUTION = '<a href="https://www.ign.es/" target="_blank" rel="noopener noreferrer">IGN/CNIG · CC BY 4.0</a>';

export const CINEMATIC_COVER_EVIDENCE = Object.freeze({
  imagery: 'PNOA/IGN orthoimagery, WMTS OI.OrthoimageCoverage',
  imageryUrl: 'https://www.ign.es/wmts/pnoa-ma',
  elevation: 'IGN WCS Elevacion4258_5 extraction; local Terrarium pyramid',
  elevationCoverage: DEM_BOUNDS,
  outputGrid: Object.freeze([1024, 1024]),
  approximateOutputSpacingMetres: Object.freeze([177, 196]),
  pyramidZooms: Object.freeze([6, 10]),
  boundaries: 'Official administrative geometry, IGN/CNIG; no invented provincial borders',
  licence: 'CC BY 4.0 IGN/CNIG; source attribution must remain accessible',
  precisionClaim: null,
});

const PLACES = Object.freeze([
  { name: 'Madrid', coordinates: [-3.7038, 40.4168], capital: true },
  { name: 'Segovia', coordinates: [-4.1184, 40.9429] },
  { name: 'Ávila', coordinates: [-4.6995, 40.6565] },
  { name: 'Guadalajara', coordinates: [-3.1667, 40.6333] },
  { name: 'Cuenca', coordinates: [-2.1374, 40.0719] },
  { name: 'Toledo', coordinates: [-4.0245, 39.8628] },
]);

const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
const toTiles = value => Array.isArray(value) ? [...value] : [value];
const zeroPadding = { left: 0, right: 0, top: 0, bottom: 0 };

function validBounds(value, fallback) {
  if (!Array.isArray(value) || value.length !== 4 || !value.every(Number.isFinite)) return [...fallback];
  const [west, south, east, north] = value;
  return west < east && south < north && west >= -180 && east <= 180 && south > -85 && north < 85 ? [...value] : [...fallback];
}

function signedArea(ring) {
  let area = 0;
  for (let index = 0; index < ring.length - 1; index++) {
    area += ring[index][0] * ring[index + 1][1] - ring[index + 1][0] * ring[index][1];
  }
  return area / 2;
}

function oriented(ring, counterclockwise) {
  const coordinates = ring.map(point => point.slice(0, 2));
  if ((signedArea(coordinates) > 0) !== counterclockwise) coordinates.reverse();
  return coordinates;
}

function polygonParts(data) {
  const features = data.type === 'FeatureCollection' ? data.features : data.type === 'Feature' ? [data] : [{ geometry: data }];
  const polygons = features.flatMap(feature => {
    if (feature.geometry?.type === 'Polygon') return [feature.geometry.coordinates];
    if (feature.geometry?.type === 'MultiPolygon') return feature.geometry.coordinates;
    return [];
  });
  if (!polygons.length || polygons.some(rings => !rings.length || rings.some(ring => ring.length < 4))) throw new Error('Madrid boundary is not a valid polygon');
  return polygons;
}

function outsideMask(polygons) {
  const world = [[-180, -85.05112878], [180, -85.05112878], [180, 85.05112878], [-180, 85.05112878], [-180, -85.05112878]];
  const features = [{ type: 'Feature', properties: {}, geometry: {
    type: 'Polygon', coordinates: [world, ...polygons.map(rings => oriented(rings[0], false))],
  } }];
  // Holes within Madrid remain outside Madrid, including administrative enclaves.
  for (const rings of polygons) {
    for (const hole of rings.slice(1)) features.push({ type: 'Feature', properties: {}, geometry: { type: 'Polygon', coordinates: [oriented(hole, true)] } });
  }
  return { type: 'FeatureCollection', features };
}

function framingSamples(polygons, bounds) {
  const points = polygons.flatMap(rings => rings[0]);
  const stride = Math.max(1, Math.ceil(points.length / 600));
  const samples = points.filter((_, index) => index % stride === 0);
  const [west, south, east, north] = bounds;
  // Actual contour extrema preserve framing without adding empty bbox corners.
  samples.push(points.reduce((a,b)=>a[0]<b[0]?a:b),points.reduce((a,b)=>a[0]>b[0]?a:b),points.reduce((a,b)=>a[1]<b[1]?a:b),points.reduce((a,b)=>a[1]>b[1]?a:b));
  return samples;
}

function defaultPadding({ width, height }) {
  return width >= 850
    ? { left: width * 0.33, right: width * 0.10, top: height * 0.11, bottom: height * 0.12 }
    : { left: width * 0.055, right: width * 0.075, top: height * 0.31, bottom: height * 0.095 };
}

function createStyle(settings) {
  const elevation = {
    type: 'raster-dem', tiles: settings.demTiles, encoding: 'terrarium', tileSize: 256,
    minzoom: settings.minzoom, maxzoom: settings.maxzoom, bounds: settings.bounds,
    attribution: settings.demAttribution,
  };
  return {
    version: 8,
    sources: {
      [IMAGERY_ID]: { type: 'raster', tiles: settings.imageryTiles, tileSize: 256, minzoom: 1, maxzoom: 19, attribution: settings.imageryAttribution },
      [DEM_ID]: elevation,
      [SHADE_ID]: { ...elevation, tiles: [...elevation.tiles] },
    },
    layers: [
      { id: 'cover-background', type: 'background', paint: { 'background-color': '#071214' } },
      { id: 'cover-imagery', type: 'raster', source: IMAGERY_ID, paint: {
        'raster-saturation': -0.10, 'raster-contrast': 0.30,
        'raster-brightness-min': 0.025, 'raster-brightness-max': 0.88,
        'raster-fade-duration': 0,
      } },
      { id: 'cover-hillshade', type: 'hillshade', source: SHADE_ID, paint: {
        'hillshade-illumination-direction': 315,
        'hillshade-illumination-anchor': 'map',
        'hillshade-exaggeration': 0.68,
        'hillshade-shadow-color': 'rgba(2,16,14,0.88)',
        'hillshade-highlight-color': 'rgba(227,224,195,0.24)',
        'hillshade-accent-color': 'rgba(4,24,18,0.45)',
      } },
    ],
    terrain: { source: DEM_ID, exaggeration: settings.exaggeration },
    sky: {
      'sky-color': '#071214', 'horizon-color': '#162822', 'fog-color': '#071214',
      'sky-horizon-blend': 0.80, 'horizon-fog-blend': 0.90, 'fog-ground-blend': 0.12,
    },
    transition: { duration: 0, delay: 0 },
  };
}

export async function mountCinematicCover(host, options = {}) {
  if (!host || typeof host.appendChild !== 'function') throw new TypeError('mountCinematicCover requires a host element');
  const lib = globalThis.maplibregl;
  const settings = {
    demTiles: toTiles(options.demTiles ?? DEM_TILES),
    bounds: validBounds(options.bounds ?? options.demBounds, DEM_BOUNDS),
    minzoom: clamp(Number.isFinite(options.minzoom) ? options.minzoom : 6, 0, 20),
    maxzoom: clamp(Number.isFinite(options.maxzoom) ? options.maxzoom : 10, 0, 22),
    madridBounds: validBounds(options.madridBounds, MADRID_BOUNDS),
    madridBoundaryUrl: options.madridBoundaryUrl ?? 'data/boundaries/madrid.geojson',
    imageryTiles: toTiles(options.imageryTiles ?? PNOA_TILES),
    imageryAttribution: options.imageryAttribution ?? `Ortofoto PNOA · ${IGN_ATTRIBUTION}`,
    demAttribution: options.demAttribution ?? `MDT IGN/CNIG · ${IGN_ATTRIBUTION}`,
    exaggeration: clamp(Number.isFinite(options.exaggeration) ? options.exaggeration : 4.8, 1, 4.8),
    pitch: clamp(Number.isFinite(options.pitch) ? options.pitch : 54, 30, 60),
    bearing: Number.isFinite(options.bearing) ? options.bearing : -12,
    padding: options.padding ?? defaultPadding,
    lang: options.lang === 'en' ? 'en' : 'es',
  };
  settings.maxzoom = Math.max(settings.minzoom, settings.maxzoom);

  const media = window.matchMedia?.('(prefers-reduced-motion: reduce)');
  let reduced = media?.matches ?? false;
  let visible = options.visible !== false;
  let destroyed = false;
  let failed = false;
  let resolved = false;
  let map;
  let frame = null;
  let progress = 0;
  let needsFit = true;
  let samples = [];
  let markerEntries = [];
  let timeout;
  let observer;
  const fetchController = new AbortController();
  const state = { style: false, imagery: false, dem: false, boundary: false, fullBoundaries: false, ready: false, status: 'loading', error: null };
  let resolveReady;
  const ready = new Promise(resolve => { resolveReady = resolve; });

  const root = document.createElement('div');
  root.className = 'cinematic-cover';
  root.dataset.state = 'loading';
  root.style.cssText = `position:absolute;inset:0;overflow:hidden;pointer-events:none;opacity:0;transition:${reduced ? 'none' : 'opacity 1200ms ease'};`;
  const surface = document.createElement('div');
  surface.className = 'cinematic-cover__map';
  surface.style.cssText = 'position:absolute;inset:0;';
  const vignette = document.createElement('div');
  vignette.className = 'cinematic-cover__vignette';
  vignette.style.cssText = 'position:absolute;inset:0;pointer-events:none;background:linear-gradient(90deg,rgba(7,18,20,.98),rgba(7,18,20,.76) 23%,rgba(7,18,20,.10) 49%,rgba(7,18,20,.03) 73%,rgba(7,18,20,.28)),linear-gradient(180deg,rgba(7,18,20,.64),transparent 23%,transparent 68%,rgba(7,18,20,.7));';
  root.append(surface, vignette);
  host.appendChild(root);

  const evidence = Object.freeze({ ...CINEMATIC_COVER_EVIDENCE,
    demTiles: Object.freeze([...settings.demTiles]), elevationCoverage: Object.freeze([...settings.bounds]),
    verticalExaggeration: settings.exaggeration,
    sourceOverride: Boolean(options.demTiles || options.imageryTiles),
  });

  function notify() {
    root.dataset.state = state.status;
    root.dataset.imagery = String(state.imagery);
    root.dataset.elevation = String(state.dem);
    root.dataset.boundary = String(state.boundary);
    const detail = { ...state, evidence };
    host.dispatchEvent(new CustomEvent('cinematiccover:status', { detail }));
    try { options.onStatus?.(detail); } catch { /* A consumer callback must not break the map. */ }
  }

  function settle(value) {
    if (resolved) return;
    resolved = true;
    clearTimeout(timeout);
    resolveReady(value);
  }

  function fail(error) {
    if (destroyed || failed) return;
    failed = true;
    state.ready = false;
    state.status = 'unavailable';
    state.error = error instanceof Error ? error.message : String(error);
    root.style.opacity = '0';
    cancelFrame();
    if (map) { map.stop(); map.remove(); map = null; }
    notify();
    settle(false);
  }

  function cancelFrame() {
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null;
  }

  function padding() {
    const width = Math.max(1, surface.clientWidth), height = Math.max(1, surface.clientHeight);
    const input = typeof settings.padding === 'function' ? settings.padding({ width, height }) : settings.padding;
    const values = {};
    for (const edge of ['left', 'right', 'top', 'bottom']) values[edge] = clamp(Number(input?.[edge]) || 0, 0, (edge === 'left' || edge === 'right' ? width : height) * 0.46);
    return { values, width, height };
  }

  function projectedExtent() {
    const extent = { left: Infinity, right: -Infinity, top: Infinity, bottom: -Infinity };
    for (const point of samples) {
      const pixel = map.project(point);
      if (!Number.isFinite(pixel.x) || !Number.isFinite(pixel.y)) continue;
      extent.left = Math.min(extent.left, pixel.x);
      extent.right = Math.max(extent.right, pixel.x);
      extent.top = Math.min(extent.top, pixel.y);
      extent.bottom = Math.max(extent.bottom, pixel.y);
    }
    return extent;
  }

  function containContour(pad, width, height) {
    if (!samples.length) return;
    const margin = Math.max(20, Math.min(width, height) * 0.025);
    const allowed = { left: pad.left + margin, right: width - pad.right - margin, top: pad.top + margin, bottom: height - pad.bottom - margin };
    const targetX = (allowed.left + allowed.right) / 2, targetY = (allowed.top + allowed.bottom) / 2;
    for (let pass = 0; pass < 4; pass++) {
      const extent = projectedExtent();
      if (!Number.isFinite(extent.left)) break;
      const factor = Math.max((extent.right - extent.left) / Math.max(1, allowed.right - allowed.left), (extent.bottom - extent.top) / Math.max(1, allowed.bottom - allowed.top));
      if (factor > 1.005) {
        map.jumpTo({ zoom: Math.max(5, map.getZoom() - Math.log2(factor) - 0.025) });
        continue;
      }
      if(factor<.88){map.jumpTo({zoom:Math.min(9.25,map.getZoom()+Math.min(.5,Math.log2(.94/factor)))});continue;}
      const dx = (extent.left + extent.right) / 2 - targetX;
      const dy = (extent.top + extent.bottom) / 2 - targetY;
      if (Math.hypot(dx, dy) < 3) break;
      const center = map.unproject([width / 2 + dx, height / 2 + dy]);
      map.jumpTo({ center });
    }
  }

  function applyCamera(fit) {
    if (!map || !state.style || !surface.clientWidth || !surface.clientHeight) return;
    const amount = reduced ? 0 : progress;
    const bearing = settings.bearing + amount * 3.5;
    const pitch = settings.pitch + amount * Math.min(2, 60 - settings.pitch);
    const { values: pad, width, height } = padding();
    if (fit) {
      const bounds = [[settings.madridBounds[0], settings.madridBounds[1]], [settings.madridBounds[2], settings.madridBounds[3]]];
      const camera = map.cameraForBounds(bounds, { padding: pad, bearing, maxZoom: 9.25 });
      if (camera) {
        // cameraForBounds incorporates padding in its returned centre. Keeping
        // persistent map padding as well would offset the cover a second time.
        map.jumpTo({ ...camera, padding: zeroPadding, bearing, pitch });
      }
    } else map.jumpTo({ bearing, pitch });
    containContour(pad, width, height);
    updateLabels();
  }

  function requestFrame(fit = false) {
    needsFit ||= fit;
    if (destroyed || failed || !visible || document.hidden || frame !== null) return;
    frame = requestAnimationFrame(() => {
      frame = null;
      const shouldFit = needsFit;
      needsFit = false;
      applyCamera(shouldFit);
      checkReady();
    });
  }

  function updateLabels() {
    if (!map) return;
    const width = surface.clientWidth, height = surface.clientHeight;
    for (const { place, element } of markerEntries) {
      const point = map.project(place.coordinates);
      const left = width >= 850 ? width * 0.34 : 18;
      element.style.visibility = visible && point.x > left && point.x < width - 58 && point.y > height * 0.12 && point.y < height * 0.88 ? 'visible' : 'hidden';
    }
  }

  function createLabels() {
    if (options.labels === false) return;
    markerEntries = PLACES.map(place => {
      const element = document.createElement('div');
      element.className = `cinematic-cover__label${place.capital ? ' cinematic-cover__label--capital' : ''}`;
      element.setAttribute('aria-hidden', 'true');
      element.style.cssText = `pointer-events:none;white-space:nowrap;text-align:center;text-transform:uppercase;font:500 ${place.capital ? '14' : '10'}px Manrope,Arial,sans-serif;letter-spacing:${place.capital ? '.26' : '.30'}em;color:${place.capital ? '#f2f3e9' : '#c7d0c5'};text-shadow:0 1px 7px #071214,0 0 20px #071214;line-height:1.5;`;
      const name = document.createElement('span');
      name.textContent = place.name;
      const dot = document.createElement('span');
      dot.style.cssText = `display:block;margin:7px auto 0;width:${place.capital ? '6' : '3'}px;height:${place.capital ? '6' : '3'}px;border:1px solid #e1e8dd;border-radius:50%;background:#a5bca255;box-shadow:0 0 0 ${place.capital ? '3' : '1'}px #07121485;`;
      element.append(name, dot);
      const marker = new lib.Marker({ element, anchor: 'bottom', offset: [0, 2] }).setLngLat(place.coordinates).addTo(map);
      return { marker, element, place };
    });
    updateLabels();
  }

  function createAttribution() {
    const caption = document.createElement('div');
    caption.className = 'cinematic-cover__attribution';
    caption.style.cssText = 'position:absolute;left:24px;bottom:16px;max-width:calc(100% - 48px);font:10px/1.5 Manrope,Arial,sans-serif;letter-spacing:.025em;color:#b7c3ba;pointer-events:auto;text-shadow:0 1px 6px #071214;';
    const link = document.createElement('a');
    link.href = 'https://www.ign.es/';
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = settings.lang === 'es' ? 'PNOA · MDT y límites IGN/CNIG' : 'PNOA · IGN/CNIG elevation & boundaries';
    link.style.cssText = 'color:inherit;text-decoration:none;';
    const emphasis = document.createElement('span');
    emphasis.textContent = ` · ${settings.lang === 'es' ? 'Relieve' : 'Relief'} ×${settings.exaggeration.toLocaleString(settings.lang === 'es' ? 'es-ES' : 'en-GB')} · CC BY 4.0`;
    emphasis.title = settings.lang === 'es' ? 'Realce vertical visual. No modifica los datos de elevación.' : 'Visual vertical emphasis. The source elevation data is unchanged.';
    caption.append(link, emphasis);
    root.appendChild(caption);
  }

  function terrainIsReal() {
    if (!state.dem || !map?.queryTerrainElevation) return false;
    const locations = [[-3.98, 40.835], [-4.05, 40.79], [-3.95, 40.95], [-3.70, 40.42]];
    const heights = locations.map(point => map.queryTerrainElevation(point) / settings.exaggeration).filter(value => Number.isFinite(value) && value > 100 && value < 3500);
    return heights.length >= 2 && Math.max(...heights) - Math.min(...heights) > 20;
  }

  function checkReady() {
    if (destroyed || failed || state.ready || !map || !state.style || !state.boundary || !state.imagery || !state.dem) return;
    try {
      if (!map.isSourceLoaded(IMAGERY_ID) || !map.isSourceLoaded(DEM_ID)
        || !map.isSourceLoaded('cover-madrid') || !map.isSourceLoaded('cover-outside-madrid') || !terrainIsReal()) return;
      state.ready = true;
      state.status = 'ready';
      state.error = null;
      root.style.opacity = visible ? '1' : '0';
      notify();
      settle(true);
    } catch { /* A source can be between render/upload phases; wait for its next event. */ }
  }

  const resize = () => {
    if (destroyed || failed || !map) return;
    map.resize();
    requestFrame(true);
  };
  const motionChanged = event => { reduced = event.matches; root.style.transition = reduced ? 'none' : 'opacity 1200ms ease'; requestFrame(true); };
  const documentVisibilityChanged = () => { if (document.hidden) cancelFrame(); else if (visible) requestFrame(true); };

  const controller = {
    ready,
    resize,
    setVisible(value) {
      if (destroyed || failed) return;
      const next = Boolean(value);
      if (visible === next) return;
      visible = next;
      root.style.opacity = visible && state.ready ? '1' : '0';
      if (visible) resize();
      else { cancelFrame(); map?.stop(); updateLabels(); }
    },
    setProgress(value) {
      if (destroyed || failed || !Number.isFinite(value)) return;
      const next = clamp(value, 0, 1);
      if (Math.abs(next - progress) < 0.002) return;
      progress = next;
      if (!reduced) requestFrame();
    },
    destroy() {
      if (destroyed) return;
      destroyed = true;
      cancelFrame();
      clearTimeout(timeout);
      fetchController.abort();
      observer?.disconnect();
      window.removeEventListener('resize', resize);
      document.removeEventListener('visibilitychange', documentVisibilityChanged);
      if (media?.removeEventListener) media.removeEventListener('change', motionChanged);
      else media?.removeListener?.(motionChanged);
      markerEntries.forEach(({ marker }) => marker.remove());
      markerEntries = [];
      if (map) { map.remove(); map = null; }
      root.remove();
      state.ready = false;
      state.status = 'destroyed';
      settle(false);
    },
    get status() { return { ...state }; },
    get evidence() { return evidence; },
  };

  if (!lib?.Map || !lib?.Marker) {
    fail(new Error('The local MapLibre runtime is unavailable'));
    return controller;
  }

  const madridData = fetch(settings.madridBoundaryUrl, { signal: fetchController.signal }).then(response => {
    if (!response.ok) throw new Error('Official Madrid geometry could not load');
    return response.json();
  });
  // Both are started once. Rejections are consumed now, including if WebGL fails.
  const boundaryData = Promise.all([madridData, loadBoundaries()]);
  boundaryData.catch(() => {});

  try {
    map = new lib.Map({
      container: surface, style: createStyle(settings), interactive: false,
      center: [-3.82, 40.53], zoom: 8, bearing: settings.bearing, pitch: settings.pitch,
      minZoom: 5, maxZoom: 12, maxPitch: 60, renderWorldCopies: false,
      attributionControl: false, trackResize: false, fadeDuration: 0,
      canvasContextAttributes: { antialias: true, alpha: true, preserveDrawingBuffer: true, powerPreference: 'low-power' },
      pixelRatio: Math.min(window.devicePixelRatio || 1, 1.5),
    });
    map.getCanvas().setAttribute('aria-hidden', 'true');
    map.getCanvas().tabIndex = -1;
    map.on('sourcedata', event => {
      if (event.sourceDataType !== 'content') return;
      if (event.sourceId === IMAGERY_ID) state.imagery = true;
      if (event.sourceId === DEM_ID) state.dem = true;
      notify();checkReady();
    });
    map.on('idle', checkReady);
    map.on('moveend', updateLabels);
    map.on('error', event => {
      // One failed peripheral tile does not certify success or replace terrain.
      state.error = event.error?.message || 'A geographic resource could not load';
    });
    map.getCanvas().addEventListener('webglcontextlost', () => fail(new Error('The geographic cover lost its WebGL context')), { once: true });
    map.on('load', async () => {
      if (destroyed || failed) return;
      state.style = true;
      try {
        const [data] = await boundaryData;
        if (destroyed || failed) return;
        const polygons = polygonParts(data);
        samples = framingSamples(polygons, settings.madridBounds);
        map.addSource('cover-madrid', { type: 'geojson', data, tolerance: 0, attribution: IGN_ATTRIBUTION });
        map.addSource('cover-outside-madrid', { type: 'geojson', data: outsideMask(polygons), tolerance: 0 });
        map.addLayer({ id: 'cover-madrid-toning', type: 'fill', source: 'cover-madrid', paint: { 'fill-color': '#163124', 'fill-opacity': 0.045, 'fill-antialias': true } });
        map.addLayer({ id: 'cover-outside-shadow', type: 'fill', source: 'cover-outside-madrid', paint: { 'fill-color': '#061114', 'fill-opacity': 0.68, 'fill-antialias': true } });
        state.fullBoundaries = await installBoundaries(map);
        if (destroyed || failed) return;
        if (state.fullBoundaries) {
          map.setPaintProperty('boundary-line', 'line-opacity', 0.29);
          map.setPaintProperty('boundary-line', 'line-width', 0.85);
        }
        map.addLayer({ id: 'cover-madrid-contour-shadow', type: 'line', source: 'cover-madrid', paint: { 'line-color': '#071214', 'line-width': 3.6, 'line-opacity': 0.65 } });
        map.addLayer({ id: 'cover-madrid-contour', type: 'line', source: 'cover-madrid', paint: { 'line-color': '#edf1e8', 'line-width': 1.15, 'line-opacity': 0.90 } });
        state.boundary = true;
        createLabels();
        createAttribution();
        requestFrame(true);
      } catch (error) { fail(error); }
    });
    if (typeof ResizeObserver === 'function') {
      observer = new ResizeObserver(resize);
      observer.observe(host);
    } else window.addEventListener('resize', resize, { passive: true });
    document.addEventListener('visibilitychange', documentVisibilityChanged);
    if (media?.addEventListener) media.addEventListener('change', motionChanged);
    else media?.addListener?.(motionChanged);
    timeout = setTimeout(() => fail(new Error('The cover could not verify both orthoimagery and elevation in time')), clamp(Number.isFinite(options.readyTimeoutMs) ? options.readyTimeoutMs : 30000, 5000, 60000));
  } catch (error) { fail(error); }
  return controller;
}
