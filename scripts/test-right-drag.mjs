import assert from 'node:assert/strict';
import test from 'node:test';
import {installRightDrag, RIGHT_DRAG_MAPLIBRE_VERSION} from '../dist/right-drag.js';
import {SoftwareTerrainMap} from '../dist/terrain-fallback.js';

// Contract fixture mirrors mouse.ts's mode lookup. Browser QA also exercises
// the real pinned MapLibre handler and its final on-screen rotation.
function fixture() {
  const listeners = new Map(), calls = [];
  const manager = {_eventButton: undefined, isValidStartEvent: () => true, isValidMoveEvent: () => true};
  const dragRotate = {movement: 'circular'};
  const rotate = {
    _moveStateManager: manager, _clickTolerance: 3,
    mousemoveWindow(event, last, current, extra = {}) {
      assert.equal(this, rotate);
      calls.push(event);
      if (event.fail) throw new Error('native failure');
      if (event.inactive) return;
      let bearingDelta = (current.x - last.x) * .8;
      if (dragRotate.movement === 'circular' && current.y < 300) bearingDelta = -bearingDelta;
      return {bearingDelta, ...extra};
    },
  };
  const pitch = {mousemoveWindow: () => ({pitchDelta: -9})};
  const pan = {mousemoveWindow: () => ({panDelta: {x: 8, y: -2}})};
  const map = {
    dragRotate: Object.assign(dragRotate, {_mouseRotate: rotate, _mousePitch: pitch}), dragPan: pan,
    on(name, listener) {listeners.set(name, listener);},
    off(name, listener) {if (listeners.get(name) === listener) listeners.delete(name);},
  };
  return {map, rotate, manager, calls, listeners};
}

test('right drag has the same direction above, below and across the centre', () => {
  const f = fixture();installRightDrag(f.map);f.manager._eventButton = 2;
  for (const [y0, y1] of [[40, 40], [280, 280], [320, 320], [560, 560], [280, 320], [320, 280]]) {
    for (const dx of [-80, 80, -1, 1]) {
      const result = f.rotate.mousemoveWindow({buttons: 2}, {x: 400, y: y0}, {x: 400 + dx, y: y1});
      assert.equal(result.bearingDelta, dx * .8);
      assert.equal(f.map.dragRotate.movement, 'circular');
    }
  }
  assert.equal(RIGHT_DRAG_MAPLIBRE_VERSION, '6.15.0');
});

test('pitch, zoom, pivot, sensitivity and inertia flags remain native', () => {
  const f = fixture(), pitch = f.map.dragRotate._mousePitch.mousemoveWindow, pan = f.map.dragPan.mousemoveWindow;
  installRightDrag(f.map);f.manager._eventButton = 2;
  const extra = Object.freeze({pitchDelta: -9, zoomDelta: .5, around: {x: 320, y: 240}, noInertia: false});
  const result = f.rotate.mousemoveWindow({buttons: 2}, {x: 300, y: 150}, {x: 320, y: 120}, extra);
  assert.deepEqual(result, {bearingDelta: 16, ...extra});
  assert.equal(result.around, extra.around);
  assert.equal(f.map.dragRotate._mousePitch.mousemoveWindow, pitch);
  assert.equal(f.map.dragPan.mousemoveWindow, pan);
  assert.equal(f.rotate._clickTolerance, 3);
});

test('Ctrl+left keeps circular movement; vertical-only right drag never rotates', () => {
  const f = fixture();installRightDrag(f.map);f.manager._eventButton = 0;
  for (const y of [100, 500]) {
    assert.equal(f.rotate.mousemoveWindow({buttons: 1, ctrlKey: true}, {x: 400, y}, {x: 420, y}).bearingDelta, y < 300 ? -16 : 16);
  }
  f.manager._eventButton = 2;
  for (const [y0, y1] of [[100, 500], [500, 100]]) {
    assert.equal(f.rotate.mousemoveWindow({buttons: 2}, {x: 400, y: y0}, {x: 400, y: y1}).bearingDelta, 0);
  }
  assert.equal(f.rotate.mousemoveWindow({inactive: true}, {}, {}), undefined);
});

test('native events and timing persist, and mode restores even on failure', () => {
  const f = fixture();installRightDrag(f.map);f.manager._eventButton = 2;
  const event = {buttons: 2, timeStamp: 123};
  f.rotate.mousemoveWindow(event, {x: 0, y: 0}, {x: 10, y: 0});
  assert.equal(f.calls[0], event);
  assert.throws(() => f.rotate.mousemoveWindow({fail: true}, {}, {}), /native failure/);
  assert.equal(f.map.dragRotate.movement, 'circular');
  f.map.dragRotate.movement = 'linear';
  f.rotate.mousemoveWindow(event, {x: 0, y: 0}, {x: 10, y: 0});
  assert.equal(f.map.dragRotate.movement, 'linear');
});

test('installation is per map, idempotent and recoverable', () => {
  const a = fixture(), b = fixture(), originalA = a.rotate.mousemoveWindow, originalB = b.rotate.mousemoveWindow;
  const installed = installRightDrag(a.map);
  assert.equal(installed.installed, true);
  assert.equal(installRightDrag(a.map), installed);
  assert.equal(b.rotate.mousemoveWindow, originalB);
  installed.uninstall();
  assert.equal(installed.installed, false);
  assert.equal(a.rotate.mousemoveWindow, originalA);
  assert.equal(a.listeners.size, 0);
  assert.equal(installRightDrag(a.map).installed, true);
  a.listeners.get('remove')();
  assert.equal(a.rotate.mousemoveWindow, originalA);
});

test('cleanup preserves later adapters; unsupported engines are explicit', () => {
  const f = fixture(), installed = installRightDrag(f.map), later = () => ({bearingDelta: 7});
  f.rotate.mousemoveWindow = later;installed.uninstall();
  assert.equal(f.rotate.mousemoveWindow, later);
  assert.equal(installRightDrag({isSoftware: true}).reason, 'software-renderer-uses-pointer-deltas');
  assert.equal(installRightDrag({}).installed, false);
  assert.equal(installRightDrag(null).installed, false);
});

test('software renderer has the same on-screen direction and preserves pitch', () => {
  for (const y of [40, 560]) for (const dx of [-80, 80]) {
    const events = new Map();
    const map = {canvas: {addEventListener: (name, fn) => events.set(name, fn), focus() {}, setPointerCapture() {}},
      center: [0, 0], bearing: 0, pitch: 45, emit() {}, render() {}};
    SoftwareTerrainMap.prototype.attachInput.call(map);
    events.get('pointerdown')({pointerId: 1, clientX: 400, clientY: y, button: 2});
    events.get('pointermove')({clientX: 400 + dx, clientY: y - 10});
    assert.equal(map.bearing, dx * .25);
    assert.equal(map.pitch, 46.4);
    const projected = SoftwareTerrainMap.prototype.projectXYZ.call({...map, h: 600, w: 800,
      padding: {top: 0, bottom: 0, left: 0, right: 0}, worldScale: () => 1}, 0, 100, 0);
    assert.equal(Math.sign(projected.x - 400), -Math.sign(dx));
  }
});
