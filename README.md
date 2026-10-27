# Dr Nature wiki

Atlas visual de naturaleza de Madrid, Castilla y León y Castilla-La Mancha.
Sitio: https://dr-nature-wiki.cannes2.chatgpt.site

## Ejecutar y comprobar

```sh
npm start
npm run check
npm run database
```

Abre http://127.0.0.1:8080/. En Windows también puedes usar ../abrir-web.cmd. No requiere instalar paquetes ni claves de API para navegar. Python3 permite validar los datos y exportar la SQLite; el lanzador reconoce el runtime de la aplicación de escritorio o una instalación normal de Python.

## Experiencia

La apertura presenta el nombre con una malla WebGL de elevaciones reales. Al deslizar se llega a la portada geográfica: MDT oficial IGN, ortofoto PNOA, contorno oficial de Madrid y límites de las comunidades y provincias próximas. El movimiento responde al scroll, con alternativa de movimiento reducido.

Explorar el mapa abre la herramienta a pantalla completa. Permite desplazar, girar, inclinar, acercarse, buscar lugares/rutas/especies, filtrar y abrir fichas. Portada devuelve al recorrido. Las secciones inferiores explican el atlas, muestran un GPX sobre relieve real y enlazan los paneles de biodiversidad.

## Catálogo

55 lugares naturales y centros de interpretación, 57 itinerarios y visitas, y 66 fichas de vida. Hay 8 trazados oficiales con 3.274 coordenadas. Las demás rutas conservan ficha y fuente sin geometría inventada. Se han añadido 40 fotografías respecto a la entrega original; hay 84 registros de crédito,37 lugares y46 especies con foto asociada. La fotografía de los lobos es una contribución de Marco, desde su original de mayor calidad.

Las fichas conectan rutas, agua, hábitats, especies y preparación de la visita. Las presencias regionales no se presentan como avistamientos. No se incorporan modelos 3D de especies sin taxón, autor y licencia verificados; se utilizan paneles fotográficos documentados.

## Geografía y acabado visual

El origen de la portada es Elevacion4258_5 del WCS IGN, solicitado en EPSG:4326. El recorte regional 1024² tiene un muestreo efectivo aproximado 178×196 m. No se anuncia una malla renderizada de 5 m. La presentación utiliza realce vertical ×4,8 y las alturas originales permanecen en los datos.

Los polígonos oficiales proceden del WFS IGN: Madrid,Castilla y León,Castilla-La Mancha y las provincias Madrid,Segovia,Ávila,Guadalajara,Cuenca y Toledo. No se dibujaron desde una imagen. Los vértices se conservan y la incertidumbre de la fuente figura en los metadatos.

El mapa de exploración conserva PNOA/IGN y Terrain Tiles/Mapzen, con realce inicial ×1,5. La portada utiliza el DEM local oficial. El póster de carga es un fotograma del propio modelo oficial, con los mismos datos y cámara.

## Archivos

- dist/index.html: capítulos, interfaz y paneles.
- dist/app.js: wiki, búsqueda, filtros, fichas, mapa y cuaderno.
- dist/journey.js y journey.css: recorrido y cámaras por scroll.
- dist/terrain-intro.js: malla WebGL del nombre.
- dist/cinematic-cover.js: portada 3D geográfica.
- dist/cover.js: encuadre del póster alternativo.
- dist/boundaries.js: límites oficiales sobre el terreno.
- dist/terrain-fallback.js: relieve compatible del mapa explorable.
- dist/data/catalogue.json: contenido editorial y fuentes.
- dist/data/boundaries/: geometrías oficiales y metadatos.
- dist/data/terrain/: fuente MDT, grid, teselas y metadatos.
- dist/data/tracks/: GPX oficiales y conversiones GeoJSON.
- dist/data/asset-map.json y attribution.json: medios y derechos.
- data/catalogue.sqlite: exportación relacional; la web usa JSON.
- scripts/: servidor, validación, exportación y preparación IGN.
- docs/: visión, geografía, diseño y verificación.

## Derechos y alcance

Código MIT. Las fotografías, cartografía y GPX conservan sus propias licencias. El IGN/SCNE se acredita en la escena y en los metadatos. Los GPX del Parque Nacional mantienen las condiciones de su fuente. Consulta docs/creditos-fotografias.md, los registros y las licencias antes de reutilizar medios.

El cuaderno permanece en el navegador y puede exportarse. No hay cuentas ni sincronización entre dispositivos. La cartografía necesita Internet y disponibilidad del proveedor. Las fichas del territorio son una selección documentada. El Atlas natural incluye además una referencia nacional MITECO de 69.244 taxones de distintos rangos; su inclusión no acredita presencia en Madrid. No hay observaciones en directo, meteorología automática, navegación giro a giro ni enrutamiento sobre una red de senderos.

## Revisión en curso · 27/10/2026

El álbum solicitado es el **Atlas natural**, una única sección accesible desde la navegación. Conserva las fichas de campo y añade la Lista Patrón MITECO/IEPNB de España: 69.244 taxones, 14 grupos, 2.885 nombres comunes facilitados por la fuente y 79 fragmentos cargados bajo demanda. Véase dist/data/biodiversity/metadata.json.

La revisión incluye agrupaciones por proximidad y zoom en el mapa, ciudades y pueblos con rótulos distintos, fichas compactas, guía sobre MDT oficial y un único tema. Se comprueban antes de cerrar, junto con accesos, filtros y vista móvil. Se retiran las ramas inactivas del atlas y el selector de día/noche.

**Pendiente para la siguiente revisión visual:** portada. La referencia seleccionada permanece en docs/referencias/portada-seleccionada.png. La sustitución del Site existente se prepara sobre la revisión validada, sin cambiar su audiencia.

El panel de flora destaca la fotografía aportada por Marco de los cerezos del Valle del Jerte. El destino invitado de Extremadura enlaza una ficha del valle y el sendero oficial SL-CC32; no se atribuye a la foto un mirador ni un punto de toma concreto.

## Dirección de arquitectura · prompt ampliado

El catálogo y la representación en pantalla son independientes. Las agrupaciones no retiran registros de búsquedas, fichas o relaciones. El mapa es continuo; sus capas naturales usarán líneas y superficies cuando la fuente las publique.

Capacidades incluidas en esta revisión:

- Navegación entre mapa, listado y galería conservando búsqueda y filtros.
- Búsqueda global y por zona visible, con indicador de restricción geográfica y tolerancia a errores.
- Líneas de agua y superficies naturales desde fuentes vectoriales oficiales, fragmentadas para carga progresiva.
- Guardados de especies y colecciones personales, además de lugares y recorridos.
- Relaciones especie-lugar con clase de evidencia y procedencia explícitas.
- Arrastre derecho con sentido constante en toda la pantalla, comprobado; vertical, sensibilidad, inercia, zoom y selección conservados.
- Interfaz ES/EN, comprobaciones de acceso, móvil e integridad de datos; las coberturas pendientes se conservan explícitas.

El prompt general menciona conservar ambos temas; prevalece la petición específica de Marco de retirar el selector día/noche. La portada continúa pendiente de su revisión visual, sin rediseñarla durante estas mejoras.

### Control del botón derecho comprobado

El arrastre a la izquierda gira el paisaje en sentido horario; a la derecha, en sentido antihorario. Se utiliza el cálculo lineal nativo de MapLibre 6.15.0 exclusivamente durante el gesto derecho, evitando que el sentido cambie al pasar por encima o debajo del centro. El arrastre vertical conserva la inclinación y Ctrl + izquierdo conserva su comportamiento circular. El renderizador compatible usa el mismo sentido en pantalla.

Validación: `node --test scripts/test-right-drag.mjs` (7 pruebas). La página local temporal de `scripts/right-drag-native.html`, copiada a dist únicamente para la comprobación, verifica 13 casos mediante eventos del motor real: cuatro alturas, ambas direcciones, arrastre vertical, cruce del centro y Ctrl + izquierdo. No se publica la página de pruebas.

## Cartografía natural y publicación

El inventario cartográfico incluye 80.510 registros oficiales: tramos de cursos de agua, embalses, agua estancada, humedales y espacios protegidos. La hidrografía corresponde al recorte [-5.2, 39.5, -2.5, 41.6]; los ENP proceden de Madrid, Castilla y León y Castilla-La Mancha. No se presenta como un inventario de toda España. Las pertenencias regionales se calculan por intersección real con los límites IGN. Los bosques y Natura 2000 aún no tienen una capa poligonal completa importada.

Los enlaces directos `#place/…`, `#route/…` y `#natural/…` abren su ficha al entrar o recargar. Los identificadores oficiales con dos puntos se decodifican sin truncarlos. Comprobación: `node --test scripts/test-entry-route.mjs`. La revisión se prepara para sustituir el Site existente con la misma audiencia privada.

Las 338 piezas de geometría se distribuyen como `.geojson.gz` sin pérdida. El navegador descomprime únicamente las solicitadas; cada pieza conserva el SHA-256 del JSON original y la validación vuelve a comprobar todas las coordenadas y registros. Preparación: `python scripts/compress_geography.py`. La descarga de una ficha sigue generando GeoJSON normal.
