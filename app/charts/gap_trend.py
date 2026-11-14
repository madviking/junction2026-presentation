"""Attendance gap by native language over time, per programme."""

import plotly.graph_objects as go

from app.charts import new_figure, read_csv

CHART = {
    "title": "Attendance gap, domestic minus other-language (percentage points)",
    "subtitle": "Breast and cervical gaps widened from 2020 to 2024; colorectal (programme from 2022) is flat.",
    "source": "Finnish Cancer Registry native-language tables 2020–2024 (brain: sources/2026-11-14-cancerregistry-screening-by-language.md)",
    "order": 25,
    "height": 240,
}


def build(p: dict):
    rows = read_csv("screening_by_language.csv")
    series = (("Cervical", p["lake"], "dash"), ("Breast", p["lake"], "solid"), ("Colorectal", p["reference"], "dot"))
    fig = new_figure(
        p,
        showlegend=False,
        xaxis={"dtick": 1, "range": [2019.8, 2024.9], "gridcolor": "rgba(0,0,0,0)", "tickfont": {"color": p["muted"]}},
        yaxis={"range": [12, 25],
               "title": {"text": "Fewer attending, per 100 invited", "font": {"color": p["muted"], "size": 13}}, "gridcolor": p["line"], "zeroline": False,
               "tickfont": {"color": p["muted"]}},
        margin={"l": 8, "r": 96, "t": 8, "b": 8},
    )
    nudge = {"Breast": 6, "Colorectal": -6, "Cervical": 0}  # end labels for breast and colorectal sit close
    for name, color, dash in series:
        pts = [r for r in rows if r["programme"] == name]
        years = [int(r["year"]) for r in pts]
        gaps = [float(r["gap_pp"]) for r in pts]
        fig.add_trace(
            go.Scatter(
                x=years, y=gaps, name=name, mode="lines+markers",
                line={"color": color, "width": 2.5, "dash": dash},
                marker={"color": color, "size": 7},
                hovertemplate=f"<b>{name} %{{x}}</b><br>%{{y:.1f}} fewer per 100 invited<extra></extra>",
            )
        )
        fig.add_annotation(x=years[-1], y=gaps[-1], text=f"{name} {gaps[-1]:.1f}", showarrow=False,
                           xanchor="left", xshift=10, yshift=nudge[name], font={"color": color, "size": 13})
    table = {
        "columns": ["Programme", "Year", "Domestic %", "Other %", "Gap (percentage points)"],
        "rows": [[r["programme"], r["year"], r["domestic_pct"], r["other_pct"], r["gap_pp"]] for r in rows],
    }
    return fig, table
