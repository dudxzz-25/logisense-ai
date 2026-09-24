from datetime import date
import unittest

from backend.app.main import (
    DelayPredictionRequest,
    catalogos,
    kpis,
    ml_status,
    model_metrics,
    predict_delay,
    root,
)


class ApiSmokeTests(unittest.TestCase):
    def test_root(self):
        response = root()

        self.assertEqual(response["project"], "LogiSense AI")
        self.assertEqual(response["status"], "online")
        self.assertTrue(response["machine_learning"])

    def test_kpis(self):
        response = kpis()

        self.assertGreater(response["entregas"], 0)
        self.assertGreaterEqual(response["sla_pct"], 0)
        self.assertLessEqual(response["sla_pct"], 100)
        self.assertGreaterEqual(response["taxa_atraso_pct"], 0)
        self.assertLessEqual(response["taxa_atraso_pct"], 100)

    def test_catalogos(self):
        response = catalogos()

        self.assertGreater(len(response["transportadoras"]), 0)
        self.assertGreater(len(response["centros_distribuicao"]), 0)
        self.assertGreater(len(response["rotas"]), 0)

    def test_model_metrics(self):
        response = model_metrics()

        self.assertEqual(response["modelo"], "LogisticRegression")
        self.assertIn("test_metrics", response)
        self.assertIn("roc_auc", response["test_metrics"])

    def test_ml_status(self):
        response = ml_status()

        self.assertEqual(response["status"], "online")
        self.assertTrue(response["modelo_carregado"])
        self.assertEqual(response["modelo"], "LogisticRegression")

    def test_prediction(self):
        payload = DelayPredictionRequest(
            data_pedido=date(2026, 9, 24),
            transportadora_id=5,
            cd_id=2,
            rota_id=3,
            valor_frete=980,
            peso_kg=780,
            sla_dias=1,
        )

        response = predict_delay(payload)

        self.assertGreaterEqual(response["score_risco_pct"], 0)
        self.assertLessEqual(response["score_risco_pct"], 100)
        self.assertIn(
            response["nivel_risco"],
            {"Baixo", "Moderado", "Alto", "Muito alto"},
        )
        self.assertEqual(response["modelo"], "LogisticRegression")
        self.assertEqual(response["distancia_km"], 590.0)


if __name__ == "__main__":
    unittest.main()
