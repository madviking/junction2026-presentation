"""Days from symptom onset to each pathway step, by first-contact provider (DLBCL, Kuitunen et al. 2026)."""

import plotly.graph_objects as go

from app.charts import new_figure, read_csv

CHART = {
    "title": "Days from symptom onset, by where patients first sought care",
    "subtitle": "Lymphoma patients who started in public primary care reached treatment 84 days later than those with private or occupational care. Grouped by provider, not by language.",
    "source": "Kuitunen et al., Cancer Medicine 2026;15:e71920 (DLBCL, 160 patients, 2014–2020), as shown in the Espoo talk 13.11.2026 (brain: sources/2026-11-14-espoo-equity-talk-kuitunen.md)",
    "order": 40,
    "height": 280,
}


def build(p: dict):
    rows = read_csv("symptom_to_treatment_by_provider.csv")
    steps = [r["step"].replace(" ", "<br>") for r in rows]
    fig = new_figure(
        p,
        legend={"orientation": "h", "x": 0, "y": 1.12, "font": {"color": p["ink"]}},
        xaxis={"gridcolor": "rgba(0,0,0,0)", "tickfont": {"color": p["muted"], "size": 11}, "tickangle": 0},
        yaxis={"range": [0, 230], "dtick": 50, "ticksuffix": " d", "gridcolor": p["line"],
               "zeroline": False, "tickfont": {"color": p["muted"]}},
        margin={"l": 8, "r": 16, "t": 36, "b": 8},
    )
    series = (
        ("Private or occupational care", "private_occupational_days", p["lake"], "bottom right"),
        ("Public primary care", "public_primary_days", p["coral"], "top left"),
    )
    for name, col, color, pos in series:
        days = [int(r[col]) for r in rows]
        fig.add_trace(
            go.Scatter(
                x=steps, y=days, name=name, mode="lines+markers+text",
                line={"color": color, "width": 2.5}, marker={"color": color, "size": 7},
                text=[str(d) if d else "" for d in days], textposition=pos,
                textfont={"color": p["ink"], "size": 11}, cliponaxis=False,
                hovertemplate="<b>%{x}</b> · " + name + "<br>day %{y}<extra></extra>",
            )
        )
    table = {
        "columns": ["Step", "Private / occupational (days)", "Public primary care (days)", "Difference (days)"],
        "rows": [[r["step"], r["private_occupational_days"], r["public_primary_days"],
                  int(r["public_primary_days"]) - int(r["private_occupational_days"])] for r in rows],
    }
    return fig, table
