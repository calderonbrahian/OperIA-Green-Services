"""Pruebas de las reglas de negocio de OperIA: semáforo, cobertura, prioridad, no-fuga y datos oficiales."""
import csv
import json
import unittest
from datetime import date, timedelta
from pathlib import Path

from src.config import OUTPUTS_DIR, DATA_RAW_DIR, verificar_datos_oficiales
from src.modelos_operativos import (
    ModeloClasificacionComercial, calcular_estado_cobertura, features_en_corte, ordenar_cartera,
    COB_PROXIMA, COB_VIGENTE, COB_VENCIDA, COB_SIN, ESTADOS_COBERTURA,
    EST_FRIO, EST_FRECUENTE, EST_SEGUIMIENTO, EST_SIN_COMPRAS,
)

CORTE = date(2026, 10, 31)
REF = Path(__file__).resolve().parents[2] / "Green_Services_Recursos_de_Prueba" / "05_Validacion" / "Referencia_resumen_prueba.json"


def contrato(dias_fin, dias_inicio=-100):
    return {"fecha_inicio": str(CORTE + timedelta(days=dias_inicio)), "fecha_fin": str(CORTE + timedelta(days=dias_fin))}


class TestDatosOficiales(unittest.TestCase):
    def test_data_raw_es_el_paquete_oficial(self):
        self.assertEqual(verificar_datos_oficiales(DATA_RAW_DIR), [])

    @unittest.skipUnless(REF.exists(), "Referencia oficial no disponible")
    def test_cifras_coinciden_con_referencia_oficial(self):
        ref = json.loads(REF.read_text(encoding="utf-8"))
        cif = json.loads((OUTPUTS_DIR / "cifras_dashboard.json").read_text(encoding="utf-8"))
        self.assertEqual(cif["clientes_total"], ref["clientes"])
        self.assertEqual(cif["operaciones_confirmadas"], ref["transacciones_confirmadas"])
        self.assertEqual(cif["frios_regla_oficial"], ref["clientes_frios"])
        self.assertAlmostEqual(cif["ingreso_cop_total"], ref["ingreso_cop"], delta=0.05)


class TestCobertura(unittest.TestCase):
    def test_bordes_de_renovacion(self):
        self.assertEqual(calcular_estado_cobertura([contrato(0)], CORTE)[0], COB_PROXIMA)
        self.assertEqual(calcular_estado_cobertura([contrato(45)], CORTE)[0], COB_PROXIMA)
        self.assertEqual(calcular_estado_cobertura([contrato(46)], CORTE)[0], COB_VIGENTE)
        self.assertEqual(calcular_estado_cobertura([contrato(-1)], CORTE)[0], COB_VENCIDA)

    def test_sin_contratos_o_no_iniciados(self):
        self.assertEqual(calcular_estado_cobertura([], CORTE)[0], COB_SIN)
        futuro = contrato(200, dias_inicio=10)  # inicia después del corte
        self.assertEqual(calcular_estado_cobertura([futuro], CORTE)[0], COB_SIN)

    def test_un_contrato_vigente_evita_marcar_vencida(self):
        self.assertEqual(calcular_estado_cobertura([contrato(-30), contrato(200)], CORTE)[0], COB_VIGENTE)
        self.assertEqual(calcular_estado_cobertura([contrato(-30), contrato(10)], CORTE)[0], COB_PROXIMA)


class TestSemaforo(unittest.TestCase):
    def setUp(self):
        self.m = ModeloClasificacionComercial()

    def estado(self, dias, cob=COB_VIGENTE):
        return self.m.clasificar_cliente(dias, 5, cob)[0]

    def test_umbrales_de_recencia(self):
        self.assertEqual(self.estado(0), EST_FRECUENTE)
        self.assertEqual(self.estado(30), EST_FRECUENTE)
        self.assertEqual(self.estado(31), EST_SEGUIMIENTO)
        self.assertEqual(self.estado(89), EST_SEGUIMIENTO)
        self.assertEqual(self.estado(90), EST_FRIO)
        self.assertEqual(self.estado(None), EST_SIN_COMPRAS)

    def test_tabla_de_verdad_prioridad(self):
        esperado = {}
        for cob in ESTADOS_COBERTURA:
            req = cob in (COB_PROXIMA, COB_VENCIDA)
            esperado[(EST_FRIO, cob)] = "ALTA"
            esperado[(EST_FRECUENTE, cob)] = "MEDIA" if req else "BAJA"
            esperado[(EST_SEGUIMIENTO, cob)] = "MEDIA" if req else "NORMAL"
            esperado[(EST_SIN_COMPRAS, cob)] = "MEDIA" if req else "NORMAL"
        dias = {EST_FRIO: 120, EST_FRECUENTE: 5, EST_SEGUIMIENTO: 60, EST_SIN_COMPRAS: None}
        for (est, cob), prio in esperado.items():
            with self.subTest(estado=est, cobertura=cob):
                r = self.m.clasificar_cliente(dias[est], 5, cob)
                self.assertEqual((r[0], r[1]), (est, prio))

    def test_cobertura_vigente_nunca_es_media(self):
        for dias in (0, 15, 45, 80):
            self.assertNotEqual(self.m.clasificar_cliente(dias, 5, COB_VIGENTE)[1], "MEDIA")

    def test_el_criterio_explica_la_decision(self):
        crit = self.m.clasificar_cliente(0, 5, COB_PROXIMA)[3]
        self.assertIn("0 d", crit)
        self.assertIn(COB_PROXIMA, crit)


class TestOrdenYConsistencia(unittest.TestCase):
    def test_la_probabilidad_solo_ordena_dentro_de_la_prioridad(self):
        cartera = [
            {"id": "a", "prioridad": "BAJA", "prob": 99},
            {"id": "b", "prioridad": "ALTA", "prob": 10},
            {"id": "c", "prioridad": "ALTA", "prob": 80},
        ]
        self.assertEqual([c["id"] for c in ordenar_cartera(cartera)], ["c", "b", "a"])

    def test_vista_360_completa_y_consistente(self):
        with open(OUTPUTS_DIR / "vista_clientes_360.csv", encoding="utf-8-sig") as f:
            filas = list(csv.DictReader(f))
        with open(DATA_RAW_DIR / "clientes.csv", encoding="utf-8-sig") as f:
            ids = {r["cliente_id"] for r in csv.DictReader(f)}
        self.assertEqual({r["Cliente_ID"] for r in filas}, ids)  # ningún cliente se pierde
        m = ModeloClasificacionComercial()
        for r in filas:
            dias = int(r["Dias_Sin_Comprar"]) if r["Dias_Sin_Comprar"] != "" else None
            est, prio, _, _ = m.clasificar_cliente(dias, int(r["Transacciones"]), r["Estado_Cobertura"])
            self.assertEqual((r["Estado_Cliente"], r["Prioridad_Llamada"]), (est, prio), r["Cliente_ID"])


class TestSinFugaDelFuturo(unittest.TestCase):
    def test_features_ignoran_fechas_posteriores_al_corte(self):
        pasado = [CORTE - timedelta(days=d) for d in (3, 20, 70, 200)]
        futuro = [CORTE + timedelta(days=d) for d in (1, 5, 29)]
        self.assertEqual(features_en_corte(pasado, CORTE), features_en_corte(pasado + futuro, CORTE))

    def test_sin_historial_usa_recencia_sentinela(self):
        rec, f30, f90, n = features_en_corte([CORTE + timedelta(days=5)], CORTE)
        self.assertEqual((f30, f90, n), (0, 0, 0))
        self.assertEqual(rec, 730)


if __name__ == "__main__":
    unittest.main()
