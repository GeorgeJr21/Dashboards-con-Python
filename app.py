import pandas as pd
from sklearn.preprocessing import StandardScaler
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
df = pd.read_csv(url, sep=';')

scaler = StandardScaler()
num_cols = df.columns[:-1]
df[num_cols] = scaler.fit_transform(df[num_cols])

app = Dash(__name__)

app.layout = html.Div([

    html.H2("Universidad Tecnológica de Panamá",
            style={'textAlign': 'center'}),

    html.H3("Análisis de Datos y Toma de Decisiones en Computación",
            style={'textAlign': 'center'}),

    html.H4("Tarea #3 - Dashboard en Python",
            style={'textAlign': 'center'}),

    html.Hr(),

    html.H4("Integrantes:", style={'marginTop': '20px'}),

    html.Ul([
        html.Li("Jorge Rodas"),
        html.Li("Emily Morales"),
        html.Li("Ester Garcia"),
    ]),

    html.Hr(),

    html.H1("Wine Quality Dashboard",
            style={'textAlign': 'center'}
    ),
    dcc.Dropdown(
        id="feature",
        options=[{"label": c, "value": c} for c in num_cols],
        value="alcohol"
    ),
    dcc.Slider(
        id="quality",
        min=int(df["quality"].min()),
        max=int(df["quality"].max()),
        step=1,
        value=int(df["quality"].median())
    ),
    dcc.Graph(id="hist"),
    dcc.Graph(id="box"),
    dcc.Graph(
        figure=px.scatter(df, x="alcohol", y="quality",
                          title="Alcohol vs Calidad")
    ),
    dcc.Graph(
        figure=px.imshow(df.corr(numeric_only=True),
                         title="Mapa de Correlación")
    )
])

@app.callback(
    Output("hist", "figure"),
    Input("feature", "value")
)
def update_hist(feature):
    return px.histogram(df, x=feature, title=f"Distribución de {feature}")

@app.callback(
    Output("box", "figure"),
    [Input("feature", "value"),
     Input("quality", "value")]
)
def update_box(feature, quality):
    temp = df[df["quality"] >= quality]
    return px.box(temp, y=feature, title=f"{feature} para calidad >= {quality}")

if __name__ == "__main__":
    app.run(debug=True)