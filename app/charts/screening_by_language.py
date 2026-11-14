"""Screening attendance 2024 by native language (Finnish Cancer Registry)."""

import plotly.graph_objects as go

from app.charts import new_figure, read_csv

CHART = {
    "title": "Screening attendance by native language, 2024",
    "subtitle": "Share of invited people who attended. Other-language invitees attend about 20 points less in every programme.",
    "source": "Finnish Cancer Registry, screening statistics 2024 (brain: sources/2026-11-14-cancerregistry-screening-by-language.md)",
    "order": 10,
    "height": 260,
}


def build(p: dict):
    rows = [r for r in read_csv("screening_by_language.csv") if r["year"] == "2024"]
    programmes = [r["programme"] for r in rows]
    fig = new_figure(p, yaxis={"range": [0, 100], "ticksuffix": "%", "gridcolor": p["line"],
                               "tickfont": {"color": p["muted"]}, "zeroline": False})
    series = (
        ("Finnish, Swedish or Sámi", "domestic_pct", "domestic_invited", p["lake"]),
        ("Other or unknown language", "other_pct", "other_invited", p["coral"]),
    )
    for name, pct, invited, color in series:
        fig.add_trace(
            go.Bar(
                name=name,
                x=programmes,
                y=[float(r[pct]) for r in rows],
                customdata=[int(r[invited]) for r in rows],
                marker={"color": color, "cornerradius": 4, "line": {"width": 0}},
                text=[f"{float(r[pct]):.0f}%" for r in rows],
                textposition="outside",
                textfont={"color": p["ink"], "size": 12},
                cliponaxis=False,
                hovertemplate="<b>%{x}</b> · " + name + "<br>%{y:.1f}% attended<br>%{customdata:,} invited<extra></extra>",
            )
        )
    table = {
        "columns": ["Programme", "Domestic %", "Other/unknown %", "Gap (pp)"],
        "rows": [[r["programme"], r["domestic_pct"], r["other_pct"], r["gap_pp"]] for r in rows],
    }
    return fig, table
