"""
Wine Quality Dashboard — Backend API
=====================================
FastAPI service that loads the UCI "Wine Quality (red)" dataset once at
startup and exposes small, purpose-built JSON endpoints for the frontend
to consume. All aggregation/filtering happens here so the frontend stays
a thin rendering layer.

Run with:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

DATA_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "wine-quality/winequality-red.csv"
)

app = FastAPI(title="Wine Quality Dashboard API", version="1.0.0")

# Allow the static frontend (served from any origin/port, e.g. file://
# or a local dev server) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Data loading (once, at process startup)
# ---------------------------------------------------------------------
df = pd.read_csv(DATA_URL, sep=";")
NUMERIC_FEATURES = [c for c in df.columns if c != "quality"]


def _validate_feature(feature: str) -> None:
    if feature not in NUMERIC_FEATURES:
        raise HTTPException(
            status_code=400,
            detail=f"'{feature}' no es una característica válida. "
                   f"Usa una de: {NUMERIC_FEATURES}",
        )


# ---------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok", "rows_loaded": int(len(df))}


@app.get("/api/meta")
def get_meta():
    """Everything the frontend needs to build its controls on load."""
    return {
        "features": NUMERIC_FEATURES,
        "quality_min": int(df["quality"].min()),
        "quality_max": int(df["quality"].max()),
        "quality_default": int(df["quality"].median()),
        "n_rows": int(len(df)),
    }


@app.get("/api/kpis")
def get_kpis(quality: int = Query(..., description="Umbral mínimo de calidad")):
    """Summary indicators for the KPI cards, recomputed for the current filter."""
    filtered = df[df["quality"] >= quality]
    return {
        "total_wines": int(len(df)),
        "filtered_wines": int(len(filtered)),
        "avg_quality": round(float(df["quality"].mean()), 2),
        "avg_alcohol": round(float(df["alcohol"].mean()), 2),
        "pct_at_or_above": round(100 * len(filtered) / len(df), 1) if len(df) else 0,
    }


@app.get("/api/histogram")
def get_histogram(feature: str = Query(...)):
    """Raw values for one feature — the frontend bins them client-side."""
    _validate_feature(feature)
    return {"feature": feature, "values": df[feature].round(4).tolist()}


@app.get("/api/boxplot")
def get_boxplot(feature: str = Query(...), quality: int = Query(...)):
    """Values for one feature, filtered to quality >= threshold."""
    _validate_feature(feature)
    filtered = df[df["quality"] >= quality]
    return {
        "feature": feature,
        "quality_threshold": quality,
        "values": filtered[feature].round(4).tolist(),
        "n": int(len(filtered)),
    }


@app.get("/api/scatter")
def get_scatter():
    """Alcohol vs. quality, fixed pair used for the scatter panel."""
    return {
        "alcohol": df["alcohol"].round(4).tolist(),
        "quality": df["quality"].tolist(),
    }


@app.get("/api/correlation")
def get_correlation():
    """Full numeric correlation matrix for the heatmap panel."""
    corr = df.corr(numeric_only=True).round(3)
    return {
        "columns": corr.columns.tolist(),
        "matrix": corr.values.tolist(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
