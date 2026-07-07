"""
Wine Quality Dashboard — Frontend (100% Python, Dash)
======================================================
Este frontend NO calcula nada por su cuenta: para cada dato que
muestra, hace una petición HTTP al backend FastAPI (ver ../backend/main.py)
y solo se encarga de construir la interfaz y los gráficos con Plotly.

Requiere que el backend esté corriendo en API_BASE antes de arrancar.

Run con:
    pip install -r requirements.txt
    python app.py
"""

import requests
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

API_BASE = "http://127.0.0.1:8000"

# ---------------------------------------------------------------------
# Tema visual (paleta inspirada en una etiqueta de vino)
# ---------------------------------------------------------------------
COLORS = {
    "bg": "#1b2a20",
    "bg_panel": "#223327",
    "gold": "#c9a44c",
    "gold_soft": "#e3c98a",
    "burgundy": "#8c2f45",
    "cream": "#f1eae0",
    "muted": "#9fb0a2",
    "border": "rgba(201,164,76,0.25)",
}

FONT_DISPLAY = "Georgia, 'Times New Roman', serif"
FONT_BODY = "'Segoe UI', Arial, sans-serif"
FONT_MONO = "'Consolas', 'Courier New', monospace"

PANEL_STYLE = {
    "backgroundColor": COLORS["bg_panel"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "4px",
    "padding": "20px",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["cream"], family=FONT_BODY, size=12),
    margin=dict(t=10, r=10, b=40, l=48),
    xaxis=dict(gridcolor="rgba(201,164,76,0.12)", zerolinecolor="rgba(201,164,76,0.2)"),
    yaxis=dict(gridcolor="rgba(201,164,76,0.12)", zerolinecolor="rgba(201,164,76,0.2)"),
)


# ---------------------------------------------------------------------
# Llamadas al backend
# ---------------------------------------------------------------------
def api_get(path: str, params: dict | None = None) -> dict:
    resp = requests.get(f"{API_BASE}{path}", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


# Datos que no dependen de los filtros: se piden una sola vez al arrancar.
meta = api_get("/api/meta")
scatter_data = api_get("/api/scatter")
corr_data = api_get("/api/correlation")

FEATURES = meta["features"]
QUALITY_MIN = meta["quality_min"]
QUALITY_MAX = meta["quality_max"]
QUALITY_DEFAULT = meta["quality_default"]
DEFAULT_FEATURE = "alcohol" if "alcohol" in FEATURES else FEATURES[0]


# ---------------------------------------------------------------------
# Figuras estáticas (no cambian con los filtros)
# ---------------------------------------------------------------------
def build_scatter_figure() -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=scatter_data["alcohol"],
            y=scatter_data["quality"],
            mode="markers",
            marker=dict(
                color=scatter_data["quality"],
                colorscale=[[0, COLORS["gold_soft"]], [1, COLORS["burgundy"]]],
                size=6,
                opacity=0.65,
            ),
        )
    )
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="alcohol (% vol)", yaxis_title="calidad")
    return fig


def build_correlation_figure() -> go.Figure:
    fig = go.Figure(
        go.Heatmap(
            z=corr_data["matrix"],
            x=corr_data["columns"],
            y=corr_data["columns"],
            zmin=-1,
            zmax=1,
            colorscale=[[0, COLORS["burgundy"]], [0.5, COLORS["bg_panel"]], [1, COLORS["gold"]]],
            colorbar=dict(thickness=12, outlinewidth=0),
        )
    )
    layout = {**PLOTLY_LAYOUT, "margin": dict(t=10, r=10, b=90, l=90)}
    fig.update_layout(**layout, xaxis_tickangle=-45)
    return fig


# ---------------------------------------------------------------------
# App Dash
# ---------------------------------------------------------------------
app = Dash(__name__)
app.title = "Wine Quality Dashboard"


def kpi_card(label: str, value_id: str, accent: bool = False) -> html.Div:
    style = dict(PANEL_STYLE)
    if accent:
        style = {**style, "borderColor": "rgba(140,47,69,0.45)"}
    return html.Div(
        [
            html.P(label, style={
                "margin": "0 0 8px", "fontSize": "11px", "letterSpacing": "0.08em",
                "textTransform": "uppercase", "color": COLORS["muted"],
            }),
            html.P(id=value_id, style={
                "margin": 0, "fontSize": "28px", "fontFamily": FONT_MONO,
                "color": COLORS["gold_soft"],
            }),
        ],
        style={**style, "flex": "1"},
    )


app.layout = html.Div(
    style={
        "backgroundColor": COLORS["bg"],
        "color": COLORS["cream"],
        "fontFamily": FONT_BODY,
        "minHeight": "100vh",
        "padding": "0 0 40px",
    },
    children=[

        # ---------- Encabezado ----------
        html.Div(
            style={
                "textAlign": "center", "padding": "48px 24px 28px",
                "borderBottom": f"1px solid {COLORS['border']}",
            },
            children=[
                html.P("PANEL ANALÍTICO INTERACTIVO", style={
                    "margin": "0 0 6px", "fontFamily": FONT_MONO, "fontSize": "11px",
                    "letterSpacing": "0.18em", "color": COLORS["gold"],
                }),
                html.H1("Wine Quality", style={
                    "margin": 0, "fontFamily": FONT_DISPLAY, "fontStyle": "italic",
                    "fontSize": "3rem", "color": COLORS["cream"],
                }),
                html.P("Fisicoquímica del vino tinto y su relación con la calidad", style={
                    "margin": "10px auto 4px", "maxWidth": "520px", "color": COLORS["muted"],
                }),
                html.P(f"Dataset: UCI Wine Quality (red) · {meta['n_rows']} muestras", style={
                    "margin": 0, "fontSize": "12px", "color": COLORS["muted"], "opacity": 0.7,
                }),
            ],
        ),

        html.Div(
            style={"maxWidth": "1120px", "margin": "0 auto", "padding": "32px 24px 0"},
            children=[

                # ---------- Controles ----------
                html.Div(
                    style={**PANEL_STYLE, "display": "flex", "gap": "32px",
                           "flexWrap": "wrap", "alignItems": "flex-end", "marginBottom": "28px"},
                    children=[
                        html.Div(
                            style={"flex": "1", "minWidth": "220px"},
                            children=[
                                html.Label("Característica", style={
                                    "fontSize": "11px", "letterSpacing": "0.1em",
                                    "textTransform": "uppercase", "color": COLORS["muted"],
                                }),
                                dcc.Dropdown(
                                    id="feature-select",
                                    options=[{"label": f, "value": f} for f in FEATURES],
                                    value=DEFAULT_FEATURE,
                                    clearable=False,
                                    style={"marginTop": "8px", "color": "#1b2a20"},
                                ),
                            ],
                        ),
                        html.Div(
                            style={"flex": "2", "minWidth": "320px"},
                            children=[
                                html.Label(id="quality-label", style={
                                    "fontSize": "11px", "letterSpacing": "0.1em",
                                    "textTransform": "uppercase", "color": COLORS["muted"],
                                }),
                                dcc.Slider(
                                    id="quality-slider",
                                    min=QUALITY_MIN,
                                    max=QUALITY_MAX,
                                    step=1,
                                    value=QUALITY_DEFAULT,
                                    marks={i: str(i) for i in range(QUALITY_MIN, QUALITY_MAX + 1)},
                                    tooltip={"placement": "bottom", "always_visible": False},
                                ),
                            ],
                        ),
                    ],
                ),

                # ---------- KPIs ----------
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)",
                           "gap": "16px", "marginBottom": "28px"},
                    children=[
                        kpi_card("Muestras totales", "kpi-total"),
                        kpi_card("Calidad promedio", "kpi-avg-quality"),
                        kpi_card("Alcohol promedio", "kpi-avg-alcohol"),
                        kpi_card("Cumplen el umbral", "kpi-pct", accent=True),
                    ],
                ),

                # ---------- Gráficos ----------
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                    children=[
                        html.Div(style=PANEL_STYLE, children=[
                            html.H2("Distribución", style={"fontFamily": FONT_DISPLAY, "margin": "0 0 2px"}),
                            html.P("Histograma de la característica seleccionada",
                                   style={"fontSize": "12.5px", "color": COLORS["muted"], "margin": "0 0 8px"}),
                            dcc.Graph(id="hist-graph", config={"displayModeBar": False}),
                        ]),
                        html.Div(style=PANEL_STYLE, children=[
                            html.H2("Comparación por umbral", style={"fontFamily": FONT_DISPLAY, "margin": "0 0 2px"}),
                            html.P("Diagrama de caja para calidad ≥ umbral",
                                   style={"fontSize": "12.5px", "color": COLORS["muted"], "margin": "0 0 8px"}),
                            dcc.Graph(id="box-graph", config={"displayModeBar": False}),
                        ]),
                        html.Div(style=PANEL_STYLE, children=[
                            html.H2("Alcohol vs. calidad", style={"fontFamily": FONT_DISPLAY, "margin": "0 0 2px"}),
                            html.P("Relación entre grado alcohólico y calidad percibida",
                                   style={"fontSize": "12.5px", "color": COLORS["muted"], "margin": "0 0 8px"}),
                            dcc.Graph(id="scatter-graph", figure=build_scatter_figure(),
                                       config={"displayModeBar": False}),
                        ]),
                        html.Div(style=PANEL_STYLE, children=[
                            html.H2("Mapa de correlación", style={"fontFamily": FONT_DISPLAY, "margin": "0 0 2px"}),
                            html.P("Correlación entre todas las variables fisicoquímicas",
                                   style={"fontSize": "12.5px", "color": COLORS["muted"], "margin": "0 0 8px"}),
                            dcc.Graph(id="corr-graph", figure=build_correlation_figure(),
                                       config={"displayModeBar": False}),
                        ]),
                    ],
                ),
            ],
        ),

        html.P("Frontend: Dash (Python) · Backend: FastAPI (Python) · Gráficos: Plotly", style={
            "textAlign": "center", "fontSize": "12px", "color": COLORS["muted"],
            "marginTop": "32px",
        }),
    ],
)


# ---------------------------------------------------------------------
# Callbacks — cada uno consulta al backend en el momento en que
# cambia un filtro, en vez de recalcular nada localmente.
# ---------------------------------------------------------------------
@app.callback(Output("quality-label", "children"), Input("quality-slider", "value"))
def update_quality_label(quality):
    return f"Calidad mínima: {quality}"


@app.callback(
    Output("kpi-total", "children"),
    Output("kpi-avg-quality", "children"),
    Output("kpi-avg-alcohol", "children"),
    Output("kpi-pct", "children"),
    Input("quality-slider", "value"),
)
def update_kpis(quality):
    data = api_get("/api/kpis", params={"quality": quality})
    return (
        f"{data['total_wines']:,}",
        f"{data['avg_quality']:.2f}",
        f"{data['avg_alcohol']:.2f}% vol",
        f"{data['pct_at_or_above']}%",
    )


@app.callback(Output("hist-graph", "figure"), Input("feature-select", "value"))
def update_histogram(feature):
    data = api_get("/api/histogram", params={"feature": feature})
    fig = go.Figure(go.Histogram(x=data["values"], nbinsx=30, marker_color=COLORS["gold"]))
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title=feature, yaxis_title="frecuencia")
    return fig


@app.callback(
    Output("box-graph", "figure"),
    Input("feature-select", "value"),
    Input("quality-slider", "value"),
)
def update_boxplot(feature, quality):
    data = api_get("/api/boxplot", params={"feature": feature, "quality": quality})
    fig = go.Figure(go.Box(
        y=data["values"],
        name=f"calidad ≥ {quality}",
        marker_color=COLORS["burgundy"],
        line_color=COLORS["gold_soft"],
        boxmean=True,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, yaxis_title=feature, showlegend=False)
    return fig


if __name__ == "__main__":
    app.run(debug=True, port=8050)
