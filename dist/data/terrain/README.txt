IGN regional terrain crop for the cover

Fetch metadata.json and madrid-1024.f32. The binary has exactly 1024*1024 Float32 little-endian samples, row-major, north to south. Heights are metres with no visual exaggeration applied.

Use the pixel-centre and sample-index formulae in metadata.json. Return null outside bbox. Bilinear interpolation for display can use the four surrounding valid samples; it must not extend coverage outside the rectangle.

The original WCS GeoTIFF is retained as madrid-mdt05-regional.tif. Its sample values are signed Int16; Float32 conversion preserves them exactly. Effective spacing is about 177 by 196 metres, despite MDT05 source naming. Do not advertise a delivered 5 m terrain mesh.

Visible attribution: Relieve: IGN / SCNE · MDT05 remuestreado · CC BY 4.0 scne.es.

MapLibre source: type raster-dem, tiles [data/terrain/tiles/{z}/{x}/{y}.png], tileSize256, encoding terrarium, minzoom6, maxzoom10, bounds equal to metadata bbox. Tiles are XYZ/Web Mercator. Partial tiles have opaque alpha255 and edge-extruded RGB solely as technical padding; outside values are NOT geographic coverage. Transparency is avoided because canvas premultiplication can erase hidden RGB and produce -32768 m cliffs. Nodata outside the exact bbox is defined by bounds and metadata. Camera and source bounds must respect the crop; samples outside must return null.
