# Verificación · revisión 3 · 28/10/2026

La portada geográfica aprobada por Marco se conserva. Esta revisión actúa sobre el mapa de exploración, las fichas, el Atlas y los trazados.

## Datos comprobados

- 55 lugares, 66 itinerarios/visitas y 66 fichas de vida. Todas las fichas de vida tienen fotografía; 37 lugares tienen foto asociada. Los restantes indican la imagen pendiente.
- 22 GPX oficiales, con 6.670 coordenadas: 14 incorporados en esta revisión. Los originales nuevos conservan su SHA-256 y sus segmentos; no se completan retornos ni caminos por inferencia.
- 104 registros de crédito. Las 20 imágenes nuevas conservan autor, archivo de origen, licencia y huella; se entregan en WebP para la web. La foto del gallipato identifica su contexto de acuario.
- Corrección de Lycoperdon perlatum, hábitats ampliados en 20 fichas y referencias científicas adicionales. Las referencias generales de una especie no se convierten en avistamientos locales.
- 69.244 taxones nacionales MITECO y 80.510 elementos cartográficos oficiales. Se mantienen sus fragmentos y carga bajo demanda. La clasificación cartográfica cubre Madrid, Castilla y León y Castilla-La Mancha; se explica la cobertura pendiente al filtrar Extremadura.
- Validación de referencias, rutas y licencias; geometrías IGN y malla de terreno; identificadores, compresión y metadatos geográficos. SQLite reconstruida con integridad y claves foráneas correctas.

## Uso comprobado en navegador

- Apertura de fichas y lista del mapa, cierre de lista sin salir del mapa, cámara ajustada al panel real. Repetir el encuadre regional conserva el mismo zoom: no acumula relleno de cámara.
- Ficha móvil ampliable/contraíble a 375 × 812 y disposición horizontal a 844 × 390. La ficha permanece dentro del viewport y no genera desbordamiento horizontal.
- Atlas móvil: 24 tarjetas por página, fotografía y galería sin desbordamiento horizontal a 375 px. Los filtros y el inventario nacional conservan su función.
- Gallipato: imagen cargada, cuatro bloques de lectura y contexto fotográfico. Su botón de referencia encuentra Pleurodeles waltl en MITECO.
- Búsqueda nacional «quercuz» con filtro de plantas: devuelve 22 nombres parecidos e indica expresamente que no hay coincidencia exacta.
- Enlace directo al espacio Sierra Norte de Guadarrama: ficha y geometría oficial cargadas. Se prueba el mismo identificador codificado del informe anterior del usuario.
- Navafría: muestra 8,2 km solo de ida y distingue la ficha actual de 16,4 km. Taravilla: GPX, perfil y condiciones del gestor, incluida la reserva estacional y la discrepancia de tiempo publicada.
- Favorito de ruta conservado tras recarga; favorito de prueba retirado y retirada confirmada tras recarga. Los demás favoritos no se borran.
- Sin errores nuevos de consola en estas comprobaciones.

## Pruebas automatizadas

20 pruebas: dirección del arrastre derecho, conservación de controles nativos y recuperación; enlaces directos; entrega geográfica gzip y respuestas erróneas; cámara/paneles en escritorio, móvil y horizontal; búsqueda exacta y aproximada del inventario con filtro y caché.

```sh
node --test scripts/test-right-drag.mjs scripts/test-entry-route.mjs scripts/test-geographic-delivery.mjs scripts/test-map-layout.mjs scripts/test-album-search.mjs
npm run check
npm run database
```

## Alcance

No es una revisión de campo ni de avisos en tiempo real. Las fichas Daimiel distinguen las medidas de CNIG y MITECO; no se conserva una etiqueta de accesibilidad para el GPX completo sin respaldo. Horcajo conserva su ficha enlazada: el archivo oficial es una ruta planificada rte, no se presenta como track registrado.

La wiki ilustrada es una selección editorial, no una ficha fotográfica de cada taxón nacional. Los modelos 3D de especies y la ampliación exhaustiva por hábitats siguen pendientes. No se declara una auditoría formal WCAG, lector de pantalla, ni pruebas físicas iOS/Android. La batería completa de importación/exportación GPX y borradores no se repite en esta revisión. Los controles respetan el movimiento reducido existente; no se ha alterado la preferencia del sistema.

## Publicación y recuperación

Se publica en el Site existente conservando su acceso privado. La identificación exacta del despliegue está en PUBLICACION.json de la carpeta principal. La copia del código se conserva en el repositorio privado MarcoFragola/dr-nature-wiki; cada entrega se identifica por etiqueta y por su manifiesto de recuperación.


## Revisión 4 · demostración «Del mapa al sendero» · 28/10/2026

La sección explica tres acciones: leer el relieve, consultar el recorrido y preparar la visita. Sus pasos son botones nativos; el scroll cambia suavemente la cámara en escritorio, y en pantallas compactas la selección se hace con los botones sin forzar el scroll. Se conserva la alternativa de movimiento reducido.

Se sustituye exclusivamente el relieve de la demostración por un recorte local IGN WCS con muestreo efectivo de unos 13 m y alturas sin realce. La portada mantiene su DEM, su cámara y sus fuentes. Se retira la frontera administrativa de esta escena para no confundirla con el sendero.

La inspección de la imagen PNOA actual confirmó un empalme fotográfico de color que, en perspectiva, parecía una pared. La escena usa un recorte georreferenciado de la capa oficial PNOA2023 y una cámara que encuadra la ruta dentro de una zona fotográfica consistente. No se inventan montañas ni se retocan píxeles de la ortofoto. Datos, URL y SHA-256 en dist/data/route-lesson/metadata.json; preparación reproducible en scripts/prepare_route_terrain.py.

El GPX de Cotos–Zona del Zabala permanece intacto. Sus puntos de inicio/regreso y destino se señalan sobre la geometría, y los datos de la ficha oficial (4,7 km totales, 1 h 45 min, +279 m) quedan debajo del mapa. El GPX no contiene cotas; el DEM de la escena no se presenta como un perfil de altitud medido del archivo. La ficha actual del parque se contrastó el 28/10/2026.

Comprobaciones: tres nuevas pruebas de geometría, segmentos y cámara con movimiento reducido; validación SHA-256 de GeoTIFF, imagen y 92 teselas locales; alturas finitas y cobertura de toda la ruta. Revisión visual de escritorio y móvil de 375 px, posición de etiquetas y paso al mapa real. Sin revisión de campo ni condiciones en directo.
