# Dr Nature wiki

**Curiosidades de Marco.** Un atlas personal de naturaleza para explorar Madrid, Castilla y León y Castilla-La Mancha, con una selección invitada del Valle del Jerte.

[Explorar la web pública](https://dr-nature-wiki.netlify.app/)

## Qué encontrarás

- Una portada con relieve y ortofoto del IGN, y un mapa interactivo con búsqueda, capas y filtros.
- 55 lugares, 66 rutas y visitas, y 66 fichas de vida. Hay 22 recorridos con trazado GPX oficial.
- Una demostración de la ruta de Cotos con relieve local, ortofoto PNOA y el trazado oficial.
- Un Atlas natural ilustrado y una referencia nacional del MITECO con 69.244 taxones consultables por nombre y grupo.
- Un cuaderno para guardar fichas, organizar colecciones y trabajar con GPX. Se guarda en el navegador y se puede exportar.

Las fichas son una selección personal documentada. Cada fuente indica el alcance de sus datos. La cartografía del mapa interactivo se carga desde el IGN y Terrain Tiles.

## Ejecutar en local

Con Node.js instalado, ejecuta desde la raíz del repositorio:

```sh
npm start
```

Abre [http://127.0.0.1:8080/](http://127.0.0.1:8080/). Para navegar basta con los archivos estáticos de `dist/`. El sitio funciona sin cuentas ni claves de API.

```sh
npm run check
node --test scripts/test-*.mjs
```

La comprobación de datos utiliza Python 3 con NumPy y Pillow. La carpeta `dist/` contiene la versión lista para publicar en Netlify. `data/catalogue.sqlite` es una exportación de consulta y `scripts/` contiene las herramientas de preparación y validación.

## Publicación en Netlify

Para actualizar el sitio, sube `dist/` a [los despliegues del proyecto](https://app.netlify.com/projects/dr-nature-wiki/deploys). La publicación actual es manual y el sitio estático viene preparado en esa carpeta.

## Créditos y licencias

El [código usa la licencia MIT](LICENSE). Las fotografías, la cartografía y los GPX conservan las licencias y créditos de sus fuentes. Consulta los [créditos fotográficos](docs/creditos-fotografias.md), la [procedencia cartográfica](docs/geografia.md) y los [metadatos de la demostración de Cotos](dist/data/route-lesson/metadata.json).
