"""
render_heatmap_svg.py
Lê data/contributions.json e desenha a grade clássica de 53 semanas x 7
dias em caixas coloridas e arredondadas, com uma rampa de verde estilo
GitHub. Revela a grade uma vez, com deslize diagonal linha após linha
(CSS keyframes que tocam ao carregar e depois congelam — sem loop),
mais uma legenda Menos->Mais e um rodapé com estatísticas.

Uso:
    python scripts/render_heatmap_svg.py
Gera:
    contrib-heatmap.svg
"""
import json
import datetime

INPUT_JSON = "data/contributions.json"
OUTPUT_SVG = "contrib-heatmap.svg"

# none -> mais brilhante (nível 5 é um verde neon no topo)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP = 3
COLS = 53
ROWS = 7
MARGIN_LEFT = 30
MARGIN_TOP = 20
LEGEND_H = 30
FOOTER_H = 26
STAGGER = 0.045  # por célula, na diagonal (col + row)

def load_data() -> dict:
    with open(INPUT_JSON, encoding="utf-8") as f:
        return json.load(f)


def build_grid(days: list[dict]) -> dict[tuple[int, int], dict]:
    """Mapeia (semana, dia_da_semana) -> registro do dia, alinhando pelo domingo."""
    if not days:
        return {}
    first_date = datetime.date.fromisoformat(days[0]["date"])
    start_offset = first_date.weekday()  # segunda=0 ... domingo=6
    # GitHub usa domingo como primeiro dia da semana
    dow_sunday_first = (start_offset + 1) % 7

    grid = {}
    for i, d in enumerate(days):
        idx = i + dow_sunday_first
        week = idx // 7
        dow = idx % 7
        grid[(week, dow)] = d
    return grid


def build_svg(data: dict) -> str:
    days = data["days"]
    stats = data["stats"]
    grid = build_grid(days)

    width = MARGIN_LEFT + COLS * (CELL + GAP)
    height = MARGIN_TOP + ROWS * (CELL + GAP) + LEGEND_H + FOOTER_H

    cells_svg = []
    for week in range(COLS):
        for dow in range(ROWS):
            record = grid.get((week, dow))
            level = record["level"] if record else 0
            color = PALETTE[min(level, len(PALETTE) - 1)]
            x = MARGIN_LEFT + week * (CELL + GAP)
            y0 = MARGIN_TOP + dow * (CELL + GAP)
            delay = (week * ROWS + dow) * STAGGER
            date_label = record["date"] if record else ""
            count_label = record["count"] if record else 0

            cells_svg.append(f'''
    <rect x="{x}" y="{y0 - 18}" width="{CELL}" height="{CELL}" rx="2.5"
          fill="{color}" opacity="0" class="cell">
      <title>{date_label}: {count_label} contribuições</title>
      <animate attributeName="opacity" from="0" to="1"
               begin="{delay:.3f}s" dur="0.15s" fill="freeze"/>
      <animate attributeName="y" from="{y0 - 18}" to="{y0}"
               begin="{delay:.3f}s" dur="0.15s" fill="freeze" calcMode="spline"
               keySplines="0.2 0.8 0.2 1"/>
    </rect>''')

    legend_y = MARGIN_TOP + ROWS * (CELL + GAP) + 14
    legend_swatches = []
    for i, color in enumerate(PALETTE):
        lx = width - MARGIN_LEFT - (len(PALETTE) - i) * (CELL + 4)
        legend_swatches.append(
            f'<rect x="{lx}" y="{legend_y - 10}" width="{CELL}" height="{CELL}" '
            f'rx="2.5" fill="{color}"/>'
        )

    footer_y = legend_y + FOOTER_H
    footer_text = (
        f"{stats['total_last_year']} contribuições no último ano · "
        f"streak atual: {stats['current_streak']} dias · "
        f"streak mais longo: {stats['longest_streak']} dias"
    )

    svg = f'''<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}"
     xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="transparent"/>
{"".join(cells_svg)}
  <text x="{MARGIN_LEFT}" y="{legend_y - 2}" font-family="Consolas, Menlo, monospace"
        font-size="11" fill="#8b949e">Menos</text>
{"".join(legend_swatches)}
  <text x="{width - MARGIN_LEFT + 4}" y="{legend_y - 2}" font-family="Consolas, Menlo, monospace"
        font-size="11" fill="#8b949e">Mais</text>
  <text x="{MARGIN_LEFT}" y="{footer_y}" font-family="Consolas, Menlo, monospace"
        font-size="12" fill="#c9d1d9">{footer_text}</text>
</svg>'''
    return svg


def main():
    data = load_data()
    svg = build_svg(data)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[render_heatmap_svg] salvo em {OUTPUT_SVG}")


if __name__ == "__main__":
    main()
