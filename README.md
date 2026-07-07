# Wine Quality Dashboard — Python

Dashboard interactivo sobre el dataset **Wine Quality (red)** de UCI,
separado en **backend** y **frontend**, ambos escritos enteramente en
Python (nada de HTML/CSS/JS sueltos).

```
wine-dashboard/
├── backend/
│   ├── main.py            # FastAPI: carga el CSV y expone endpoints JSON
│   └── requirements.txt
├── frontend/
│   ├── app.py              # Dash: construye la UI y llama al backend por HTTP
│   └── requirements.txt
└── README.md
```

## Cómo se comunican

El **frontend (Dash)** no calcula ni filtra nada por su cuenta: cada vez
que cambias un control, `app.py` hace una petición HTTP (con `requests`)
al **backend (FastAPI)**, que es quien tiene el DataFrame cargado y quien
hace los cálculos. El frontend solo arma la interfaz y dibuja lo que
recibe con Plotly.

```
[Dash: app.py]  --requests.get()-->  [FastAPI: main.py]  --pandas-->  CSV (UCI)
      |<------------- JSON -------------------|
```

## 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Verifica que responde en `http://localhost:8000/api/health`. Al arrancar
descarga el CSV directamente desde el repositorio UCI, así que necesita
conexión a internet.

Endpoints disponibles:

| Endpoint                              | Descripción                                        |
|----------------------------------------|-----------------------------------------------------|
| `GET /api/health`                      | Estado del servicio                                 |
| `GET /api/meta`                        | Features disponibles, rango de calidad, nº de filas |
| `GET /api/kpis?quality=N`              | Indicadores resumen filtrados por calidad ≥ N       |
| `GET /api/histogram?feature=X`         | Valores de una característica para el histograma    |
| `GET /api/boxplot?feature=X&quality=N` | Valores filtrados para el boxplot                   |
| `GET /api/scatter`                     | Alcohol vs. calidad                                 |
| `GET /api/correlation`                 | Matriz de correlación completa                      |

## 2. Frontend (Dash)

**Con el backend ya corriendo** en otra terminal:

```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre `http://localhost:8050`. Si el backend está en otra URL o puerto,
cambia la constante `API_BASE` al inicio de `app.py`.

## 3. Qué muestra el dashboard

- **Filtros**: característica fisicoquímica a analizar y umbral mínimo
  de calidad (deslizador).
- **Indicadores**: total de muestras, calidad promedio, alcohol
  promedio y % de vinos que cumplen el umbral seleccionado.
- **Histograma**: distribución de la característica elegida.
- **Boxplot**: la misma característica, filtrada por el umbral de
  calidad.
- **Dispersión**: alcohol vs. calidad, coloreado por calidad (estático).
- **Mapa de correlación**: correlación entre todas las variables
  numéricas del dataset (estático).

## Notas

- CORS en el backend está abierto (`allow_origins=["*"]`) para
  simplificar el desarrollo local; en producción conviene restringirlo.
- Si cambias el orden de arranque (frontend antes que backend), `app.py`
  fallará al pedir `/api/meta` al importar el módulo — arranca siempre
  primero el backend.
