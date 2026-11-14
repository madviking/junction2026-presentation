"""Screening attendance 2024 by region of birth, one panel per programme."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.charts import FONT, new_figure, read_csv

CHART = {
    "title": "Attendance by region of birth, 2024",
    "subtitle": "People born in Africa attend breast and colorectal screening at just over half the rate of people born in Finland.",
    "source": "Finnish Cancer Registry, screening statistics 2024 (brain: sources/2026-11-14-cancerregistry-screening-by-language.md)",
    "order": 40,
    "wide": True,
    "height": 300,
}

PROGRAMMES = (("Breast", "breast_pct"), ("Cervical", "cervical_pct"), ("Colorectal", "colorectal_pct"))


def build(p: dict):
    rows = read_csv("screening_by_birth_region_2024.csv")
    regions = [r["region"] for r in rows][::-1]  # Finland on top
    template = new_figure(p)
    fig = make_subplots(rows=1, cols=3, shared_yaxes=True, horizontal_spacing=0.04,
                        subplot_titles=[name for name, _ in PROGRAMMES])
    fig.update_layout(template.layout, showlegend=False)
    for col, (name, key) in enumerate(PROGRAMMES, start=1):
        values = [float(r[key]) for r in rows][::-1]
        colors = [p["lake"] if region == "Finland" else p["coral"] for region in regions]
        fig.add_trace(
            go.Bar(
                x=values,
                y=regions,
                orientation="h",
                marker={"color": colors, "cornerradius": 4, "line": {"width": 0}},
                text=[f"{v:.0f}%" for v in values],
                textposition="outside",
                textfont={"color": p["ink"], "size": 12},
                cliponaxis=False,
                hovertemplate=f"<b>%{{y}}</b> · {name}<br>%{{x:.1f}}% attended<extra></extra>",
            ),
            row=1,
            col=col,
        )
        fig.update_xaxes(range=[0, 100], tickvals=[0, 50], ticksuffix="%", gridcolor=p["line"], zeroline=False,
                         tickfont={"color": p["muted"]}, row=1, col=col)
    fig.update_yaxes(tickfont={"color": p["muted"]}, gridcolor="rgba(0,0,0,0)")
    fig.update_annotations(font={"family": FONT, "color": p["ink"], "size": 13})
    fig.update_layout(margin={"l": 8, "r": 24, "t": 28, "b": 8})
    table = {
        "columns": ["Region of birth", "Breast %", "Cervical %", "Colorectal %"],
        "rows": [[r["region"], r["breast_pct"], r["cervical_pct"], r["colorectal_pct"]] for r in rows],
    }
    return fig, table
