"""
make_info_card.py
Gera um SVG estilo "neofetch": uma barra de título e linhas de
chave/valor (Now, Prev, Stack, Highlights) que aparecem com fade + leve
deslize, uma após a outra. Defina STATIC=1 para gerar um frame já
congelado (útil para Quick Look / preview local).

Uso:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py
Gera:
    info-card.svg
"""
import os

OUTPUT_SVG = "info-card.svg"

# >>> Edite estes dados com as suas informações <<<
USERNAME = "MatiasCalais"
TITLE_BAR = f"{USERNAME}@github"
ROWS = [
    ("Now", "Estudando e buscando cada vez mais resover problema"),
    ("Prev", "Suporte"),
    ("Stack", "java · C# · SQLserver · MySQL"),
    ("Highlights", "Meu primeiro projeto open-source"),
]

WIDTH = 490
ROW_HEIGHT = 34
PADDING_TOP = 70
STAGGER = 0.15
FADE_DURATION = 0.4

KEY_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"
BAR_COLOR = "#161b22"
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"


def build_svg(static: bool) -> str:
    height = PADDING_TOP + ROW_HEIGHT * len(ROWS) + 20

    rows_svg = []
    for i, (key, value) in enumerate(ROWS):
        y = PADDING_TOP + i * ROW_HEIGHT
        start = i * STAGGER

        if static:
            opacity_attr = 'opacity="1"'
            transform = ""
            animation = ""
        else:
            opacity_attr = 'opacity="0"'
            transform = ' transform="translate(-8,0)"'
            animation = f'''
        <animate attributeName="opacity" from="0" to="1"
                 begin="{start:.2f}s" dur="{FADE_DURATION}s" fill="freeze" />
        <animateTransform attributeName="transform" type="translate"
                 from="-8,0" to="0,0" begin="{start:.2f}s"
                 dur="{FADE_DURATION}s" fill="freeze" />'''

        rows_svg.append(f'''
    <g {opacity_attr}{transform}>{animation}
      <text x="24" y="{y}" font-family="Consolas, Menlo, monospace"
            font-size="14" font-weight="bold" fill="{KEY_COLOR}">{key}</text>
      <text x="160" y="{y}" font-family="Consolas, Menlo, monospace"
            font-size="14" fill="{VALUE_COLOR}">{value}</text>
    </g>''')

    svg = f'''<svg viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}"
     xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="{WIDTH}" height="{height}" rx="8"
        fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1"/>
  <rect x="0" y="0" width="{WIDTH}" height="34" rx="8" fill="{BAR_COLOR}"/>
  <circle cx="20" cy="17" r="6" fill="#ff5f56"/>
  <circle cx="40" cy="17" r="6" fill="#ffbd2e"/>
  <circle cx="60" cy="17" r="6" fill="#27c93f"/>
  <text x="{WIDTH/2}" y="22" text-anchor="middle" font-family="Consolas, Menlo, monospace"
        font-size="13" fill="{VALUE_COLOR}">{TITLE_BAR}</text>
{"".join(rows_svg)}
</svg>'''
    return svg


def main():
    static = os.environ.get("STATIC") == "1"
    svg = build_svg(static)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[make_info_card] salvo em {OUTPUT_SVG} (static={static})")


if __name__ == "__main__":
    main()
