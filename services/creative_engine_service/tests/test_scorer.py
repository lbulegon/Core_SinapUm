"""
Testes para scorer
"""
import unittest
from services.creative_engine_service.learning.scorer import CreativeScorer


class ScorerTestCase(unittest.TestCase):
    """Testes para scorer de performance"""
    
    def setUp(self):
        self.scorer = CreativeScorer()
    
    def test_calculate_metrics(self):
        """Testa cálculo de métricas"""
        performance_data = {
            "views": 100,
            "responses": 20,
            "interests": 15,
            "orders": 5,
            "conversions": 3,
        }
        
        metrics = self.scorer.calculate_metrics("variant_123", performance_data)
        
        self.assertEqual(metrics["variant_id"], "variant_123")
        self.assertGreater(metrics["response_rate"], 0)
        self.assertGreater(metrics["interest_rate"], 0)
        self.assertGreater(metrics["engagement_score"], 0)
        self.assertLessEqual(metrics["confidence_index"], 1.0)
    
    def test_compare_variants(self):
        """Testa comparação de variantes"""
        variants_metrics = {
            "variant_1": {
                "engagement_score": 0.5,
                "response_rate": 0.2,
            },
            "variant_2": {
                "engagement_score": 0.7,
                "response_rate": 0.3,
            },
        }
        
        result = self.scorer.compare_variants(variants_metrics)
        
        self.assertEqual(result["best_variant"], "variant_2")
        self.assertEqual(len(result["ranking"]), 2)
