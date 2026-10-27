REFERENCIA GEOGRAFICA OFICIAL · DR NATURE WIKI

Instantánea: 27 de octubre de 2026.

80.510 registros geográficos:
- 73.713 tramos o cursos de agua (no 73.713 ríos distintos).
- 181 embalses.
- 6.253 masas de agua clasificadas como «Lago» por la fuente IGN; la categoría incluye objetos pequeños y no acredita condiciones actuales.
- 208 humedales.
- 155 espacios naturales protegidos del MITECO.

COBERTURA
La hidrografía incluye todos los registros oficiales que intersectan el rectángulo[-5.2,39.5,-2.5,41.6] en orden oeste,sur,este,norte. Es Madrid y parte de sus entornos de Castilla y León y Castilla-La Mancha; no son las tres comunidades completas. Se conservan sin recortar las geometrías que cruzan el rectángulo.
Los ENP incluyen los códigos de administración30, 41 y 42 del archivo oficial y los parques nacionales interautonómicos Picos de Europa y Sierra de Guadarrama, que la fuente codifica80. Se conservan sus formas completas, incluidas partes fuera de las tres comunidades. No incluye todos los ENP de España ni la Red Natura 2000 como conjunto independiente.

FORMATO
index.json: columnas search=[id,name,type,bbox,chunk,minZoom,regionMask]. chunk es índice numérico en chunks[]. Cada descriptor de fragmento contiene file,bbox,count,bytes. bbox corresponde a la geometría completa, no al marco de la celda.
Los fragmentos detallados son GeoJSON FeatureCollection. Celdas de0.25 grados por centro de bbox; bloques de hasta1.5MB/500elementos. Los datos no se deben descargar todos al abrir la web.
overview_chunks enumera fragmentos de vista amplia(minZoom<=9), separados por familia/celda1grado y hasta1.9 MB cada uno. Consultar por intersección de bbox para cargar solo lo necesario. Los objetos de overview son los mismos IDs que los del catálogo detallado; no se suman como registros nuevos.
metadata.json conserva fuente, licencia, fechas, alcance, reproyección y limitaciones. import-report.json conserva URLs y hashes de las respuestas fuente.

GEOMETRIA Y PRECISION
No se recortan, suavizan ni simplifican topológicamente las formas. Coordenadas XY a seis decimales; los 24 tramos minúsculos que colapsarían conservan nueve. Se omite Z en visualización y se conserva en la fuente original de trabajo; el relieve procede del MDT separado. source_resolution conserva el valor original y no se presenta como precisión posicional de levantamiento. geographic_precision_m es null.
ENP se reproyecta de ETRS89/UTM30N(EPSG:25830) a longitud/latitud WGS84(EPSG:4326) con pyproj3.7.2/PROJ; escala de fuente1:50.000, sin afirmar exactitud métrica de los límites.

REPRODUCCION
python scripts/prepare_enp.py --offline (requiere pyproj3.7.2; solo preparación, no dependencia de la web)
python scripts/prepare_geography.py --offline
python scripts/validate_geographic_reference.py
Para descargar fuentes que falten, omitir --offline. Los originales se guardan en web/tmp/geography, fuera de la publicación.

LIMITES
No se deducen fotografías, avistamientos, accesos, permisos, calidad del agua ni navegabilidad de senderos. Los nombres ausentes siguen siendo null; una etiqueta genérica de interfaz no se debe presentar como nombre oficial. regionMask y regions se derivan de intersecciones geométricas con los límites oficiales del IGN; no de centroides ni de códigos administrativos. Los códigos de administración del ENP siguen siendo un atributo distinto de la fuente.

DERECHOS
Hidrografía: IGN/CNIG · CC BY4.0 scne.es, condiciones enlazadas en metadata.json.
ENP: Origen de los datos: Ministerio para la Transición Ecológica y el Reto Demográfico. Diciembre2025. Reutilización con cita de fuente y fecha conforme al aviso legal MITECO; no se presupone una licencia Creative Commons específica ni patrocinio ministerial.

FILTRO REGIONAL DERIVADO
regionMask es la séptima columna del índice y una propiedad de cada feature: 1 Madrid, 2 Castilla y León, 4 Castilla-La Mancha. Los bits se combinan si el elemento toca o cruza varias regiones; 0 significa que no intersecta ninguna de estas tres, sin asignarlo a otra comunidad. regions enumera los nombres correspondientes.
El cálculo usa la geometría completa y los polígonos oficiales de data/boundaries/comunidades.geojson, sin buffers ni aproximación por centroides. No implica pertenencia exclusiva ni precisión superior a la de las fuentes.
Se reparan copias topológicas solo para el cálculo si GEOS detecta invalidez; geometrías publicadas y archivo de límites permanecen intactos. Detalles, versiones, máscaras, reparaciones y hashes de conservación en regional-intersection-report.json.
Reproducción opcional tras la importación: python scripts/derive_geography_regions.py. Requiere Shapely2.1.2 y NumPy>=1.21 únicamente durante la preparación; no añade dependencias de ejecución a la web.
