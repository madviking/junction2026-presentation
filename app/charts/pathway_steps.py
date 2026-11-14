"""Attendance at each screening step (screening, then follow-up), domestic vs other native language."""

import plotly.graph_objects as go

from app.charts import new_figure, read_csv

CHART = {
    "title": "Attendance at each step of screening, by native language",
    "subtitle": "The gap is at attending screening; follow-up after an abnormal result is about equal, except colonoscopy.",
    "source": "Finnish Cancer Registry native-language tables 2022–2024 (brain: sources/2026-11-14-cancerregistry-screening-by-language.md)",
    "order": 20,
    "height": 340,
}

SERIES = (("Finnish, Swedish or Sámi", "domestic_pct"), ("Other or unknown language", "other_pct"))


def _gap(v: float) -> str:
    return f"{v:+.1f} pts".replace("-", "−")


def build(p: dict):
    rows = read_csv("pathway_steps.csv")
    # Two-level y axis: stage (screening / follow-up), then programme + step.
    y = [[r["stage"] for r in rows], [f"{r['programme']}: {r['step'].lower()}" if r["stage"] != "Attending screening"
                                      else r["programme"] for r in rows]]
    dom = [float(r["domestic_pct"]) for r in rows]
    oth = [float(r["other_pct"]) for r in rows]
    fig = new_figure(
        p,
        xaxis={"range": [40, 100], "ticksuffix": "%", "gridcolor": p["line"], "zeroline": False,
               "tickfont": {"color": p["muted"]},
               "title": {"text": "Share who attended", "font": {"color": p["muted"], "size": 13}}},
        yaxis={"autorange": "reversed", "tickfont": {"color": p["ink"]}, "gridcolor": "rgba(0,0,0,0)"},
        margin={"l": 8, "r": 24, "t": 36, "b": 8},
        legend={"orientation": "h", "x": 1, "xanchor": "right", "y": 1.0, "yanchor": "bottom",
                "font": {"color": p["muted"]}},
    )
    # Connector line per row (one trace, None-separated).
    lx, ly0, ly1 = [], [], []
    for i in range(len(rows)):
        lx += [dom[i], oth[i], None]
        ly0 += [y[0][i], y[0][i], None]
        ly1 += [y[1][i], y[1][i], None]
    fig.add_trace(go.Scatter(x=lx, y=[ly0, ly1], mode="lines", line={"color": p["reference"], "width": 3},
                             hoverinfo="skip", showlegend=False))
    for (name, key), color in zip(SERIES, (p["lake"], p["coral"])):
        fig.add_trace(
            go.Scatter(
                x=[float(r[key]) for r in rows], y=y, mode="markers", name=name,
                marker={"color": color, "size": 13, "line": {"color": p["surface"], "width": 1.5}},
                customdata=[r["years"] for r in rows],
                hovertemplate="%{y}<br>" + name + ": %{x:.1f}%<br>%{customdata}<extra></extra>",
            )
        )
    # Gap label just right of the row's higher value.
    fig.add_trace(
        go.Scatter(
            x=[max(d, o) for d, o in zip(dom, oth)], y=y, mode="text", showlegend=False, hoverinfo="skip",
            text=[_gap(float(r["gap_pp"])) for r in rows], textposition="middle right",
            textfont={"color": p["muted"], "size": 12},
        )
    )
    table = {
        "columns": ["Step", "Finnish/Swedish/Sámi %", "Other/unknown %", "Gap (pts)", "Years", "Note"],
        "rows": [[f"{r['programme']}: {r['step'].lower()}", r["domestic_pct"], r["other_pct"], r["gap_pp"], r["years"],
                  r["note"] or "—"] for r in rows],
    }
    return fig, table
