"""
Testes para adapters
"""
import unittest
from services.creative_engine_service.adapters.whatsapp import WhatsAppAdapter
from services.creative_engine_service.contracts import CreativeVariant, CreativeContext


class AdaptersTestCase(unittest.TestCase):
    """Testes para adapters"""
    
    def setUp(self):
        self.adapter = WhatsAppAdapter()
        self.variant = CreativeVariant(
            variant_id="test_123",
            strategy="price",
            channel="status",
            image_url="http://test.com/image.jpg",
            text_short="Texto curto",
            text_medium="Texto médio",
            text_long="Texto longo",
            ctas=["Saiba mais"],
        )
    
    def test_adapt_for_status(self):
        """Testa adaptação para status"""
        context = CreativeContext(channel="status")
        result = self.adapter.adapt(self.variant, context)
        
        self.assertEqual(result["channel"], "status")
        self.assertIn("text", result)
        self.assertIn("cta", result)
        self.assertLessEqual(len(result.get("text", "")), 250)
    
    def test_adapt_for_group(self):
        """Testa adaptação para grupo"""
        context = CreativeContext(channel="group")
        result = self.adapter.adapt(self.variant, context)
        
        self.assertEqual(result["channel"], "group")
        self.assertIn("cta_primary", result)
    
    def test_adapt_for_private(self):
        """Testa adaptação para privado"""
        context = CreativeContext(channel="private")
        result = self.adapter.adapt(self.variant, context)
        
        self.assertEqual(result["channel"], "private")
        self.assertIn("messages", result)
        self.assertEqual(len(result["messages"]), 2)  # Mensagem inicial + follow-up
