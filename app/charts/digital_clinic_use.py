"""Public digital-clinic contacts per person, by population group (8 counties, register study)."""

import plotly.graph_objects as go

from app.charts import new_figure, read_csv

CHART = {
    "title": "Public digital-clinic contacts per person, by group",
    "subtitle": "In the eight counties studied, people whose native language is not Finnish or Swedish used the chat clinic 40% less than residents overall (0.12 vs 0.20 contacts per person).",
    "source": "Kujansivu et al., Scand J Prim Health Care 2026, register study of 8 wellbeing services counties, 2022–2025; Helsinki and Vantaa–Kerava not included (brain: sources/2026-11-14-aalto-digital-clinic-users-register-study.md)",
    "order": 60,
    "height": 250,
}


def build(p: dict):
    rows = read_csv("digital_clinic_use_by_group.csv")[::-1]  # "All residents" on top
    color = {"reference": p["lake"], "silta": p["coral"], "context": p["reference"]}
    values = [float(r["contacts_per_person"]) for r in rows]
    fig = new_figure(
        p,
        showlegend=False,
        xaxis={"range": [0, 0.56], "showticklabels": False, "showgrid": False,
               "title": {"text": "Contacts per person", "font": {"color": p["muted"], "size": 13}}},
        yaxis={"gridcolor": "rgba(0,0,0,0)", "tickfont": {"color": p["ink"]}},
        margin={"l": 8, "r": 16, "t": 8, "b": 8},
    )
    fig.add_trace(
        go.Bar(
            x=values,
            y=[r["group"] for r in rows],
            orientation="h",
            marker={"color": [color[r["role"]] for r in rows], "cornerradius": 4, "line": {"width": 0}},
            text=[f"{v:.2f}" for v in values],
            textposition="outside",
            textfont={"color": p["ink"], "size": 12},
            cliponaxis=False,
            customdata=[r["digital_share_pct"] + "%" if r["digital_share_pct"] else "not stated" for r in rows],
            hovertemplate="<b>%{y}</b><br>%{x:.2f} digital-clinic contacts per person"
                          "<br>digital share of public primary-care contacts: %{customdata}<extra></extra>",
        )
    )
    table = {
        "columns": ["Group", "Digital-clinic contacts per person", "Digital share of public primary-care contacts"],
        "rows": [[r["group"], r["contacts_per_person"], (r["digital_share_pct"] + "%") if r["digital_share_pct"] else "not stated"]
                 for r in rows[::-1]],
    }
    return fig, table
