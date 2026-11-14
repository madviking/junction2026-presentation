"""County foreign-language share vs breast screening attendance."""

import plotly.graph_objects as go

from app.charts import new_figure, read_csv

CHART = {
    "title": "Counties with more foreign-language residents screen less",
    "subtitle": "22 mainland wellbeing services counties. County-level correlation r = −0.85; it does not prove the same for individuals.",
    "source": "Statistics Finland 11rm (2025) + Sotkanet breast screening 2024 (brain: sources/2026-11-13-hva-languages.md)",
    "order": 30,
}

LABELLED = {"Helsinki", "Vantaa–Kerava", "Western Uusimaa"}


def build(p: dict):
    rows = [r for r in read_csv("county_language_screening.csv") if r["breast_pct_2024"]]
    fig = new_figure(
        p,
        xaxis={"title": {"text": "Foreign-language residents (%)", "font": {"color": p["muted"]}},
               "ticksuffix": "%", "automargin": True, "gridcolor": p["line"], "zeroline": False, "tickfont": {"color": p["muted"]}},
        yaxis={"title": {"text": "Breast screening (%)", "font": {"color": p["muted"]}},
               "ticksuffix": "%", "automargin": True, "gridcolor": p["line"], "zeroline": False, "tickfont": {"color": p["muted"]}},
        showlegend=False,
        margin={"l": 8, "r": 16, "t": 8, "b": 8},
    )
    fig.add_trace(
        go.Scatter(
            x=[float(r["foreign_language_pct"]) for r in rows],
            y=[float(r["breast_pct_2024"]) for r in rows],
            mode="markers+text",
            text=[r["county"] if r["county"] in LABELLED else "" for r in rows],
            # Label to the right on the left half of the plot, to the left on the right half.
            textposition=["middle right" if float(r["foreign_language_pct"]) < 15 else "middle left" for r in rows],
            textfont={"color": p["muted"], "size": 12},
            customdata=[[r["county"], int(r["foreign_language_residents"])] for r in rows],
            marker={"size": 11, "color": p["lake"], "line": {"width": 2, "color": p["surface"]}},
            hovertemplate="<b>%{customdata[0]}</b><br>%{x:.1f}% foreign-language (%{customdata[1]:,})"
            "<br>%{y:.1f}% breast screening<extra></extra>",
        )
    )
    table = {
        "columns": ["County", "Foreign-language %", "Breast screening %"],
        "rows": [[r["county"], r["foreign_language_pct"], r["breast_pct_2024"]] for r in rows],
    }
    return fig, table
