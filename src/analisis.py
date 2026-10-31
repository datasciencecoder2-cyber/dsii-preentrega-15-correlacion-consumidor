"""Limpieza, pruebas de supuestos y análisis de correlación."""

import pandas as pd
from scipy.stats import shapiro

X = 'sesiones_30d'
Y = 'importe_compra_usd'
NUMERICAS = [X, Y, 'antiguedad_cliente_dias', 'productos_comprados']
REQUERIDAS = ['id_transaccion', 'cliente_id', 'fecha_compra', X, Y,
              'antiguedad_cliente_dias', 'productos_comprados', 'canal', 'medio_pago']


def limpiar_datos(datos: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    faltan = sorted(set(REQUERIDAS) - set(datos.columns))
    if faltan:
        raise ValueError(f'Faltan columnas obligatorias: {faltan}')
    crudo = datos.copy()
    duplicados = int(crudo['id_transaccion'].duplicated().sum())
    if crudo['id_transaccion'].isna().any():
        raise ValueError('id_transaccion no puede tener nulos')
    crudo = crudo.drop_duplicates(subset='id_transaccion').copy()
    for nombre in NUMERICAS:
        crudo[nombre] = pd.to_numeric(crudo[nombre], errors='coerce')
    crudo['fecha_compra'] = pd.to_datetime(crudo['fecha_compra'], errors='coerce')
    nulos_criticos = int(crudo[[X, Y]].isna().any(axis=1).sum())
    fechas_invalidas = int(crudo['fecha_compra'].isna().sum())
    validos = crudo.dropna(subset=[X, Y, 'fecha_compra']).copy()
    validos = validos[(validos[X] >= 0) & (validos[Y] >= 0)].copy()
    validos = validos.sort_values('id_transaccion').reset_index(drop=True)
    reporte = {
        'filas_crudas': len(datos),
        'transacciones_duplicadas': duplicados,
        'nulos_criticos_despues_deduplicar': nulos_criticos,
        'fechas_invalidas': fechas_invalidas,
        'filas_analizadas': len(validos),
        'regla': 'una transacción por cliente; se descartan faltantes en las variables del par',
    }
    return validos, reporte


def detectar_iqr(datos: pd.DataFrame, variable: str = Y) -> tuple[pd.DataFrame, dict]:
    if variable not in datos or datos[variable].isna().any():
        raise ValueError(f'Variable inexistente o con nulos: {variable}')
    q1, q3 = datos[variable].quantile([0.25, 0.75])
    iqr = q3 - q1
    inferior = q1 - 1.5 * iqr
    superior = q3 + 1.5 * iqr
    marcado = datos.copy()
    marcado['es_outlier_iqr'] = (marcado[variable] < inferior) | (marcado[variable] > superior)
    limites = {'q1': float(q1), 'q3': float(q3), 'iqr': float(iqr),
               'limite_inferior': float(inferior), 'limite_superior': float(superior),
               'cantidad_marcados': int(marcado['es_outlier_iqr'].sum())}
    return marcado, limites


def comparar_correlaciones(datos: pd.DataFrame) -> pd.DataFrame:
    marcado, _ = detectar_iqr(datos)
    completo = marcado
    sensibilidad = marcado.loc[~marcado['es_outlier_iqr']]
    resultados = []
    for metodo in ('pearson', 'spearman', 'kendall'):
        resultados.append({
            'metodo': metodo.capitalize(),
            'todos_los_registros': float(completo[X].corr(completo[Y], method=metodo)),
            'sin_marcados_iqr_solo_sensibilidad': float(sensibilidad[X].corr(
                sensibilidad[Y], method=metodo)),
        })
    return pd.DataFrame(resultados)


def diagnostico(datos: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for variable in (X, Y):
        serie = datos[variable].dropna()
        estadistico, p = shapiro(serie)
        filas.append({
            'variable': variable,
            'n': int(len(serie)),
            'media': float(serie.mean()),
            'mediana': float(serie.median()),
            'desviacion': float(serie.std()),
            'asimetria': float(serie.skew()),
            'curtosis_exceso': float(serie.kurt()),
            'shapiro_w': float(estadistico),
            'shapiro_p': float(p),
        })
    return pd.DataFrame(filas)
