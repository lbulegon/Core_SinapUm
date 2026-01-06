"""
Testes para estratégias
"""
import unittest
from services.creative_engine_service.strategies.price import PriceStrategy
from services.creative_engine_service.strategies.benefit import BenefitStrategy
from services.creative_engine_service.strategies.urgency import UrgencyStrategy
from services.creative_engine_service.contracts import CreativeContext


class StrategiesTestCase(unittest.TestCase):
    """Testes para estratégias de criativo"""
    
    def setUp(self):
        self.product_data = {
            "id": "1",
            "nome": "Perfume Teste",
            "marca": "Marca Teste",
            "descricao": "Descrição do produto",
            "categoria": "Perfumes",
            "volume_ml": 100,
            "imagens": ["test.jpg"],
        }
        self.context = CreativeContext(
            channel="group",
            locale="pt-BR",
            tone="direto"
        )
    
    def test_price_strategy(self):
        """Testa estratégia de preço"""
        strategy = PriceStrategy()
        brief = strategy.generate_brief(
            product_data=self.product_data,
            context=self.context
        )
        
        self.assertEqual(strategy.name, "price")
        self.assertIn("preço", brief.headline.lower())
        self.assertIsNotNone(brief.cta)
        self.assertGreater(len(brief.bullets), 0)
    
    def test_benefit_strategy(self):
        """Testa estratégia de benefícios"""
        strategy = BenefitStrategy()
        brief = strategy.generate_brief(
            product_data=self.product_data,
            context=self.context
        )
        
        self.assertEqual(strategy.name, "benefit")
        self.assertIn("qualidade", brief.headline.lower() or brief.angle.lower())
        self.assertGreater(len(brief.bullets), 0)
    
    def test_urgency_strategy(self):
        """Testa estratégia de urgência"""
        strategy = UrgencyStrategy()
        brief = strategy.generate_brief(
            product_data=self.product_data,
            context=self.context
        )
        
        self.assertEqual(strategy.name, "urgency")
        self.assertIsNotNone(brief.urgency_text)
        self.assertIn("tempo", brief.angle.lower() or brief.headline.lower())


if __name__ == '__main__':
    unittest.main()
