"""12 pruebas sin llamadas a redes ni recursos ajenos al repositorio."""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from generar_datos import generar_datos
from src.analisis import X, Y, limpiar_datos, detectar_iqr, diagnostico, comparar_correlaciones

ROOT = Path(__file__).resolve().parents[1]


class TestCorrelaciones(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.crudo = pd.read_csv(ROOT / 'datos/transacciones_simuladas.csv')
        cls.limpio, cls.reporte = limpiar_datos(cls.crudo)
        cls.marcados, cls.iqr = detectar_iqr(cls.limpio)
        cls.tabla = comparar_correlaciones(cls.limpio)

    def test_01_reproducibilidad_semilla(self):
        pd.testing.assert_frame_equal(self.crudo, generar_datos(), check_dtype=False)

    def test_02_estructura_y_cantidad(self):
        self.assertEqual(len(self.crudo), 262)
        self.assertTrue({X, Y, 'canal', 'id_transaccion'}.issubset(self.crudo.columns))

    def test_03_deduplicacion_identificador(self):
        self.assertEqual(self.reporte['transacciones_duplicadas'], 2)
        self.assertFalse(self.limpio['id_transaccion'].duplicated().any())

    def test_04_nulos_criticos_controlados(self):
        self.assertEqual(self.reporte['nulos_criticos_despues_deduplicar'], 7)
        self.assertFalse(self.limpio[[X, Y]].isna().any().any())
        self.assertEqual(len(self.limpio), 253)

    def test_05_variable_de_fecha_parseada(self):
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.limpio['fecha_compra']))

    def test_06_iqr_y_13_registros(self):
        self.assertAlmostEqual(self.iqr['q1'], 84.0)
        self.assertAlmostEqual(self.iqr['q3'], 162.97)
        self.assertEqual(self.iqr['cantidad_marcados'], 13)

    def test_07_extremos_controlados(self):
        self.assertTrue({10008, 10096, 10209}.issubset(set(
            self.marcados.loc[self.marcados['es_outlier_iqr'], 'id_transaccion'])))

    def test_08_tres_coeficientes_finitos(self):
        self.assertEqual(set(self.tabla['metodo']), {'Pearson', 'Spearman', 'Kendall'})
        self.assertTrue(np.isfinite(self.tabla['todos_los_registros'].to_numpy()).all())

    def test_09_spearman_robusto_en_escenario(self):
        pearson = float(self.tabla.loc[self.tabla.metodo == 'Pearson', 'todos_los_registros'].iloc[0])
        spearman = float(self.tabla.loc[self.tabla.metodo == 'Spearman', 'todos_los_registros'].iloc[0])
        self.assertGreater(spearman, pearson + 0.3)

    def test_10_sensibilidad_pearson(self):
        fila = self.tabla.loc[self.tabla.metodo == 'Pearson'].iloc[0]
        self.assertGreater(fila['sin_marcados_iqr_solo_sensibilidad'], fila['todos_los_registros'] + .5)

    def test_11_diagnostico_normalidad(self):
        d = diagnostico(self.limpio)
        self.assertEqual(len(d), 2)
        self.assertTrue((d['shapiro_p'] < 0.05).all())

    def test_12_integridad_entrada_provoca_error(self):
        with self.assertRaisesRegex(ValueError, 'Faltan columnas'):
            limpiar_datos(self.crudo.drop(columns=[Y]))


if __name__ == '__main__':
    unittest.main()
