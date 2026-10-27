# Verificación de la edición ampliada

Fecha: 27/10/2026. Pruebas en la vista local servida por Node y el navegador integrado.

## Comprobado

- Sintaxis de app.js, i18n.js, landscape.js y terrain-fallback.js correcta.
- Catálogo: 53 lugares, 55 rutas, 65 especies, 128 fuentes y 8 trazados oficiales con 3.274 coordenadas. IDs, relaciones, referencias, archivos y créditos comprobados.
- SQLite reconstruida a partir del catálogo: integrity_check correcto, sin errores de claves foráneas; 675.840 bytes. Es una exportación, no un servidor conectado.
- Fondo final WebP cargado, 1672 × 941 px y 471.716 bytes. Los nombres y la interfaz son capas de la web.
- Cámara del paisaje: zoom mediante botones (1 → 1,30), restablecimiento con Inicio (1,00), enfoque al seleccionar Peñalara y apertura/cierre de fichas.
- Búsqueda global de Ruidera, sus tres rutas y los itinerarios de Cotos; salto de un lugar fuera de la escena al Mapa real.
- Mapa real: carga de ortofoto y elevación, estado PNOA/IGN ×1,5 y visualización del GPX oficial Cotos–Zona del Zabala. Su perfil se identifica como no disponible al faltar cotas.
- Filtros combinados de Madrid, bicicleta, máximo 3 km y accesibilidad: estado sin resultados; restablecimiento a 53 lugares.
- Guardar Peñalara y conservar el favorito tras recarga; retirada posterior del favorito de prueba.
- Menú móvil, navegación al atlas, cambio ES/EN, 65 fichas y búsqueda de Aquila adalberti. Fotografía, créditos, taxón, ecología, rasgos y ámbito documental visibles en inglés.
- Tema claro y oscuro; contraste de los paneles revisado visualmente.
- Portada y filtros a 390 × 844 px y vista de escritorio. El documento móvil mide 390 px de ancho y no presenta desbordamiento horizontal. Se corrigieron solapamientos de filtros y controles.
- 40 fotografías nuevas descargadas y decodificadas: 18 lugares y 22 especies, con archivo exacto, autor y licencia. Hay 35 lugares y 45 especies con fotografía asociada. Las demás fichas muestran expresamente la imagen pendiente.
- Capturas guardadas en capturas/. La referencia inicial se conserva en referencias/.

## Límites

La vista Paisaje es una ilustración generada, no un modelo topográfico validado. Sus puntos son posiciones de composición; coordenadas y trazados pertenecen al Mapa real. El mapa necesita Internet y disponibilidad de los servicios.

Las 47 rutas sin GPX no dibujan un recorrido inventado. Métricas desconocidas siguen siendo null. No se revisaron senderos sobre el terreno, avisos en directo ni todas las combinaciones posibles de filtros.

La alternativa de relieve por software procede de la edición inicial. Esta revisión no repitió todas sus condiciones de fallo. No se ejecutó una auditoría formal WCAG, un lector de pantalla real ni pruebas físicas en iOS/Android. La importación/exportación GPX y los borradores se conservan, pero no se repitió su batería completa en esta revisión.

## Publicación

Esta edición está disponible localmente. La subida al sitio existente fue rechazada por la revisión automática al considerar insuficiente la autorización explícita del destino/publicación. No se volvió a intentar por otra vía ni se modificó la audiencia. La publicación queda pendiente de autorización de Marco.

## Repetir

```sh
npm run check
npm run database
npm start
```
