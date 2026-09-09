# CARRDS 🃏

Generador automático de cartas educativas para Educación Física (orientación,
deportes, condición física, nutrición...). Defines cada carta en un archivo de
texto sencillo (YAML) y el proyecto genera un PDF listo para imprimir, con
**6 cartas por hoja A4**, para plastificar y usar en clase.

## Cómo funciona

```
data/<contenido>/*.yaml   →  scripts/generate.py  →  output/<contenido>.pdf
      (tus cartas)           (plantilla + estilo)      (listo para imprimir)
```

- `data/` — un archivo `.yaml` por carta, agrupados en carpetas por contenido
  (`orientacion`, `deportes`, `nutricion`, `condicion_fisica`...).
- `templates/` — la plantilla HTML (`sheet.html.j2`) y los estilos (`style.css`).
  Aquí se define el diseño de la carta; cámbialo una vez y afecta a todas las
  cartas.
- `assets/icons/` — iconos SVG reutilizables en varias cartas.
- `scripts/generate.py` — script que lee las cartas de un contenido, las
  agrupa de 6 en 6 y exporta el PDF.
- `output/` — PDFs ya generados (se regeneran solos al hacer *push*, ver más
  abajo).

## Uso en local

```bash
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium     # descarga el navegador que genera el PDF (una sola vez)

python scripts/generate.py orientacion
# -> output/orientacion.pdf
```

## Cómo añadir una carta nueva (sin tocar código)

1. Ve a la carpeta del contenido correspondiente en `data/` (o créala si es un
   contenido nuevo, ej. `data/nutricion/`).
2. Copia un archivo `.yaml` parecido al que quieras crear y cambia sus valores.
3. Hay dos tipos de carta ahora mismo:

   **Tipo "ruta"** (dibujo de puntos y líneas):
   ```yaml
   id: "006"
   contenido: orientacion
   color: "#3f7d3f"
   tipo: ruta
   categoria_label: "RUTA ESPACIAL"
   trayectos:
     - [[30,10],[60,10],[60,45],[85,45],[85,80],[30,80],[30,10]]
   puntos_guia:
     - [15,18]
   ```
   Los puntos son coordenadas de 0 a 100 (como un cuadrado virtual). Cada
   lista dentro de `trayectos` es una línea conectada; `puntos_guia` son
   puntos sueltos de referencia (aparecen en gris).

   **Tipo "regla"** (icono + título + descripción):
   ```yaml
   id: "003"
   contenido: orientacion
   color: "#3f7d3f"
   tipo: regla
   icono: memoria_visual.svg   # debe existir en assets/icons/
   titulo: "Memoria visual"
   descripcion: "Observa durante 10 segundos y después reproduce la figura sin verla."
   ```

4. Ejecuta `python scripts/generate.py <contenido>` (o simplemente haz *push*
   a GitHub, ver siguiente sección) y revisa el PDF.

## Cómo crear un contenido nuevo (ej. "deportes", "nutrición")

1. Crea una carpeta `data/deportes/`.
2. Añade tus cartas `.yaml` dentro, con un `color` distinto para diferenciar
   el mazo a simple vista (ej. azul para deportes, naranja para nutrición).
3. Si necesitas un icono nuevo, añade el `.svg` en `assets/icons/` (puedes
   pedir ayuda a Claude para crearlo).
4. Genera con `python scripts/generate.py deportes`.

## Automatización con GitHub Actions

El workflow en `.github/workflows/build.yml` hace esto automáticamente cada
vez que subes cambios en `data/`, `templates/`, `assets/` o `scripts/`:

1. Instala todo lo necesario.
2. Genera un PDF por cada carpeta dentro de `data/`.
3. Deja los PDFs descargables como *artifact* del workflow (pestaña
   **Actions** → la ejecución → **Artifacts**).
4. Además los guarda directamente en `output/` dentro del repositorio, para
   que puedas descargarlos sin entrar en Actions.

Así, para añadir una carta nueva **no necesitas instalar nada en tu
ordenador**: editas o añades el `.yaml` desde la propia web de GitHub, y en
un par de minutos tienes el PDF actualizado en `output/`.

## Cambiar el diseño de todas las cartas a la vez

Edita `templates/style.css` (colores, tipografía, grosor de línea, tamaño de
la insignia...) o `templates/sheet.html.j2` (qué información se muestra y en
qué orden). El cambio se aplica automáticamente a todas las cartas de todos
los contenidos la próxima vez que se generen.
