DR NATURE WIKI · REFERENCIA DE BIODIVERSIDAD DE ESPAÑA
Instantánea consultada: 27 de octubre de 2026

La fuente es la Lista Patrón de las especies silvestres presentes en España,
publicada por MITECO/IEPNB mediante su API pública de listas controladas.
No se han mezclado estos registros con las fichas curadas del atlas.

CONTENIDO
69.244 taxones únicos de 14 grandes grupos de navegación.
64.360 registros tienen rango Species; los demás corresponden a subespecies,
variedades, formas y otros rangos. La cifra total no es una cifra de especies.
2.885 taxones incluyen nombre común facilitado por la fuente. No se han
inventado traducciones ni nombres comunes para completar los demás.

El servicio oficial declara 69.249 filas: cinco IDs se repiten en su vista
por variantes de nombre común o distinta representación de una autoría vacía.
La consolidación conserva los nombres alternativos en common_names y se documenta en
source-consolidation.json. No se fusionan taxones por semejanza del nombre.

ÁMBITO
scope="ES" significa referencia taxonómica nacional, terrestre y marina.
La pertenencia a la Lista Patrón no acredita presencia en Madrid ni en una
ruta o punto concreto. Estos registros no contienen observaciones, nidos,
coordenadas sensibles ni distribución local inferida.

No se incorporan fotografías ni descripciones biológicas para estos miles
de registros. Las fotografías y el contenido editorial de las fichas curadas
conservan sus propias fuentes y licencias, independientes de esta referencia.

ARCHIVOS Y USO EN LA WEB
metadata.json contiene fuente, licencia, ámbito, totales, grupos y limitaciones
sin las 69.244 tuplas del buscador. Puede abrirse para mostrar procedencia sin
descargar el índice de búsqueda completo.

index.json (~4,63 MB) contiene:
- total_taxa: número de IDs taxonómicos únicos.
- source: procedencia, licencia, atribución, fecha y URLs oficiales.
- scope, limitations, ranks y kingdoms: ámbito y límites del conjunto.
- groups: id, label.es/label.en, count y lista de índices de chunks.
- chunks: file, group, label, count, bytes y extremos alfabéticos.
- search_columns: ["id","scientific_name","common_name","group","chunk"].
- search: una tupla por taxón, siguiendo ese orden de columnas.

El último valor de cada tupla es un índice entero de chunks, no un nombre
de archivo. El archivo se obtiene con index.chunks[row[4]].file. Las rutas
file ya son relativas a la raíz de la web (data/biodiversity/chunks/...).
Conviene cargar el índice solo al abrir esta biblioteca y cargar cada chunk
bajo demanda al pedir un registro, sin descargar los 79 chunks al inicio.

Cada chunk contiene {schema,source_id,scope,group,records}. Cada registro:
id, source_taxon_id, taxon_concept_id, scientific_name,
scientific_name_with_author, authorship, common_name,
common_name_language, kingdom, phylum, class, order, family, genus,
rank, group, source_group, environment, origin, source_id, source_url,
scope, name_according_to, taxon_remarks.

Los campos no facilitados por la fuente son null o vacíos. El API no declara el idioma
de cada nombre común; common_name_language se conserva como null. La etiqueta
de interfaz recomendada es "Nombre común (fuente)". Se conserva el texto real
de la fuente, sin atribuirle una lengua que no viene documentada por registro.

id usa el identificador oficial estable con prefijo miteco:lp:.
source_url lleva a una consulta de la API restringida al ID correspondiente.
La taxonomía original se conserva: group es solo una ayuda de navegación
derivada de kingdom/class/phylum/source_group. Los valores originales se
mantienen en sus campos; los líquenes no se identifican por apariencia.

curated-links.json relaciona 63 fichas curadas con IDs de esta referencia por
igualdad exacta del nombre científico. No infiere sinonimias ni presencia local.
Las fichas curadas que no coinciden exactamente siguen siendo válidas por sus
fuentes originales y no se alteran por esta falta de coincidencia.

import-report.json resume cifras y tamaño. source-consolidation.json explica
las cinco filas adicionales de la fuente. La fuente no proporciona una fecha
global de actualización en estas respuestas: fecha de consulta no equivale a
fecha de última revisión taxonómica. La instantánea no se actualiza sola.

REPRODUCCIÓN
Desde cualquier directorio, con Python 3 y acceso a Internet:
  python web/scripts/prepare_biodiversity_reference.py

Para regenerar con la instantánea local y comprobar sus hashes, sin red:
  python web/scripts/prepare_biodiversity_reference.py --offline

Para obtener una nueva instantánea oficial:
  python web/scripts/prepare_biodiversity_reference.py --refresh

Los originales y sus hashes se guardan en web/tmp/biodiversidad, que está
excluido por el .gitignore existente. No se publica esa caché de trabajo.
La importación utiliza la API oficial de integración, no la descarga web
protegida con CAPTCHA. Mantiene validación TLS y carga certificados de
confianza del sistema; no desactiva comprobaciones de certificados.

FUENTES Y LICENCIA
Lista Patrón:
https://pro.iepnb.gob.es/recursos/listas-controladas
API pública:
https://iepnb.gob.es/api/catalogo/v_listapatronespecie
Documentación de la API:
https://pro.iepnb.gob.es/recursos/servicios-interoperables/api-catalogo
Condiciones de reutilización y licencia por defecto del portal:
https://pro.iepnb.gob.es/aviso-legal
CC BY 4.0, salvo indicación distinta de un conjunto:
https://creativecommons.org/licenses/by/4.0/

Atribución: MITECO / Inventario Español del Patrimonio Natural y de la
Biodiversidad, Lista Patrón de las especies silvestres presentes en España;
instantánea del 27/10/2026. Datos normalizados para Dr Nature wiki.
Esta reutilización no implica patrocinio ni validación del proyecto por MITECO.
