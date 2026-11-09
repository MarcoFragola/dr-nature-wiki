# Restaurar Dr Nature wiki

La etiqueta `site-v4` conserva la copia histórica del código y los datos. La rama `main` documenta la publicación actual en Netlify.
COPIA_DE_SEGURIDAD.json identifica el commit de origen y los SHA-256 de sus archivos. La regla .gitattributes conserva los bytes y las sumas de comprobación al clonar en otros sistemas.

## Ejecutar

Con Node.js instalado, abre una terminal en esta carpeta y ejecuta:

```sh
npm start
```

Abre http://127.0.0.1:8080/. La web no necesita paquetes de npm ni claves API para navegar. Python 3 con numpy y Pillow permite ejecutar `npm run check` y `npm run database`.

## Alcance

Incluye código, fotografías y créditos, cartografía IGN/MITECO, inventario nacional, GPX, scripts, documentación y la SQLite exportada. Las geometrías comprimidas conservan íntegros los datos originales. Se mantienen las licencias de cada medio.

El cuaderno personal se guarda en el navegador y se exporta desde la web; no forma parte del código. La cartografía remota depende de sus proveedores.

La web se publica desde `dist/` mediante una carga manual en el [proyecto de Netlify](https://app.netlify.com/projects/dr-nature-wiki/deploys). La referencia histórica de `COPIA_DE_SEGURIDAD.json` corresponde a la etiqueta `site-v4`.
