# Visión del producto

Actualizada con las indicaciones directas de Marco del 27/10/2026. El documento define objetivos; el estado implementado se detalla en verificacion.md.

PROMPT MAESTRO · DR NATURE WIKI
Versión: 27 de octubre de 2026
Autor del encargo: Marco. Este documento describe el producto objetivo; no afirma que todas sus fases estén implementadas en la primera edición.

Actúa como un equipo experto en diseño de producto digital, desarrollo web geoespacial, accesibilidad, divulgación de biodiversidad y gestión de datos. Construye y evoluciona Dr Nature wiki: un atlas de naturaleza visual, interactivo, educativo y explorable libremente. Trabaja sobre el código entregado si existe; conserva las decisiones válidas y no reinicies el proyecto sin una razón técnica demostrable.

1. VISIÓN

Quiero una experiencia de exploración del territorio comparable, en intención, a recorrer Google Earth, combinada con una enciclopedia visual de la naturaleza. El mapa debe ser la experiencia principal. El usuario debe poder pasar de una montaña a sus caminos, de un río a su ecosistema, y de una especie a los entornos donde está documentada, sin perder su orientación.

El proyecto empieza en la Comunidad de Madrid y las dos comunidades autónomas con las que limita: Castilla y León y Castilla-La Mancha. No incluyas La Rioja, Aragón o Extremadura como comunidades limítrofes de Madrid. Que la cartografía base permita navegar por España no implica que el catálogo editorial cubra toda España. Señala claramente la cobertura de cada capa.

Prioriza naturaleza: La Pedriza, Peñalara, Cotos, Navacerrada, Fuenfría, Ducha de los Alemanes, Valsaín, Rascafría, cascadas del Purgatorio, Sierra del Rincón, Montejo, Tejera Negra, Gredos, Río Dulce, embalses y bosques de interés. Incluye naturaleza cercana a las poblaciones cuando tenga valor ecológico, como Monte de Boadilla y Casa de Campo. No conviertas la plataforma en un directorio de monumentos, restaurantes o turismo urbano.

2. REFERENCIAS Y CRITERIO VISUAL

Las imágenes del usuario son referencias de composición, luz y atmósfera, no cartografía válida. Corrige los errores geográficos de esas imágenes. Nunca conviertas una imagen generada en un supuesto mapa real ni dibujes cordilleras, fronteras o lagos imaginarios.

Referencia geográfica: https://idem.madrid.org/visor/3D/ . Es un ejemplo de exploración del terreno. Consulta los servicios y metadatos oficiales; no copies su código ni supongas que todo lo visible es un modelo individual de cada elemento. Dr Nature debe transformar el territorio en conocimiento accesible: filtros sencillos, fotografías, fichas conectadas, rutas y preparación de la visita. Evita replicar una interfaz de SIG profesional con listas técnicas interminables.

Dirección visual: verde bosque profundo, blanco cálido, acento verde salvia, fotografías auténticas, superficies translúcidas legibles, tipografía limpia y jerarquía editorial. Modo claro y oscuro completos. Español e inglés completos, incluyendo controles, estados vacíos, avisos y textos alternativos. Los nombres propios oficiales pueden conservar su forma original.

La portada debe reconstruir la primera referencia visual de Marco con un paisaje fotorealista ilustrado, controles HTML/SVG e interacción real de cámara y fichas. Mantener un modo Mapa real operativo y un enlace al visor IDEM como alternativas. La ilustración no se presenta como cartografía ni como un modelo topográfico real. Titular breve, una acción clara y una pequeña selección de lugares. Usa movimiento para orientar: transiciones de cámara, enfoque de marcadores, apertura de fichas y seguimiento de un GPX. No añadas scroll secuestrado, animaciones continuas que gasten batería o decoraciones que oculten el mapa. Respeta prefers-reduced-motion.

3. MOTOR GEOGRÁFICO

Utiliza un motor probado: MapLibre GL JS con raster DEM para un atlas regional o CesiumJS si las necesidades de globo, quantized-mesh y 3D Tiles justifican la migración. Elige con una prueba real de terreno, precisión, rendimiento y despliegue; no con una captura promocional.

El relieve debe proceder de un modelo digital de elevaciones real. Usa cartografía e imágenes georreferenciadas de IGN/CNIG, PNOA, IDEM u otros proveedores documentados con licencia y atribución. Evalúa MDT de 5 m cuando el servicio, formato y alojamiento lo permitan. Declara resolución, fecha, datum y exageración vertical. ×1 equivale a la escala original; cualquier realce es visual y debe identificarse.

Permite desplazar, acercar, girar, inclinar, orientar al norte, recuperar el encuadre inicial y activar capas. Implementa controles de teclado y táctiles. Carga teselas por nivel de detalle y únicamente cuando sean necesarias. Conserva una alternativa compatible si WebGL no está disponible; una alternativa no debe anunciar datos o precisión que no posee.

Las capas objetivo incluyen relieve, ortofoto, senderos, ciclismo autorizado, hidrografía, embalses, lagunas, bosques, vegetación, hábitats y espacios protegidos. No declares que una capa está implementada si solo filtra una lista de lugares. Distingue la imagen aérea de una geometría consultable. Documenta qué capas son ráster, vectoriales o modelos 3D y qué preguntas puede responder cada una.

4. EXPLORACIÓN Y FILTROS

Navegación principal: Explorar, Rutas, Atlas natural y Mi cuaderno. Búsqueda por lugar, ruta, especie y nombre científico. Mantén mapa, resultados y ficha seleccionada sincronizados. Permite enlaces profundos a las fichas.

Filtros combinables: comunidad, área, ecosistema, fauna, flora, hongos/líquenes, agua, actividad, longitud, desnivel, dificultad, tiempo, tipo de trazado y accesibilidad. Los filtros familiares, de perros, bicicletas y movilidad reducida requieren evidencia de la fuente: desconocido, permitido con condiciones y prohibido son estados distintos. No deduzcas accesibilidad de una ruta corta ni seguridad infantil de poco desnivel.

El usuario puede explorar sin cuenta. Los filtros deben mostrar su efecto y tener un restablecimiento claro. Ofrece estados vacíos útiles y explica qué dato falta sin rellenarlo artificialmente.

5. FICHAS DE RUTAS

Cada ficha puede incluir: nombre oficial, ubicación, fotografías, geometría GPX/GeoJSON, fuente del trazado, fecha de revisión, distancia, ascenso/descenso, duración orientativa, dificultad publicada o MIDE cuando exista, circular/lineal/ida y vuelta, puntos de acceso documentados, paisaje y especies del entorno.

Solo dibuja caminos obtenidos de una geometría real autorizada o importada por el usuario. Si falta el GPX, presenta la ficha y su fuente sin inventar una polilínea. Distingue distancia de ida, recorrido completo y valores derivados. Si dos fuentes discrepan, registra ambas y explica cuál se utiliza.

Muestra un perfil de elevación solo cuando existan cotas del GPX o un muestreo de DEM claramente etiquetado y reproducible. No inventes perfiles decorativos. El sobrevuelo debe seguir la geometría y tener un botón visible de detener.

Incluye preparación personalizada: niños, experiencia, perros, bici, accesibilidad, desnivel, exposición, estación, nieve/hielo, calor, tormentas, restricciones y reservas. Nunca presentes «sin alertas» como «seguro». Separa los consejos generales de avisos actuales con fecha, organismo y caducidad. Si no hay integración meteorológica, enlaza AEMET sin simular un dato en directo.

«Cómo llegar» abrirá Google Maps hacia un inicio de ruta documentado o buscará el lugar por nombre. Un punto de interés no es automáticamente un aparcamiento ni un acceso practicable. No prometas transporte público, aparcamiento o acceso rodado sin verificarlo.

6. WIKI DE BIODIVERSIDAD

Cada especie debe tener identidad taxonómica, nombre común ES/EN, fotografía fiable, rasgos orientativos, hábitat, papel ecológico, distribución documentada, fuentes y fecha. Conecta especies, ecosistemas, agua, áreas y rutas mediante relaciones con evidencia.

Distingue inventario regional, presencia documentada en un área, observación concreta y posibilidad de encuentro. Ninguna de ellas garantiza un avistamiento. No pegues iconos de animales sobre coordenadas ficticias. Generaliza o excluye localizaciones sensibles, nidos y refugios. Respeta geoprivacidad y precisión original de iNaturalist/GBIF.

Modelos 3D: solo GLB/glTF o visores autorizados con taxón correcto, autor, fuente, licencia, versión y revisión. No presentes un animal generado, una especie parecida o un modelo genérico como ejemplar real de otra especie. Si no existe un modelo verificable, ofrece un panel fotográfico bien diseñado. Carga los modelos bajo demanda con límite de peso y alternativa accesible. No afirmes que todos los animales o árboles del mapa están reconstruidos.

7. FUENTES Y BASE DE DATOS

Usa primero gestores de parques y administraciones para rutas, regulación y accesos; IGN/CNIG/IDEM y servicios regionales para cartografía; inventarios oficiales, GBIF e iNaturalist para biodiversidad; Wikimedia Commons para medios; Wikipedia/Wikidata para contexto y relaciones, con trazabilidad y revisión.

No hagas scraping indiscriminado ni presupongas acceso a una API de Wikiloc. Su ayuda consultada el 27/10/2026 indica que no ofrece una API pública. Los enlaces y GPX aportados con permisos son una vía distinta de copiar su base de rutas.

Arquitectura objetivo: PostgreSQL + PostGIS, entidades normalizadas de áreas, rutas, tramos, taxones, hábitats, cuerpos de agua, observaciones, avisos, fuentes, fotografías, modelos 3D, usuarios, favoritos y versiones. Archivos pesados en almacenamiento de objetos/CDN, no dentro de filas SQL ni descargados todos al inicio. Índices espaciales, consultas por caja visible, paginación, caché, búsqueda y relación explícita evidencia-entidad.

Registra por dato: origen, identificador externo, autor/editor, licencia, fecha de observación si existe, fecha de consulta, resolución/precisión, confianza y estado de revisión. Mantén la licencia de una observación separada de la de su foto. Preserva los registros originales de forma controlada y la política de borrado/actualización. Deduplica observaciones compartidas entre iNaturalist y GBIF.

La primera edición puede servirse con JSON y base SQLite exportable, siempre que se explique. No la llames base exhaustiva o sincronizada si no lo es. Propón una ingesta por fases con objetivos de cobertura y criterios de aprobación, no cifras inventadas de miles de rutas o especies.

8. CUADERNO PERSONAL

Guardar lugares y rutas, ordenar una escapada, configurar preferencias, importar/exportar GPX y exportar el cuaderno. En una versión sin servidor, conserva datos en el navegador y facilita exportación. Explica que no se sincronizan entre dispositivos.

El dibujo libre produce un borrador con segmentos rectos. Etiquétalo como no validado y no navegable. Para crear rutas calculadas sobre caminos reales será necesario integrar un grafo de senderos y un motor de enrutamiento, con perfiles y restricciones comprobados. No conviertas una línea recta entre favoritos en una ruta practicable.

Cuando existan cuentas, añade autenticación, autorización por propietario, políticas RLS, exportación/borrado y controles de compartición. No publiques ubicaciones o recorridos personales por defecto.

9. CALIDAD Y ENTREGABLES

Entrega código legible, configuración reproducible, archivos de datos, fuentes, licencias, documentación de ejecución y alojamiento, y un informe breve de funciones disponibles frente a pendientes. Sin botones vacíos, métricas ficticias, datos comerciales inventados o claves secretas en el navegador.

Prueba: carga real de teselas y relieve, geometrías dentro de su ámbito, referencias completas, filtros combinados, estados sin resultados, cambios de idioma/tema, persistencia de favoritos, importación de GPX inválido y multisegmento, exportación, navegación por teclado, lectores de pantalla y diseño móvil. Respeta tamaños táctiles, contraste y movimiento reducido. Describe cualquier verificación que el entorno impida; no la des por superada.

Primero inspecciona el proyecto actual y las fuentes. Propón las decisiones técnicas indispensables, el alcance comprobable del siguiente incremento y sus criterios de aceptación. Construye ese incremento completo, pruébalo y entrega una versión utilizable. Si falta un dato esencial, pregúntalo; para decisiones reversibles, usa criterio profesional y explica la decisión.

FUENTES DE REFERENCIA DEL PROMPT
https://www.comunidad.madrid/geoportal/idem
https://idem.madrid.org/visor/3D/
https://www.comunidad.madrid/medio-ambiente/cartografia-topografica-tematica
https://pnoa.ign.es/web/portal/pnoa-imagen/visualizadores-y-servicios-web
https://registry.opendata.aws/terrain-tiles/
https://maplibre.org/maplibre-gl-js/docs/examples/3d-terrain/
https://www.parquenacionalsierraguadarrama.es/visita/rutas
https://www.inaturalist.org/pages/developers
https://www.inaturalist.org/pages/api+recommended+practices
https://help.inaturalist.org/en/support/solutions/articles/151000169938
https://techdocs.gbif.org/en/data-publishing/multimedia-publishing
https://help.wikiloc.com/article/102-api-for-developers
