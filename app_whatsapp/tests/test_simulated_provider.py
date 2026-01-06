"""
Testes para ProviderSimulated
"""
from django.test import TestCase
from app_whatsapp.providers.provider_simulated import ProviderSimulated
from app_whatsapp.models import AppWhatsappEvent, AppWhatsappInstance
from app_whatsapp.domain.events import EventType


class ProviderSimulatedTestCase(TestCase):
    """Testes para ProviderSimulated"""
    
    def setUp(self):
        self.provider = ProviderSimulated()
        self.instance_key = "test_instance_123"
    
    def test_create_instance(self):
        """Testa criação de instância"""
        result = self.provider.create_instance(self.instance_key)
        self.assertTrue(result['success'])
        self.assertEqual(result['instance_key'], self.instance_key)
        
        # Verificar evento criado
        event = AppWhatsappEvent.objects.filter(
            instance_key=self.instance_key,
            type=EventType.INSTANCE_CREATED.value
        ).first()
        self.assertIsNotNone(event)
    
    def test_get_qr(self):
        """Testa obtenção de QR code"""
        self.provider.create_instance(self.instance_key)
        result = self.provider.get_qr(self.instance_key)
        
        self.assertEqual(result['count'], 1)
        self.assertIsNotNone(result['qr_code'])
        
        # Verificar evento QR_UPDATED
        event = AppWhatsappEvent.objects.filter(
            instance_key=self.instance_key,
            type=EventType.QR_UPDATED.value
        ).first()
        self.assertIsNotNone(event)
    
    def test_simulate_scan(self):
        """Testa simulação de scan do QR"""
        self.provider.create_instance(self.instance_key)
        result = self.provider.simulate_scan(self.instance_key)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['status'], 'connected')
        
        instance = AppWhatsappInstance.objects.get(instance_key=self.instance_key)
        self.assertEqual(instance.status, 'connected')
    
    def test_simulate_inbound_message(self):
        """Testa simulação de mensagem recebida"""
        self.provider.create_instance(self.instance_key)
        result = self.provider.simulate_inbound_message(
            instance_key=self.instance_key,
            from_number="5511999999999",
            text="Olá",
            shopper_id="shopper_123"
        )
        
        self.assertTrue(result['success'])
        
        # Verificar evento MESSAGE_IN
        event = AppWhatsappEvent.objects.filter(
            instance_key=self.instance_key,
            type=EventType.MESSAGE_IN.value
        ).first()
        self.assertIsNotNone(event)
        self.assertEqual(event.shopper_id, "shopper_123")
    
    def test_send_message(self):
        """Testa envio de mensagem"""
        self.provider.create_instance(self.instance_key)
        result = self.provider.send_message(
            instance_key=self.instance_key,
            to="5511999999999",
            payload={"text": "Teste"},
        )
        
        self.assertTrue(result['success'])
        self.assertIn('message_id', result)
        
        # Verificar evento MESSAGE_OUT
        event = AppWhatsappEvent.objects.filter(
            instance_key=self.instance_key,
            type=EventType.MESSAGE_OUT.value
        ).first()
        self.assertIsNotNone(event)
