"""Dashboard chart registry.

Add a chart = add one module in this folder with:

    CHART = {"title": "...", "subtitle": "...", "source": "...", "order": 30}
    def build(p: dict) -> tuple[go.Figure, dict]:
        fig = new_figure(p)          # themed, transparent, Silta fonts
        ...                          # use p["lake"], p["coral"], ... never raw hex
        return fig, {"columns": [...], "rows": [[...], ...]}   # the data-table view

`build` runs once per theme (light and dark) so each mode gets its own validated
colors. Data files live in content/data/ (read them with app.content.data_path).
Modules whose name starts with `_` are skipped.
"""

from __future__ import annotations

import csv
import importlib
import pkgutil
from dataclasses import dataclass
from typing import Callable

import plotly.graph_objects as go

from app import content

# Chart colors are validated (dataviz validate_palette.js: lightness band, chroma,
# CVD and normal-vision separation, 3:1 contrast) against each mode's card surface.
# `lake` = series 1 (reference group), `coral` = series 2 (the group Silta serves).
THEMES: dict[str, dict[str, str]] = {
    "light": {
        "lake": "#1769a8",
        "coral": "#c2512f",
        "reference": "#9aa6ad",
        "ink": "#142028",
        "muted": "#56636b",
        "line": "#e3e8e5",
        "surface": "#ffffff",
    },
    "dark": {
        "lake": "#3896d8",
        "coral": "#dc6a3c",
        "reference": "#5d6c73",
        "ink": "#e5ecef",
        "muted": "#98a7ae",
        "line": "#27363d",
        "surface": "#162026",
    },
}

FONT = '"Atkinson Hyperlegible", Verdana, system-ui, sans-serif'
CONFIG = {"displaylogo": False, "responsive": True, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}


def new_figure(p: dict, **layout) -> go.Figure:
    axis = {
        "automargin": True,
        "gridcolor": p["line"],
        "linecolor": p["line"],
        "zeroline": False,
        "tickfont": {"color": p["muted"]},
        "title": {"font": {"color": p["muted"]}},
    }
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": FONT, "color": p["ink"], "size": 13},
        margin={"l": 8, "r": 16, "t": 8, "b": 8},
        hoverlabel={"bgcolor": p["surface"], "bordercolor": p["line"], "font": {"color": p["ink"], "family": FONT}},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0, "font": {"color": p["muted"]}},
        xaxis=axis,
        yaxis=axis,
        bargap=0.3,
        bargroupgap=0.08,
    )
    if layout:
        fig.update_layout(**layout)
    return fig


def read_csv(name: str) -> list[dict]:
    with content.data_path(name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass
class Chart:
    id: str
    title: str
    subtitle: str
    source: str
    order: int
    height: int
    wide: bool
    build: Callable[[dict], tuple[go.Figure, dict]]

    def render(self) -> dict:
        figures, table = {}, {"columns": [], "rows": []}
        for theme, palette in THEMES.items():
            fig, built_table = self.build(palette)
            fig.update_layout(height=self.height)
            figures[theme] = fig.to_json()
            if theme == "light":
                table = built_table
        return {"chart": self, "figures": figures, "table": table}


def discover() -> list[Chart]:
    charts = []
    for module_info in pkgutil.iter_modules(__path__):
        if module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{module_info.name}")
        meta = getattr(module, "CHART", None)
        if meta is None or not hasattr(module, "build"):
            continue
        charts.append(
            Chart(
                id=module_info.name,
                title=meta["title"],
                subtitle=meta.get("subtitle", ""),
                source=meta.get("source", ""),
                order=int(meta.get("order", 100)),
                height=int(meta.get("height", 360)),
                wide=bool(meta.get("wide", False)),
                build=module.build,
            )
        )
    return sorted(charts, key=lambda c: (c.order, c.id))
