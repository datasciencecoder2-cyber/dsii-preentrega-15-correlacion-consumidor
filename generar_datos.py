"""Genera un conjunto sintético, reproducible, de pedidos de e-commerce.

Ningún dato pertenece a compradores reales. Las compras extremas de las filas
10008, 10096 y 10209 se insertan deliberadamente para estudiar sensibilidad.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261031
N_CLIENTES = 260


def generar_datos() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    sesiones = rng.poisson(7, N_CLIENTES) + 1
    refuerzo = rng.random(N_CLIENTES) < 0.12
    sesiones[refuerzo] += rng.integers(5, 17, refuerzo.sum())

    gasto = 15 + 10 * sesiones + 1.2 * np.power(sesiones, 1.35)
    gasto = np.clip(gasto + rng.normal(0, 24, N_CLIENTES), 10, None).round(2)

    # Valores deliberadamente extremos, que NO representan errores confirmados.
    for fila, monto, visitas in [(7, 950.0, 3), (95, 1450.0, 5), (208, 2100.0, 2)]:
        gasto[fila] = monto
        sesiones[fila] = visitas

    fechas = pd.date_range('2026-01-01', '2026-09-30')
    canales = rng.choice(['Web', 'App movil'], N_CLIENTES, p=[0.55, 0.45])
    metodos = rng.choice(['Tarjeta', 'Transferencia', 'Billetera digital'],
                         N_CLIENTES, p=[0.45, 0.15, 0.40])
    antiguedad = rng.integers(35, 1400, size=N_CLIENTES)
    productos = np.maximum(1, np.floor(gasto / 65).astype(int))

    tabla = pd.DataFrame({
        'id_transaccion': np.arange(10001, 10001 + N_CLIENTES),
        'cliente_id': np.arange(20001, 20001 + N_CLIENTES),
        'fecha_compra': pd.to_datetime(rng.choice(fechas, N_CLIENTES)).strftime('%Y-%m-%d'),
        'sesiones_30d': sesiones.astype(float),
        'importe_compra_usd': gasto,
        'antiguedad_cliente_dias': antiguedad,
        'productos_comprados': productos,
        'canal': canales,
        'medio_pago': metodos,
    })

    # Siete faltantes en variables críticas (cuatro montos, tres sesiones).
    tabla.loc[[25, 143, 234, 242], 'importe_compra_usd'] = np.nan
    tabla.loc[[35, 134, 200], 'sesiones_30d'] = np.nan

    # Dos transacciones duplicadas; el análisis exige una fila por operación.
    return pd.concat([tabla, tabla.loc[[18, 61]]], ignore_index=True)


if __name__ == '__main__':
    archivo = Path(__file__).resolve().parent / 'datos' / 'transacciones_simuladas.csv'
    archivo.parent.mkdir(exist_ok=True)
    tabla = generar_datos()
    tabla.to_csv(archivo, index=False, encoding='utf-8')
    print(f'Dataset sintético reproducible: {len(tabla)} filas -> {archivo}')
