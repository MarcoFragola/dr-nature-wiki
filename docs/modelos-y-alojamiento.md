# Cómo continuar Dr Nature wiki

Recomendación preparada el 27 de octubre de 2026. Los modelos, planes y condiciones de alojamiento pueden cambiar; consulta las páginas enlazadas al contratar.

## ¿Hace falta otro prompt?

La visión del proyecto y la dirección visual están concretadas. El archivo `vision-producto.md` organiza la visión completa y sus criterios de calidad para continuar en otra sesión, modelo o herramienta. Adjunta también el proyecto actual y pide una mejora concreta por entrega. El prompt describe el producto objetivo; el README explica lo que ya está implementado.

## Entorno, modelo y esfuerzo

Mi elección para este proyecto es Codex con **GPT‑6.1 Sol y pensamiento High** para programar, probar y mantener el repositorio. La documentación oficial presenta Sol como una opción capaz para trabajo prolongado de código; usarlo como opción habitual es mi recomendación práctica, no una garantía de calidad automática.

Usaría **GPT‑6 Astra, High o Extra High**, para decisiones difíciles de arquitectura geoespacial, revisión de fuentes y problemas que Sol no resuelva satisfactoriamente. Reservaría esfuerzos mayores para una dificultad concreta, después de medir el resultado. Work y Codex son entornos de trabajo; Sol y Astra son modelos. Work resulta útil para organizar investigación, diseño y entregables; Codex para trabajar sobre el código. La disponibilidad depende de tu cuenta y configuración.

Fuente oficial: https://learn.chatgpt.com/docs/models . No necesitas una API de IA en la web publicada para que los visitantes exploren mapas y fichas: el proyecto entregado no hace inferencias ni consume una clave de OpenAI.

## Recomendación de alojamiento

Para esta edición estática elegiría **GitHub para versionar el código y Cloudflare Pages para servir `dist/`**. GitHub Pages es una alternativa estática. No hace falta contratar una máquina permanente para esta versión. Antes de elegir plan, revisa los límites actuales, tráfico, condiciones comerciales y condiciones de los proveedores de cartografía. No se garantiza coste cero de un producto ampliado.

1. Crea un repositorio propio y sube el código completo, sin claves, GPX personales ni archivos `.env`. El ZIP entregado no contiene credenciales.
2. Conecta ese repositorio a Cloudflare Pages, selecciona un proyecto estático y la carpeta de salida `dist`. No se necesita compilación; si la interfaz exige un comando, utiliza un comando inocuo como `exit 0`, según la documentación vigente.
3. Abre la URL generada y comprueba teselas, fuentes, rutas, idioma, favoritos e importación GPX en un navegador con WebGL y en móvil.
4. Añade un dominio propio desde el panel del alojamiento y configura DNS/HTTPS según sus instrucciones. Esta entrega no compra un dominio ni crea una cuenta en esos proveedores.
5. Mantén cambios por commits, revisión de contenido, copias de seguridad y fecha de consulta. Para recibir público amplio, revisa límites y continuidad de los servicios de mapas; un servicio público de teselas no equivale a una garantía de disponibilidad.

Documentación de alojamiento:

- Cloudflare Pages, HTML estático: https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
- GitHub Pages: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages

El despliegue privado de Sites que acompaña esta entrega permite revisar el resultado. Un repositorio de Sites no es tu cuenta de GitHub; el ZIP te permite llevarte el proyecto y crear allí su historial.

## Hacia una base de conocimiento extensa

La cantidad de datos exige una ingesta editorial y geográfica mantenida. No se resuelve rellenando fichas con IA. La base SQLite entregada contiene datos reales de esta primera edición; el frontend consume el mismo catálogo en JSON. Para crecer, propongo:

| Etapa | Resultado verificable |
|---|---|
| 1. Catálogo revisado | Completar áreas prioritarias, rutas oficiales, fuentes, fechas, relaciones entre taxones y lugares; control de licencias y revisiones |
| 2. Capas consultables | Incorporar hidrografía, límites de espacios protegidos y hábitats desde servicios oficiales con metadatos; consulta por elemento |
| 3. Base geoespacial | PostgreSQL/PostGIS, índices espaciales, paginación por área visible, almacenamiento de medios en objetos/CDN y tareas de actualización |
| 4. Observaciones | Ingesta autorizada de GBIF/iNaturalist, deduplicación, privacidad geográfica, precisión y evidencia de presencia claramente separadas |
| 5. Cuentas y planificación | Autenticación, favoritos sincronizados, autorización por propietario y rutas calculadas sobre caminos permitidos mediante un motor de enrutamiento |
| 6. Avisos y modelos | Integración con fuentes vigentes de restricciones/meteorología y modelos 3D con taxón, licencia y calidad verificados |

Supabase con PostGIS es una posible base gestionada; no está conectada en esta entrega: https://supabase.com/docs/guides/database/extensions/postgis . Define primero el volumen esperado y las consultas antes de escoger plan.

Las tablas objetivo incluyen áreas, rutas/tramos, taxones, hábitats, agua, observaciones, medios, avisos, fuentes, versiones, usuarios y favoritos. Cada relación importante necesita evidencia. Guarda la geometría en PostGIS y los archivos pesados fuera de las filas SQL. Sirve por zona y nivel de detalle; no descargues toda España ni todos los modelos al entrar.

## IDEM y la experiencia que buscas

El visor de IDEM es una buena referencia para examinar territorio real. Dr Nature añade una capa de lectura naturalista: qué paisaje es, qué vida alberga, cómo recorrerlo, qué condiciones revisar y dónde ampliar información. La cobertura visual de un mapa y la cobertura documentada de una wiki son distintas.

La edición actual usa PNOA y Terrain Tiles. La integración de servicios IDEM, un MDT de mayor resolución o Cesium debe hacerse tras comprobar formato, atribución, disponibilidad, rendimiento y metadatos. No se ha incorporado su visor dentro de una apariencia diferente ni se promete una reconstrucción individual de todos los árboles, rocas y animales.

- IDEM: https://www.comunidad.madrid/geoportal/idem
- Visor 3D: https://idem.madrid.org/visor/3D/
- PNOA: https://pnoa.ign.es/web/portal/pnoa-imagen/visualizadores-y-servicios-web
- Terreno: https://registry.opendata.aws/terrain-tiles/
- MapLibre: https://maplibre.org/maplibre-gl-js/docs/examples/3d-terrain/

## Fuentes y condiciones prácticas

Wikiloc indica en su ayuda consultada que no ofrece una API pública. No diseñes una ingesta suponiendo ese acceso: https://help.wikiloc.com/article/102-api-for-developers . Enlazar una ruta y reutilizar su GPX son acciones con condiciones distintas.

iNaturalist recomienda su API actual y vías de exportación para volumen; respeta las ubicaciones ocultas o privadas. GBIF distingue la licencia del registro de la licencia de sus medios. No asumas que una foto hereda los permisos de una observación.

- https://www.inaturalist.org/pages/api+recommended+practices
- https://help.inaturalist.org/en/support/solutions/articles/151000169938
- https://techdocs.gbif.org/en/data-publishing/multimedia-publishing

La fuente de Guadarrama publica CC BY-NC-SA 4.0: https://www.parquenacionalsierraguadarrama.es/licencia-creative-commons . Antes de una explotación comercial, comprueba la compatibilidad de los recursos y consigue los permisos necesarios o sustitúyelos. Este aviso se refiere a recursos concretos incluidos; no a una restricción general del código original.
