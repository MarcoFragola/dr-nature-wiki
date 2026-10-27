/**
 * Position-independent right-button rotation in the pinned MapLibre 6.15.0.
 *
 * Native circular rotation changes sign above/below the map centre. Use the
 * native linear calculation for right-button samples only: cursor left turns
 * the landscape clockwise, cursor right counterclockwise, anywhere on screen.
 * The native handler still owns sensitivity, threshold, pivot and inertia.
 * Ctrl+left retains the configured movement, and vertical pitch is untouched.
 *
 * This deliberately isolated adapter depends on this version's internal shape.
 * Check it when upgrading MapLibre; an unsupported shape returns installed:false.
 * Sources, from the verified official v6.15.0 package:
 * https://github.com/maplibre/maplibre-gl-js/blob/v6.15.0/src/ui/handler/mouse.ts
 * https://github.com/maplibre/maplibre-gl-js/blob/v6.15.0/src/ui/handler/drag_handler.ts
 * https://github.com/maplibre/maplibre-gl-js/blob/v6.15.0/src/ui/handler/drag_move_state_manager.ts
 */
const installations = new WeakMap();
export const RIGHT_DRAG_MAPLIBRE_VERSION = '6.15.0';

export function installRightDrag(map) {
  if (!map || (typeof map !== 'object' && typeof map !== 'function')) {
    return {installed: false, reason: 'missing-map', uninstall() {}};
  }
  const existing = installations.get(map);
  if (existing) return existing;
  if (map.isSoftware) {
    return {installed: false, reason: 'software-renderer-uses-pointer-deltas', uninstall() {}};
  }
  const dragRotate = map.dragRotate;
  const rotate = dragRotate?._mouseRotate;
  const manager = rotate?._moveStateManager;
  if (typeof rotate?.mousemoveWindow !== 'function' ||
      typeof manager?.isValidStartEvent !== 'function' ||
      typeof manager?.isValidMoveEvent !== 'function' ||
      !['circular', 'linear'].includes(dragRotate.movement)) {
    return {installed: false, reason: 'unsupported-maplibre-handler-shape', uninstall() {}};
  }

  const originalMove = rotate.mousemoveWindow;
  function linearRightMove(...args) {
    // Ctrl+left starts the same native handler with button 0 and stays unchanged.
    // Ctrl+right uses the separate roll handler; it never starts mouseRotate.
    if (this._moveStateManager._eventButton !== 2) return originalMove.apply(this, args);
    const configuredMovement = dragRotate.movement;
    dragRotate.movement = 'linear';
    try {
      return originalMove.apply(this, args);
    } finally {
      dragRotate.movement = configuredMovement;
    }
  }
  rotate.mousemoveWindow = linearRightMove;
  let installed = true;
  function uninstall() {
    if (!installed) return;
    installed = false;
    // Preserve another adapter installed later instead of overwriting it.
    if (rotate.mousemoveWindow === linearRightMove) rotate.mousemoveWindow = originalMove;
    map.off?.('remove', uninstall);
    installations.delete(map);
  }
  const installation = {
    get installed() { return installed; },
    reason: null,
    handler: 'dragRotate._mouseRotate.mousemoveWindow',
    uninstall,
  };
  installations.set(map, installation);
  map.on?.('remove', uninstall);
  return installation;
}
