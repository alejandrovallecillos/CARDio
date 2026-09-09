#!/usr/bin/env python3
"""
CARRDS - generador de cartas educativas.

Uso:
    python scripts/generate.py <contenido> [--out ruta_salida.pdf]

Ejemplo:
    python scripts/generate.py orientacion
    python scripts/generate.py orientacion --out output/orientacion.pdf

Lee todos los archivos .yaml de data/<contenido>/, los agrupa en hojas
de 6 cartas, renderiza el HTML con la plantilla y lo exporta a PDF
usando un navegador Chromium (vía Playwright), lo que da un resultado
fiel a como se vería en un navegador moderno (CSS Grid, bordes
redondeados, etc.).
"""

import argparse
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
ASSETS_ICONS_DIR = ROOT / "assets" / "icons"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"

BADGE_ICON_FILE = "explorador.svg"  # icono mini que llevan todas las cartas
CARDS_PER_SHEET = 6


def tinte_claro(color_hex: str, mezcla_blanco: float = 0.88) -> str:
    """Genera una versión muy clara de un color, para usar como fondo de carta.
    mezcla_blanco: 0 = color puro, 1 = blanco puro. 0.85-0.9 da un tinte suave."""
    color_hex = color_hex.lstrip("#")
    r, g, b = (int(color_hex[i : i + 2], 16) for i in (0, 2, 4))
    r2 = round(r + (255 - r) * mezcla_blanco)
    g2 = round(g + (255 - g) * mezcla_blanco)
    b2 = round(b + (255 - b) * mezcla_blanco)
    return f"#{r2:02x}{g2:02x}{b2:02x}"


def cargar_svg(nombre_archivo: str) -> str:
    ruta = ASSETS_ICONS_DIR / nombre_archivo
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encuentra el icono '{nombre_archivo}' en {ASSETS_ICONS_DIR}"
        )
    return ruta.read_text(encoding="utf-8")


def cargar_cartas(contenido: str) -> list[dict]:
    carpeta = DATA_DIR / contenido
    if not carpeta.exists():
        disponibles = [p.name for p in DATA_DIR.iterdir() if p.is_dir()]
        raise FileNotFoundError(
            f"No existe data/{contenido}/. Contenidos disponibles: {disponibles}"
        )

    archivos = sorted(carpeta.glob("*.yaml")) + sorted(carpeta.glob("*.yml"))
    if not archivos:
        raise FileNotFoundError(f"No hay archivos .yaml dentro de data/{contenido}/")

    cartas = []
    insignia_svg = cargar_svg(BADGE_ICON_FILE)

    for archivo in archivos:
        carta = yaml.safe_load(archivo.read_text(encoding="utf-8")) or {}
        carta.setdefault("puntos_guia", [])
        carta.setdefault("trayectos", [])
        carta["insignia_svg"] = insignia_svg
        carta["color_claro"] = tinte_claro(carta.get("color", "#3f7d3f"))

        if carta.get("tipo") == "regla" and carta.get("icono"):
            carta["icono_svg"] = cargar_svg(carta["icono"])

        cartas.append(carta)

    return cartas


def agrupar_en_hojas(cartas: list[dict], por_hoja: int = CARDS_PER_SHEET) -> list[list[dict]]:
    return [cartas[i : i + por_hoja] for i in range(0, len(cartas), por_hoja)]


def renderizar_html(hojas: list[list[dict]]) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    plantilla = env.get_template("sheet.html.j2")
    css = (TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    return plantilla.render(hojas=hojas, css=css)


def html_a_pdf(html: str, ruta_salida: Path) -> None:
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page()
        pagina.set_content(html, wait_until="load")
        pagina.pdf(
            path=str(ruta_salida),
            print_background=True,
            prefer_css_page_size=True,
        )
        navegador.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera un mazo de cartas CARRDS en PDF.")
    parser.add_argument("contenido", help="Nombre de la subcarpeta dentro de data/ (ej: orientacion)")
    parser.add_argument("--out", help="Ruta del PDF de salida", default=None)
    args = parser.parse_args()

    cartas = cargar_cartas(args.contenido)
    hojas = agrupar_en_hojas(cartas)
    html = renderizar_html(hojas)

    ruta_salida = Path(args.out) if args.out else OUTPUT_DIR / f"{args.contenido}.pdf"
    html_a_pdf(html, ruta_salida)

    print(f"✅ Generadas {len(cartas)} cartas en {len(hojas)} hoja(s) A4.")
    print(f"📄 PDF: {ruta_salida}")


if __name__ == "__main__":
    main()
