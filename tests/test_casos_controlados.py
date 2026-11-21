"""Pruebas unitarias para validar las reglas de negocio y casos controlados."""
import unittest
from datetime import date
from src.data_loader import calcular_importe_cop
from src.validador import validar_casos_controlados

class TestCasosControlados(unittest.TestCase):

    def test_casos_controlados_json(self):
        """Verifica que todos los casos controlados de Casos_controlados.json pasen."""
        resultados = validar_casos_controlados()
        for res in resultados:
            with self.subTest(caso=res["caso"]):
                self.assertTrue(res["aprobado"], f"Falló el caso {res['caso']}: {res}")

    def test_calculo_cop_directo(self):
        venta = {
            "estado": "Confirmada",
            "cantidad": "2",
            "precio_unitario": "100000",
            "descuento_pct": "10",
            "moneda": "COP",
            "fecha": "2026-05-01"
        }
        res = calcular_importe_cop(venta, {})
        self.assertEqual(res, 180000.0)

    def test_calculo_usd_conversion(self):
        venta = {
            "estado": "Confirmada",
            "cantidad": "3",
            "precio_unitario": "100",
            "descuento_pct": "0",
            "moneda": "USD",
            "fecha": "2026-05-01"
        }
        rates = {"2026-05-01": 4000.0}
        res = calcular_importe_cop(venta, rates)
        self.assertEqual(res, 1200000.0)

    def test_venta_anulada_retorna_cero(self):
        venta = {
            "estado": "Anulada",
            "cantidad": "5",
            "precio_unitario": "200000",
            "descuento_pct": "0",
            "moneda": "COP",
            "fecha": "2026-05-01"
        }
        res = calcular_importe_cop(venta, {})
        self.assertEqual(res, 0.0)

if __name__ == "__main__":
    unittest.main()
