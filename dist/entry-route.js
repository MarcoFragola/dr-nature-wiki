// Entry identifiers can contain colons and accented text; decode only the ID.
// Scroll chapter anchors are deliberately outside this router.
export function parseEntryRoute(hash) {
  const match = /^#(place|route|natural)\/(.+)$/.exec(hash || '');
  if (!match) return null;
  try {
    const id = decodeURIComponent(match[2]);
    if (!id || /[\u0000-\u001f\u007f]/.test(id)) return null;
    return {type: match[1], id, key: `${match[1]}:${id}`};
  } catch {
    return null;
  }
}
