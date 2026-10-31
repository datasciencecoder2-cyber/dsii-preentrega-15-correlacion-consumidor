# Data Science II · Pre-entrega 15

## Análisis de correlación — comportamiento del consumidor

**Pregunta de negocio:** entre clientes que realizaron una compra, ¿más sesiones en el sitio durante los últimos 30 días se asocian con un importe mayor de su pedido?

La entrega compara **Pearson, Spearman y Kendall** en un dataset **100 % sintético** de e-commerce. Incluye diagnóstico visual y estadístico de distribuciones, análisis de valores extremos, tres matrices de correlación, interpretación de negocio y una discusión explícita de causalidad.

> **Advertencia de procedencia:** los registros son simulados localmente con semilla fija `20261031`; no contienen datos de personas reales ni son una muestra representativa. Las transacciones `10008`, `10096` y `10209` incluyen montos altos creados deliberadamente como prueba de sensibilidad a outliers. Las relaciones no pueden generalizarse a clientes reales.

## Estructura

```text
.
├── notebooks/
│   └── preentrega_15_correlacion_consumidor.ipynb  # Notebook ejecutado, outputs visibles
├── datos/
│   └── transacciones_simuladas.csv                 # Datos sintéticos de entrada
├── graficos/                                      # Gráficos exportados como PNG
├── resultados/                                    # Tablas CSV y resumen JSON
├── evidencia/                                     # Registro de validación
├── src/
│   └── analisis.py                                # Limpieza, IQR y coeficientes
├── tests/
│   └── test_analisis.py                            # Tests de cálculo y reproducibilidad
├── generar_datos.py                               # Regenerar el CSV con semilla fija
├── ejecutar.py                                    # Ejecutar y guardar notebook
├── requirements.txt
├── .gitignore
└── README.md
```

## Requisitos

- Python 3.11 o superior.
- Dependencias de `requirements.txt`.
- No se requieren credenciales ni acceso a Internet para reproducir el análisis: se incluye el CSV local.

## Pasos para ejecutar

Desde la carpeta raíz del proyecto:

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py ejecutar.py
```

Abrí `notebooks/preentrega_15_correlacion_consumidor.ipynb` con JupyterLab, VS Code o el visor de GitHub. **El notebook subido ya conserva sus resultados de ejecución**.

Para reconstruir los datos desde cero, antes del notebook ejecutá `py generar_datos.py`. Es un procedimiento opcional y determinista.

## Datos, unidad de análisis y limpieza

- Una transacción por cliente. Cada fila expresa un pedido y las sesiones previas de su cliente.
- Entrada: **262 filas** (260 clientes más 2 duplicados). Una vez eliminados los duplicados por `id_transaccion` y descartadas 7 filas con nulos en las variables analizadas, quedan **253 observaciones**.
- El diccionario de variables y las razones de limpieza aparecen dentro del notebook.
- La variable `importe_compra_usd` está en USD simulados; no existe una conversión monetaria externa.

## Resultados principales

Correlación entre `sesiones_30d` e `importe_compra_usd`:

| Método | Dataset analizado, n=253 | Excluyendo 13 outliers IQR (sensibilidad), n=240 |
|---|---:|---:|
| Pearson | 0.231 | 0.896 |
| Spearman | 0.828 | 0.876 |
| Kendall tau-b | 0.698 | 0.716 |

**Conclusión principal:** para este dataset artificial sesgado y con observaciones monetarias extremas, **Spearman** es el coeficiente descriptivo principal: cuantifica la asociación monótona por rangos con menor influencia de la magnitud de esos extremos. **Kendall tau-b** ofrece contraste de concordancia y maneja empates; **Pearson** se informa para evaluar asociación lineal y su sensibilidad. Los valores de los tres coeficientes no se comparan como si midieran exactamente la misma magnitud.

**IQR:** `Q1=84.00`, `Q3=162.97`, `IQR=78.97`; límite superior `281.425` y **13 operaciones señaladas**. Estar fuera de los límites es una **alerta de inspección**, no una prueba de fraude o error. Se mantiene el conjunto completo para la conclusión principal; la exclusión de valores señalados se usa **solo como análisis de sensibilidad**, no como limpieza definitiva.

### Interpretación para negocio

En estas transacciones simuladas, los clientes con mayor actividad digital tienden a presentar pedidos de mayor importe **en términos de ordenamiento**, pero hay compradores con pocas sesiones y compras excepcionales. No corresponde suponer que incrementar sesiones *cause* compras mayores: podrían influir promociones, ticket esperado, categoría, ingresos, campañas y selección de clientes que ya compraron.

**Acción recomendada:** usar Spearman y Kendall como diagnóstico inicial para segmentar sesiones/gasto y auditar compras extremas antes de diseñar un experimento o modelo. No tomar decisiones reales sobre compradores a partir de estos datos simulados.

## Alcances y limitaciones

- La normalidad de las variables no es requisito estricto para **calcular** Pearson; afecta especialmente algunos procedimientos inferenciales. Para la elección descriptiva también importan linealidad, monotonicidad y valores influyentes.
- `Shapiro-Wilk` se muestra como una indicación de incompatibilidad con una distribución normal, no como prueba de causalidad ni criterio único de selección.
- Al existir frecuencias discretas y empates en sesiones, se usa tau-b de Kendall (vía `pandas.corr(method='kendall')`).
- `productos_comprados` se construye a partir de `importe_compra_usd` en la simulación; no debe interpretarse su correlación como relación independiente ni utilizarse como predictor sin revisar temporalidad y filtración de datos.
- Las comparaciones antes/después de excluir valores IQR son descriptivas: no confirman que esas observaciones sean errores.

## Checklist de la consigna

- [x] Notebook `.ipynb` ejecutable con resultados visibles.
- [x] Pearson, Spearman y Kendall para el mismo par y matrices para variables numéricas.
- [x] Histogramas, boxplot, scatter, heatmaps y análisis de sensibilidad.
- [x] Diagnóstico de supuestos, sesgo y outliers; Shapiro-Wilk y cuantiles IQR.
- [x] Conclusión de negocio, decisión metodológica y correlación ≠ causalidad.
- [x] Datos, README, generación y tests reproducibles.
