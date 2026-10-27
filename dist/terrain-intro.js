/**
 * On-demand WebGL scene from official IGN WCS terrain, resampled for this site.
 * Terrain: Elevacion4258_5, delivered regional grid ~178 x196 m. CC BY4.0 scne.es.
 * Full source, CRS, sampling and limits: data/terrain/metadata.json.
 * Local Terrarium tile10/500/384. Visual vertical emphasis x4.8 only.
 * Surface colours are art direction, not a land-cover classification.
 */

const GRID = 96;
const WORLD_SIZE = 6;
const EXAGGERATION = 4.8;
const EARTH_CIRCUMFERENCE = 40075016.68557849;
const CENTER_LATITUDE = 40.835;
const TILE = Object.freeze({ zoom: 10, x: 500, y: 384 });
const DEM_URL = `data/terrain/tiles/${TILE.zoom}/${TILE.x}/${TILE.y}.png`;

export const TERRAIN_INTRO_EVIDENCE = Object.freeze({
  source: 'IGN / SCNE official WCS terrain, regional resampling',
  sourceUrl: 'https://servicios.idee.es/wcs-inspire/mdt',
  attributionUrl: 'data/terrain/metadata.json',
  attribution: 'IGN / SCNE · MDT05 remuestreado · CC BY4.0 scne.es',
  licence: 'CC BY4.0 scne.es',
  tile: TILE,
  demUrl: DEM_URL,
  sourceVerifiedAt: '2026-10-27',
  requestedCenter: Object.freeze([-3.98, CENTER_LATITUDE]),
  encoding: 'Terrarium RGB, metres',
  meshSamples: Object.freeze([GRID, GRID]),
  verticalExaggeration: EXAGGERATION,
  presentation: 'Art-directed DEM scene; forest and granite colours are illustrative.',
  precisionClaim: null,
});

const VERTEX_SHADER = `
  precision highp float;
  attribute vec3 aPosition;
  attribute vec3 aNormal;
  attribute vec2 aUv;
  attribute float aElevation;
  attribute float aShelter;
  uniform mat4 uViewProjection;
  uniform vec3 uEye;
  varying vec3 vNormal;
  varying vec2 vUv;
  varying float vElevation;
  varying float vShelter;
  varying float vDistance;
  void main() {
    vNormal = aNormal;
    vUv = aUv;
    vElevation = aElevation;
    vShelter = aShelter;
    vDistance = distance(uEye, aPosition);
    gl_Position = uViewProjection * vec4(aPosition, 1.0);
  }
`;

const FRAGMENT_SHADER = `
  precision mediump float;
  varying vec3 vNormal;
  varying vec2 vUv;
  varying float vElevation;
  varying float vShelter;
  varying float vDistance;
  void main() {
    vec3 normal = normalize(vNormal);
    vec3 light = normalize(vec3(-0.65, 0.85, -0.35));
    float diffuse = max(dot(normal, light), 0.0);
    float steepness = 1.0 - max(normal.y, 0.0);
    float highland = smoothstep(0.48, 0.94, vElevation);
    float granite = clamp(highland * 0.65 + smoothstep(0.32, 0.75, steepness) * 0.45, 0.0, 0.85);
    vec3 forest = vec3(0.035, 0.089, 0.073);
    vec3 stone = vec3(0.28, 0.30, 0.265);
    vec3 surface = mix(forest, stone, granite);
    surface *= (0.34 + 1.13 * diffuse) * mix(1.0, 0.72, vShelter);
    surface += vec3(0.021, 0.036, 0.033) * pow(1.0 - diffuse, 2.0);
    float fog = smoothstep(5.0, 11.5, vDistance);
    vec3 fogColour = vec3(0.02745, 0.07059, 0.07843);
    surface = mix(surface, fogColour, fog * 0.84);
    float edgeDistance = min(min(vUv.x, 1.0 - vUv.x), min(vUv.y, 1.0 - vUv.y));
    float edge = smoothstep(0.0, 0.17, edgeDistance);
    float alpha = edge * (1.0 - fog * 0.68) * 0.96;
    gl_FragColor = vec4(surface * alpha, alpha);
  }
`;

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
const lerp = (from, to, amount) => from + (to - from) * amount;
const smooth = value => value * value * (3 - 2 * value);
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
function normalize(vector) {
  const length = Math.hypot(...vector) || 1;
  return vector.map(value => value / length);
}

// Column-major matrices, matching WebGL's uniformMatrix4fv convention.
function perspective(fieldOfView, aspect, near, far) {
  const focal = 1 / Math.tan(fieldOfView / 2);
  const depth = 1 / (near - far);
  return new Float32Array([
    focal / aspect, 0, 0, 0,
    0, focal, 0, 0,
    0, 0, (far + near) * depth, -1,
    0, 0, 2 * far * near * depth, 0,
  ]);
}

function lookAt(eye, target) {
  const z = normalize(eye.map((value, axis) => value - target[axis]));
  const x = normalize(cross([0, 1, 0], z));
  const y = cross(z, x);
  return new Float32Array([
    x[0], y[0], z[0], 0,
    x[1], y[1], z[1], 0,
    x[2], y[2], z[2], 0,
    -dot(x, eye), -dot(y, eye), -dot(z, eye), 1,
  ]);
}

function multiply(a, b) {
  const result = new Float32Array(16);
  for (let column = 0; column < 4; column++) {
    for (let row = 0; row < 4; row++) {
      let value = 0;
      for (let index = 0; index < 4; index++) value += a[index * 4 + row] * b[column * 4 + index];
      result[column * 4 + row] = value;
    }
  }
  return result;
}

function createShader(gl, type, source) {
  const shader = gl.createShader(type);
  if (!shader) throw new Error('WebGL shader allocation failed');
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const message = gl.getShaderInfoLog(shader) || 'Shader compilation failed';
    gl.deleteShader(shader);
    throw new Error(message);
  }
  return shader;
}

function createProgram(gl) {
  const shaders = [];
  let program;
  try {
    shaders.push(createShader(gl, gl.VERTEX_SHADER, VERTEX_SHADER));
    shaders.push(createShader(gl, gl.FRAGMENT_SHADER, FRAGMENT_SHADER));
    program = gl.createProgram();
    if (!program) throw new Error('WebGL program allocation failed');
    shaders.forEach(shader => gl.attachShader(program, shader));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program) || 'Shader linking failed');
    return program;
  } catch (error) {
    if (program) gl.deleteProgram(program);
    throw error;
  } finally {
    shaders.forEach(shader => gl.deleteShader(shader));
  }
}

function meshFromImage(image) {
  const raster = document.createElement('canvas');
  raster.width = image.naturalWidth;
  raster.height = image.naturalHeight;
  const context = raster.getContext('2d', { willReadFrequently: true });
  if (!context || raster.width < 2 || raster.height < 2) throw new Error('Elevation raster cannot be read');
  context.drawImage(image, 0, 0);
  const { data } = context.getImageData(0, 0, raster.width, raster.height);
  const { width, height } = raster;
  const elevations = new Float32Array(width * height);
  for (let index = 0; index < elevations.length; index++) {
    const offset = index * 4;
    if (data[offset + 3] !== 255) throw new Error('Elevation tile contains missing samples');
    const metres = data[offset] * 256 + data[offset + 1] + data[offset + 2] / 256 - 32768;
    if (!Number.isFinite(metres) || metres < -500 || metres > 6000) throw new Error('Elevation tile is outside the expected regional range');
    elevations[index] = metres;
  }
  const sample = (u, v) => {
    const x = clamp(u, 0, 1) * (width - 1);
    const z = clamp(v, 0, 1) * (height - 1);
    const x0 = Math.floor(x), z0 = Math.floor(z);
    const x1 = Math.min(x0 + 1, width - 1), z1 = Math.min(z0 + 1, height - 1);
    return lerp(lerp(elevations[z0 * width + x0], elevations[z0 * width + x1], x - x0),
      lerp(elevations[z1 * width + x0], elevations[z1 * width + x1], x - x0), z - z0);
  };

  const heights = new Float32Array(GRID * GRID);
  let minimum = Infinity, maximum = -Infinity;
  for (let z = 0; z < GRID; z++) {
    for (let x = 0; x < GRID; x++) {
      const metres = sample(x / (GRID - 1), z / (GRID - 1));
      heights[z * GRID + x] = metres;
      minimum = Math.min(minimum, metres);
      maximum = Math.max(maximum, metres);
    }
  }
  if (maximum - minimum < 5) throw new Error('Elevation tile has insufficient valid relief');

  const tileMetres = EARTH_CIRCUMFERENCE * Math.cos(CENTER_LATITUDE * Math.PI / 180) / (2 ** TILE.zoom);
  const verticalScale = WORLD_SIZE * EXAGGERATION / tileMetres;
  const step = WORLD_SIZE / (GRID - 1);
  const positions = new Float32Array(GRID * GRID * 3);
  const normals = new Float32Array(GRID * GRID * 3);
  const uv = new Float32Array(GRID * GRID * 2);
  const normalizedElevation = new Float32Array(GRID * GRID);
  const shelter = new Float32Array(GRID * GRID);
  const heightAt = (x, z) => heights[clamp(z, 0, GRID - 1) * GRID + clamp(x, 0, GRID - 1)];
  for (let z = 0; z < GRID; z++) {
    for (let x = 0; x < GRID; x++) {
      const index = z * GRID + x;
      const u = x / (GRID - 1), v = z / (GRID - 1);
      positions.set([(u - 0.5) * WORLD_SIZE, (heights[index] - minimum) * verticalScale, (v - 0.5) * WORLD_SIZE], index * 3);
      const dx = (heightAt(x + 1, z) - heightAt(x - 1, z)) * verticalScale;
      const dz = (heightAt(x, z + 1) - heightAt(x, z - 1)) * verticalScale;
      normals.set(normalize([-dx, 2 * step, -dz]), index * 3);
      uv.set([u, v], index * 2);
      normalizedElevation[index] = (heights[index] - minimum) / (maximum - minimum);
      // Local valley darkening uses measured neighbours, not procedural relief.
      let enclosure = 0;
      for (const [ox, oz] of [[3, 0], [-3, 0], [0, 3], [0, -3]]) {
        enclosure += Math.max(0, (heightAt(x + ox, z + oz) - heights[index]) * verticalScale / (3 * step));
      }
      shelter[index] = clamp(enclosure * 0.35, 0, 1);
    }
  }
  const indices = new Uint16Array((GRID - 1) * (GRID - 1) * 6);
  let offset = 0;
  for (let z = 0; z < GRID - 1; z++) {
    for (let x = 0; x < GRID - 1; x++) {
      const a = z * GRID + x, b = a + 1, c = a + GRID, d = c + 1;
      indices.set([a, c, b, b, c, d], offset);
      offset += 6;
    }
  }
  raster.width = raster.height = 0;
  return { positions, normals, uv, normalizedElevation, shelter, indices, minimum, maximum };
}

/**
 * Named ES-module export. Supply a canvas sized with CSS by its owner.
 * Call setProgress(0..1) from the existing scroll observer. No internal loop.
 * `ready` resolves to a boolean; `status` exposes loading/ready/unavailable/lost.
 */
export class TerrainIntro {
  constructor(canvas) {
    if (!canvas || typeof canvas.getContext !== 'function') throw new TypeError('TerrainIntro requires a canvas');
    this.canvas = canvas;
    this.evidence = TERRAIN_INTRO_EVIDENCE;
    this.progress = 0;
    this.visible = true;
    this.status = 'loading';
    this.error = null;
    this._destroyed = false;
    this._contextLost = false;
    this._frame = null;
    this._mesh = null;
    this._buffers = [];
    this._program = null;
    this._media = window.matchMedia?.('(prefers-reduced-motion: reduce)');
    this._reduced = this._media?.matches ?? false;
    this._motionChanged = event => { this._reduced = event.matches; this._invalidate(); };
    this._visibilityChanged = () => { if (document.hidden) this._cancelFrame(); else this._invalidate(); };
    this._resize = () => this.resize();
    this._lost = event => {
      event.preventDefault();
      this._contextLost = true;
      this.status = 'lost';
      this._cancelFrame();
    };
    this._restored = () => {
      if (this._destroyed) return;
      this._contextLost = false;
      this._program = null;
      this._buffers = [];
      try {
        this._prepareProgram();
        if (this._mesh) this._uploadMesh();
        this.status = this._mesh ? 'ready' : 'loading';
        this.error = null;
        this._invalidate();
      } catch (error) { this._fail(error); }
    };
    canvas.addEventListener('webglcontextlost', this._lost);
    canvas.addEventListener('webglcontextrestored', this._restored);
    document.addEventListener('visibilitychange', this._visibilityChanged);
    if (this._media?.addEventListener) this._media.addEventListener('change', this._motionChanged);
    else this._media?.addListener?.(this._motionChanged);

    try {
      this.gl = canvas.getContext('webgl', { alpha: true, premultipliedAlpha: true, antialias: true, depth: true, powerPreference: 'low-power' });
      if (!this.gl) throw new Error('WebGL is unavailable');
      this._prepareProgram();
      this.resize();
      if (typeof ResizeObserver === 'function') {
        this._observer = new ResizeObserver(this._resize);
        this._observer.observe(canvas);
      } else window.addEventListener('resize', this._resize, { passive: true });
      this.ready = this._loadElevation();
    } catch (error) {
      this._fail(error);
      this.ready = Promise.resolve(false);
    }
  }

  setProgress(progress) {
    if (this._destroyed || !Number.isFinite(progress)) return;
    const next = clamp(progress, 0, 1);
    if (Math.abs(next - this.progress) < 0.0001) return;
    this.progress = next;
    if (!this._reduced) this._invalidate();
  }

  setVisible(visible) {
    if (this._destroyed) return;
    const next = Boolean(visible);
    if (next === this.visible) return;
    this.visible = next;
    if (next) { this.resize(); this._invalidate(); }
    else { this._cancelFrame(); this._clear(); }
  }

  resize() {
    if (this._destroyed || !this.gl || this._contextLost) return;
    const box = this.canvas.getBoundingClientRect();
    const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
    const width = Math.max(1, Math.round(box.width * ratio));
    const height = Math.max(1, Math.round(box.height * ratio));
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.canvas.width = width;
      this.canvas.height = height;
      this._invalidate();
    }
  }

  destroy() {
    if (this._destroyed) return;
    this._destroyed = true;
    this.status = 'destroyed';
    this._cancelFrame();
    this._cancelImage?.();
    this._observer?.disconnect();
    window.removeEventListener('resize', this._resize);
    document.removeEventListener('visibilitychange', this._visibilityChanged);
    this.canvas.removeEventListener('webglcontextlost', this._lost);
    this.canvas.removeEventListener('webglcontextrestored', this._restored);
    if (this._media?.removeEventListener) this._media.removeEventListener('change', this._motionChanged);
    else this._media?.removeListener?.(this._motionChanged);
    this._clear();
    if (this.gl && !this._contextLost) {
      this._buffers.forEach(buffer => this.gl.deleteBuffer(buffer));
      if (this._program) this.gl.deleteProgram(this._program);
    }
    this._buffers = [];
    this._mesh = this._program = this._locations = null;
    this.gl = null;
  }

  _prepareProgram() {
    const gl = this.gl;
    this._program = createProgram(gl);
    this._locations = {
      viewProjection: gl.getUniformLocation(this._program, 'uViewProjection'),
      eye: gl.getUniformLocation(this._program, 'uEye'),
    };
    gl.clearColor(0, 0, 0, 0);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.disable(gl.CULL_FACE);
  }

  _loadElevation() {
    return new Promise(resolve => {
      const image = new Image();
      image.crossOrigin = 'anonymous';
      image.decoding = 'async';
      let settled = false;
      const finish = success => {
        if (settled) return;
        settled = true;
        clearTimeout(timeout);
        image.onload = image.onerror = null;
        this._cancelImage = null;
        resolve(success);
      };
      const timeout = setTimeout(() => {
        if (!this._destroyed) this._fail(new Error('Elevation tile timed out'));
        finish(false);
        image.src = '';
      }, 15000);
      this._cancelImage = () => { finish(false); image.src = ''; };
      image.onload = () => {
        if (this._destroyed) { finish(false); return; }
        try {
          this._mesh = meshFromImage(image);
          this.heightRangeMetres = Object.freeze([this._mesh.minimum, this._mesh.maximum]);
          if (!this._contextLost) {
            this._uploadMesh();
            this.status = 'ready';
            this._invalidate();
          }
          this.canvas.dispatchEvent(new CustomEvent('terrainintro:ready', { detail: { evidence: this.evidence, heightRangeMetres: this.heightRangeMetres } }));
          finish(true);
        } catch (error) { this._fail(error); finish(false); }
      };
      image.onerror = () => {
        if (!this._destroyed) this._fail(new Error('Elevation tile could not load'));
        finish(false);
      };
      image.src = DEM_URL;
    });
  }

  _uploadMesh() {
    const gl = this.gl;
    const attributes = [
      ['aPosition', this._mesh.positions, 3],
      ['aNormal', this._mesh.normals, 3],
      ['aUv', this._mesh.uv, 2],
      ['aElevation', this._mesh.normalizedElevation, 1],
      ['aShelter', this._mesh.shelter, 1],
    ];
    this._buffers.forEach(buffer => gl.deleteBuffer(buffer));
    this._buffers = [];
    this._attributeBindings = attributes.map(([name, values, size]) => {
      const buffer = gl.createBuffer();
      if (!buffer) throw new Error('Terrain buffer allocation failed');
      this._buffers.push(buffer);
      gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
      gl.bufferData(gl.ARRAY_BUFFER, values, gl.STATIC_DRAW);
      return { buffer, size, location: gl.getAttribLocation(this._program, name) };
    });
    this._indexBuffer = gl.createBuffer();
    if (!this._indexBuffer) throw new Error('Terrain index allocation failed');
    this._buffers.push(this._indexBuffer);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this._indexBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, this._mesh.indices, gl.STATIC_DRAW);
  }

  _invalidate() {
    if (this._destroyed || this._contextLost || !this.visible || document.hidden || this._frame !== null) return;
    this._frame = requestAnimationFrame(() => { this._frame = null; this._render(); });
  }

  _cancelFrame() {
    if (this._frame !== null) cancelAnimationFrame(this._frame);
    this._frame = null;
  }

  _clear() {
    if (!this.gl || this._contextLost) return;
    this.gl.clearColor(0, 0, 0, 0);
    this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
  }

  _fail(error) {
    this.error = error instanceof Error ? error.message : String(error);
    this.status = 'unavailable';
    this._cancelFrame();
    this._clear();
    this.canvas.dispatchEvent(new CustomEvent('terrainintro:error', { detail: { message: this.error } }));
  }

  _render() {
    const gl = this.gl;
    if (!gl || this._destroyed || this._contextLost || !this.visible || document.hidden) return;
    gl.viewport(0, 0, this.canvas.width, this.canvas.height);
    this._clear();
    if (!this._mesh || !this._program || this.status !== 'ready') return;

    // A real perspective approach with a restrained eight-degree orbital arc.
    const progress = this._reduced ? 0.30 : smooth(this.progress);
    const azimuth = lerp(-0.20, -0.06, progress);
    const radius = lerp(6.4, 4.55, progress);
    const eye = [Math.sin(azimuth) * radius, lerp(3.0, 2.25, progress), Math.cos(azimuth) * radius];
    const target = [0, lerp(1.0, 0.82, progress), -0.20];
    const projection = perspective(44 * Math.PI / 180, this.canvas.width / this.canvas.height, 0.08, 30);
    const view = lookAt(eye, target);
    gl.useProgram(this._program);
    gl.uniformMatrix4fv(this._locations.viewProjection, false, multiply(projection, view));
    gl.uniform3fv(this._locations.eye, eye);
    for (const binding of this._attributeBindings) {
      if (binding.location < 0) continue;
      gl.bindBuffer(gl.ARRAY_BUFFER, binding.buffer);
      gl.enableVertexAttribArray(binding.location);
      gl.vertexAttribPointer(binding.location, binding.size, gl.FLOAT, false, 0, 0);
    }
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this._indexBuffer);
    gl.drawElements(gl.TRIANGLES, this._mesh.indices.length, gl.UNSIGNED_SHORT, 0);
  }
}
