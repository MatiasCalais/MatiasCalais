"""
make_ascii_svg.py
Lê source-prepped.png, reduz para uma grade de caracteres (~100x53),
mapeia o brilho de cada "pixel" da grade para um glifo de densidade,
e gera um SVG monocromático onde cada linha "digita" da esquerda para
a direita (clip-path animado via SMIL), com atraso escalonado de cima
para baixo. Roda uma vez e congela (sem loop).

Uso:
    python scripts/make_ascii_svg.py
Gera:
    avi-ascii.svg   (mantive o nome de saída do artigo original)
"""
from PIL import Image

INPUT_IMAGE = "source-prepped.png"
OUTPUT_SVG = "matias-ascii.svg"

GRID_W = 100
GRID_H = 53

# bright (sparse) -> dark (dense); o espaço inicial "apaga" o fundo
RAMP = " .`:-=+*cs#%@"

CHAR_W = 6.0
CHAR_H = 11.0
FILL_COLOR = "#c9d1d9"  # cinza claro, monocromático
FONT_SIZE = 11
ROW_STAGGER = 0.09   # segundos entre o início de cada linha
ROW_DURATION = 0.8   # duração da digitação de uma linha

def image_to_ascii_grid(path: str, cols: int, rows: int) -> list[str]:
    img = Image.open(path).convert("L").resize((cols, rows))
    pixels = list(img.getdata())
    ramp_len = len(RAMP)
    lines = []
    for r in range(rows):
        row_pixels = pixels[r * cols:(r + 1) * cols]
        chars = []
        for p in row_pixels:
            idx = min(ramp_len - 1, (p * ramp_len) // 256)
            chars.append(RAMP[idx])
        lines.append("".join(chars))
    return lines


def escape_xml(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def build_svg(lines: list[str]) -> str:
    width = GRID_W * CHAR_W
    height = GRID_H * CHAR_H + 20

    rows_svg = []
    for i, line in enumerate(lines):
        y = 14 + i * CHAR_H
        text_escaped = escape_xml(line) or " "
        start_time = i * ROW_STAGGER
        row_width = len(line) * CHAR_W

        # clip-path que revela a linha da esquerda para a direita
        rows_svg.append(f'''
    <clipPath id="clip-row-{i}">
      <rect x="0" y="{y - CHAR_H}" width="0" height="{CHAR_H}">
        <animate attributeName="width" from="0" to="{row_width}"
                 begin="{start_time:.3f}s" dur="{ROW_DURATION}s"
                 fill="freeze" calcMode="linear" />
      </rect>
    </clipPath>''')

    text_elements = []
    for i, line in enumerate(lines):
        y = 14 + i * CHAR_H
        text_escaped = escape_xml(line) or " "
        text_elements.append(
            f'    <text x="0" y="{y}" clip-path="url(#clip-row-{i})" '
            f'font-family="Consolas, Menlo, monospace" font-size="{FONT_SIZE}" '
            f'fill="{FILL_COLOR}" xml:space="preserve">{text_escaped}</text>'
        )

    svg = f'''<svg viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}"
     xmlns="http://www.w3.org/2000/svg">
  <defs>{"".join(rows_svg)}
  </defs>
  <rect width="100%" height="100%" fill="transparent"/>
{chr(10).join(text_elements)}
</svg>'''
    return svg


def main():
    lines = image_to_ascii_grid(INPUT_IMAGE, GRID_W, GRID_H)
    svg = build_svg(lines)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[make_ascii_svg] salvo em {OUTPUT_SVG}")


if __name__ == "__main__":
    main()
