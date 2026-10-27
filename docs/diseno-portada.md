# Recorrido y portada geográfica · edición 2

La referencia de Marco fija la dirección visual: vista oblicua, territorio en el centro-derecha, periferia oscura, controles finos y naturaleza como protagonista. La implementación vigente utiliza geografía real.

## Secuencia

- Nombre Dr Nature wiki sobre una malla WebGL obtenida del MDT oficial. La cámara y el título responden al scroll.
- Llegada a la portada, entrada progresiva del HUD y acceso al mapa explorable.
- Presentación del atlas, demostración sobre el GPX oficial Cotos–Zabala, paneles de biodiversidad y acceso final al mapa.
- Scroll nativo, dos escenas sticky, carga de modelos al acercarse al viewport y alternativa para movimiento reducido.

## Portada

cinematic-cover.js dibuja una escena independiente del mapa de exploración: MDT IGN, ortofoto PNOA y polígonos oficiales alineados por coordenadas. Aplica realce ×4,8, sombreado de relieve, máscara de contexto y contorno oficial de Madrid. Las cotas del dataset no se alteran.

El origen es Elevacion4258_5 del WCS IGN. Se pidió un recorte 1024² sobre [-4.9,39.65,-2.75,41.45], entregado en EPSG:4326. El muestreo regional efectivo ronda 178 ×196 m; no representa una entrega visual de 5 m. La pirámide Terrarium contiene 80 teselas z6–10. El relleno técnico fuera del bbox no amplía la cobertura válida.

Los límites autonómicos y provinciales proceden del WFS oficial IGN. Los vértices se conservan y las fuentes GeoJSON usan tolerancia 0 al renderizar. La precisión heterogénea declarada por IGN se mantiene en los metadatos; la fuente no se describe como exactitud absoluta.

El póster guadarrama-official-poster.jpg es un fotograma del propio modelo oficial renderizado. No contiene montañas generadas. Se utiliza durante la carga y como alternativa estática. La referencia visual original se conserva en referencias/portada-original.png.

Fuentes, solicitudes, licencias y límites: dist/data/terrain/metadata.json y dist/data/boundaries/metadata.json. La fuente del mapa de exploración permanece PNOA/IGN y Terrain Tiles/Mapzen; su realce inicial es ×1,5.

## Componentes

- terrain-intro.js: malla WebGL real para el nombre.
- cinematic-cover.js: portada cartográfica con dirección artística.
- journey.js y journey.css: scroll, cámaras, capítulos e idiomas.
- boundaries.js: anillos oficiales sobre el terreno.
- app.js: wiki, mapas, filtros, rutas y cuaderno.
- cover.js: encuadre del póster de alternativa.

No se ofrecen modelos 3D de especies sin ejemplar, taxón, autor y licencia comprobados. La biodiversidad se presenta mediante fotografías y paneles documentados.
