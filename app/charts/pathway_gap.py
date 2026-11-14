"""Gap at each step of the screening pathway (other-language minus domestic, percentage points)."""

import plotly.graph_objects as go

from app.charts import new_figure, read_csv

CHART = {
    "title": "Gap at each step, other-language minus domestic (percentage points)",
    "subtitle": "The large gap is at attendance. Follow-up is about equal, except colonoscopy after a positive colorectal test.",
    "source": "Finnish Cancer Registry native-language tables 2022–2024 (brain: sources/2026-11-14-cancerregistry-screening-by-language.md)",
    "order": 20,
    "height": 330,
}

VERDICT = {"gap": "Gap", "none": "No gap", "unclear": "Unclear meaning"}
SHORT = {
    "Attended screening": "attended",
    "Referred on after further exams": "referred on",
    "Attended colposcopy after referral": "colposcopy",
    "Colonoscopy after positive test": "colonoscopy",
}


def _fmt(v: float) -> str:
    return f"{v:+.1f}".replace("-", "−")


def build(p: dict):
    rows = read_csv("gap_by_step.csv")
    labels = [f"{r['programme']}: {r['step'].lower()}" for r in rows]
    # Short two-line axis labels so the bars keep their width on a phone; full step text is in hover and table.
    ticks = [f"{r['programme']}<br>{SHORT[r['step']]}" for r in rows]
    gaps = [float(r["gap_pp"]) for r in rows]
    lows = [float(r["ci_low"]) for r in rows]
    highs = [float(r["ci_high"]) for r in rows]
    colors = [p["coral"] if r["verdict"] == "gap" else p["reference"] for r in rows]
    # Plotly draws horizontal categories bottom-up; reverse so the pathway reads top-down.
    rev = lambda xs: xs[::-1]  # noqa: E731
    fig = new_figure(
        p,
        showlegend=False,
        xaxis={"range": [-27, 7], "ticksuffix": " pp",
               "title": {"text": "Difference from Finnish/Swedish speakers", "font": {"color": p["muted"], "size": 13}}, "gridcolor": p["line"], "zeroline": True,
               "zerolinecolor": p["muted"], "zerolinewidth": 1, "tickfont": {"color": p["muted"]}},
        yaxis={"tickfont": {"color": p["ink"]}, "automargin": True, "gridcolor": "rgba(0,0,0,0)"},
        margin={"l": 8, "r": 16, "t": 8, "b": 8},
    )
    fig.add_trace(
        go.Bar(
            x=rev(gaps),
            y=rev(ticks),
            orientation="h",
            marker={"color": rev(colors), "cornerradius": 4, "line": {"width": 0}},
            error_x={"type": "data", "symmetric": False, "color": p["muted"], "thickness": 1.2, "width": 4,
                     "array": rev([h - g for g, h in zip(gaps, highs)]),
                     "arrayminus": rev([g - lo for g, lo in zip(gaps, lows)])},
            text=rev([_fmt(g) for g in gaps]),
            # Big gaps: label inside the bar tip, clear of the CI whisker; small bars: label outside.
            textposition=rev(["inside" if r["verdict"] == "gap" else "outside" for r in rows]),
            insidetextanchor="end",
            insidetextfont={"color": p["surface"], "size": 12},
            outsidetextfont={"color": p["ink"], "size": 12},
            cliponaxis=False,
            customdata=rev([[VERDICT[r["verdict"]], r["years"], f"{float(r['ci_low']):.1f} to {float(r['ci_high']):.1f}",
                             int(r["other_n"]), label] for r, label in zip(rows, labels)]),
            hovertemplate="<b>%{customdata[4]}</b><br>%{x:+.1f} pp · %{customdata[0]}<br>95% CI %{customdata[2]}"
                          "<br>%{customdata[1]} · %{customdata[3]:,} other-language people<extra></extra>",
        )
    )
    table = {
        "columns": ["Step", "Domestic %", "Other %", "Gap (pp)", "95% CI", "Years", "Verdict"],
        "rows": [[label, r["domestic_pct"] or "—", r["other_pct"] or "—", r["gap_pp"],
                  f"{r['ci_low']} to {r['ci_high']}", r["years"], VERDICT[r["verdict"]]]
                 for label, r in zip(labels, rows)],
    }
    return fig, table
