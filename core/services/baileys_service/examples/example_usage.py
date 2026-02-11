"""
Exemplo de Uso do Baileys Service
==================================

Exemplos práticos de como usar o Baileys Service.
"""
import asyncio
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from core.services.baileys_service import BaileysClient


async def exemplo_basico():
    """Exemplo básico: conectar e enviar mensagem"""
    print("=" * 50)
    print("Exemplo 1: Uso Básico")
    print("=" * 50)
    
    client = BaileysClient(session_name="exemplo-basico")
    
    try:
        # Conecta (gera QR code se necessário)
        print("Conectando ao WhatsApp...")
        await client.connect()
        
        # Envia mensagem
        print("Enviando mensagem...")
        result = await client.send_text(
            "5511999999999",  # Substitua pelo número real
            "Olá! Esta é uma mensagem de teste do Baileys Service."
        )
        
        print(f"✅ Mensagem enviada! ID: {result.get('message_id')}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


async def exemplo_com_handlers():
    """Exemplo com handlers de mensagens"""
    print("\n" + "=" * 50)
    print("Exemplo 2: Handlers de Mensagens")
    print("=" * 50)
    
    client = BaileysClient(session_name="exemplo-handlers")
    
    # Handler para mensagens recebidas
    async def handle_message(from_jid, text, message_data):
        print(f"📨 Mensagem recebida de {from_jid}: {text}")
        
        # Responde automaticamente
        if text.lower() == "jarvis":
            await client.send_text(from_jid, "Olá senhor, estou aqui para servi-lo.")
    
    # Registra handler
    client.on_message(handle_message)
    
    try:
        await client.connect()
        print("✅ Conectado! Aguardando mensagens...")
        
        # Mantém conexão ativa
        await asyncio.sleep(60)  # Aguarda 60 segundos
        
    except Exception as e:
        print(f"❌ Erro: {e}")


async def exemplo_envio_midia():
    """Exemplo de envio de mídia"""
    print("\n" + "=" * 50)
    print("Exemplo 3: Envio de Mídia")
    print("=" * 50)
    
    client = BaileysClient(session_name="exemplo-midia")
    
    try:
        await client.connect()
        
        # Envia imagem
        image_path = Path(__file__).parent.parent.parent.parent / "media" / "tony.jpg"
        if image_path.exists():
            print("Enviando imagem...")
            result = await client.send_image(
                "5511999999999",
                str(image_path),
                caption="*aqui está sua imagem senhor*"
            )
            print(f"✅ Imagem enviada! ID: {result.get('message_id')}")
        else:
            print(f"⚠️ Arquivo não encontrado: {image_path}")
        
        # Envia documento
        pdf_path = Path(__file__).parent.parent.parent.parent / "media" / "tony.pdf"
        if pdf_path.exists():
            print("Enviando documento...")
            result = await client.send_document(
                "5511999999999",
                str(pdf_path),
                caption="aqui está seu documento senhor"
            )
            print(f"✅ Documento enviado! ID: {result.get('message_id')}")
        else:
            print(f"⚠️ Arquivo não encontrado: {pdf_path}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


async def exemplo_espera_resposta():
    """Exemplo de espera de resposta"""
    print("\n" + "=" * 50)
    print("Exemplo 4: Espera de Resposta")
    print("=" * 50)
    
    client = BaileysClient(session_name="exemplo-espera")
    
    try:
        await client.connect()
        
        # Envia mensagem perguntando algo
        await client.send_text(
            "5511999999999",
            "Qual é a sua cor favorita?"
        )
        
        # Aguarda resposta (30 segundos)
        print("Aguardando resposta...")
        try:
            response = await client.wait_response(
                "5511999999999@s.whatsapp.net",
                timeout=30000
            )
            print(f"✅ Resposta recebida: {response}")
        except asyncio.TimeoutError:
            print("⏱️ Timeout: Nenhuma resposta recebida")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


async def exemplo_integracao_gateway():
    """Exemplo usando o Gateway WhatsApp"""
    print("\n" + "=" * 50)
    print("Exemplo 5: Integração com Gateway")
    print("=" * 50)
    
    from core.services.whatsapp.gateway import get_whatsapp_gateway
    
    gateway = get_whatsapp_gateway()
    
    # Envia mensagem via gateway
    result = gateway.send_text(
        to="5511999999999",
        text="Olá! Esta é uma mensagem via Gateway usando Baileys.",
        metadata={
            'shopper_id': 'exemplo-shopper',
            'skm_id': 'skm-exemplo',
            'correlation_id': 'corr-exemplo'
        }
    )
    
    if result.is_success():
        print(f"✅ Mensagem enviada via Gateway! ID: {result.message_id}")
    else:
        print(f"❌ Erro: {result.error}")


if __name__ == "__main__":
    print("Baileys Service - Exemplos de Uso")
    print("=" * 50)
    print("\nEscolha um exemplo:")
    print("1. Uso Básico")
    print("2. Handlers de Mensagens")
    print("3. Envio de Mídia")
    print("4. Espera de Resposta")
    print("5. Integração com Gateway")
    print("0. Todos")
    
    escolha = input("\nDigite o número do exemplo (0-5): ")
    
    if escolha == "1":
        asyncio.run(exemplo_basico())
    elif escolha == "2":
        asyncio.run(exemplo_com_handlers())
    elif escolha == "3":
        asyncio.run(exemplo_envio_midia())
    elif escolha == "4":
        asyncio.run(exemplo_espera_resposta())
    elif escolha == "5":
        asyncio.run(exemplo_integracao_gateway())
    elif escolha == "0":
        print("\n⚠️ Executando todos os exemplos pode gerar muitas mensagens!")
        confirmar = input("Continuar? (s/n): ")
        if confirmar.lower() == 's':
            asyncio.run(exemplo_basico())
            asyncio.run(exemplo_envio_midia())
            asyncio.run(exemplo_integracao_gateway())
    else:
        print("Opção inválida!")
