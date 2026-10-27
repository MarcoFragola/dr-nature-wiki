# Datos geográficos oficiales

Las peticiones exactas, CRS, muestreo, fuentes, licencias, hashes y límites se conservan en:

- dist/data/terrain/metadata.json
- dist/data/boundaries/metadata.json

El recorte WCS usa Elevacion4258_5; la salida regional 1024² se aproxima a 178×196 m. Los valores se convierten a Terrarium mediante interpolación bilineal y codificación de alturas. El edge-padding exterior evita acantilados técnicos; no amplía el bbox válido.

Los límites WFS son polígonos oficiales de segundo y tercer orden. Los anillos se convierten en líneas drapeadas sobre el terreno sin inventar un contorno. La metadata del IGN indica escala general 1:25.000 y precisión heterogénea; no se anuncia exactitud absoluta.

## Preparar de nuevo

Los scripts prepare_ign_terrain.py y prepare_ign_boundaries.py guardan sus temporales en tmp/. Necesitan acceso de red; el primero requiere NumPy y Pillow para la preparación.

Terreno: ejecutar los modos download,package y tiles, en ese orden. Los modos capabilities y describe permiten inspeccionar el servicio antes de cambiar una petición. Fronteras: conservar el flujo inspect,download,metadata,package y provinces según el script y revisar los metadatos antes de reemplazar una fuente.

La preparación no forma parte de la carga de la web. Los visitantes reciben las teselas locales por nivel de detalle. La escena explorable mantiene su fuente global de elevaciones y la portada utiliza el recorte oficial.

Atribución: IGN/CNIG · BDLJE · CC BY 4.0 ign.es; IGN/SCNE · MDT05 remuestreado · CC BY 4.0 scne.es. Las ortofotos mantienen la atribución PNOA/IGN.
