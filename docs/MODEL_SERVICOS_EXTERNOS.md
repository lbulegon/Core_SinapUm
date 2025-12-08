# Model ServicoExterno - Documentação

## Descrição

O model `ServicoExterno` foi criado para armazenar de forma segura credenciais e configurações de serviços externos contratados, incluindo:
- APIs e serviços de terceiros (Twilio, Firebase, OpenAI, etc.)
- Servidores VPS e hospedagem (InterServer, GoDaddy, DigitalOcean, etc.)
- Credenciais de acesso SSH, FTP, MySQL
- Painéis de controle (cPanel, Plesk, etc.)

## Recursos de Segurança

✅ **Criptografia Automática**: Todos os campos sensíveis são automaticamente criptografados antes de serem salvos no banco de dados usando a biblioteca `cryptography` com Fernet (baseado no SECRET_KEY do Django).

✅ **Campos Criptografados**:
- Senhas gerais
- API Secrets
- Auth Tokens
- Senhas SSH
- Chaves privadas SSH
- Senhas do painel de controle
- Senhas FTP
- Senhas MySQL

## Tipos de Serviços Suportados

### Serviços de Comunicação e API
- Twilio
- SendGrid
- Telegram Bot API
- WhatsApp Business API

### Cloud e Infraestrutura
- AWS
- Azure
- Google Cloud
- Firebase
- DigitalOcean
- Linode

### VPS e Hospedagem
- **InterServer**
- **GoDaddy**
- Namecheap
- HostGator
- Bluehost
- Hostinger
- SiteGround
- DreamHost
- Vultr
- Hetzner
- Contabo

### Pagamentos
- Stripe
- PayPal
- Mercado Pago

### Redes Sociais
- Facebook API
- Instagram API

### IA e Machine Learning
- OpenAI

## Campos do Model

### Informações Básicas
- `nome`: Nome identificador do serviço
- `tipo_servico`: Tipo de serviço (choices)
- `ambiente`: Ambiente de uso (Desenvolvimento/Homologação/Produção)
- `url_base`: URL base do serviço
- `ativo`: Indica se o serviço está ativo

### Credenciais de Autenticação
- `usuario`: Usuário/Login
- `senha`: Senha (criptografada)
- `api_key`: API Key
- `api_secret`: API Secret (criptografado)
- `account_sid`: Account SID (para Twilio)
- `auth_token`: Auth Token (criptografado)

### Informações do Servidor VPS
- `ip_servidor`: Endereço IP do servidor
- `sistema_operacional`: SO do servidor
- `porta_ssh`: Porta SSH (padrão: 22)
- `usuario_ssh`: Usuário SSH
- `senha_ssh`: Senha SSH (criptografada)
- `chave_privada_ssh`: Chave privada SSH (criptografada)

### Painel de Controle
- `url_painel_controle`: URL do painel (cPanel, Plesk, etc)
- `usuario_painel`: Usuário do painel
- `senha_painel`: Senha do painel (criptografada)

### FTP
- `porta_ftp`: Porta FTP (padrão: 21)
- `usuario_ftp`: Usuário FTP
- `senha_ftp`: Senha FTP (criptografada)

### Banco de Dados MySQL/MariaDB
- `porta_mysql`: Porta MySQL (padrão: 3306)
- `usuario_mysql`: Usuário MySQL
- `senha_mysql`: Senha MySQL (criptografada)
- `nome_banco_dados`: Nome do banco de dados

### Outros
- `credenciais_adicionais`: JSON com credenciais adicionais
- `observacoes`: Observações sobre o serviço

## Métodos Disponíveis

### Métodos de Descriptografia
- `get_senha_decrypted()`: Retorna senha descriptografada
- `get_api_secret_decrypted()`: Retorna API Secret descriptografado
- `get_auth_token_decrypted()`: Retorna Auth Token descriptografado
- `get_senha_ssh_decrypted()`: Retorna senha SSH descriptografada
- `get_chave_privada_ssh_decrypted()`: Retorna chave privada SSH descriptografada
- `get_senha_painel_decrypted()`: Retorna senha do painel descriptografada
- `get_senha_ftp_decrypted()`: Retorna senha FTP descriptografada
- `get_senha_mysql_decrypted()`: Retorna senha MySQL descriptografada

## Uso no Django Admin

O model está registrado no Django Admin com:
- Listagem com filtros por tipo de serviço, ambiente e status
- Busca por nome, usuário, IP, API key, etc.
- Campos organizados em fieldsets colapsáveis
- Indicadores visuais de status das credenciais criptografadas
- Campos readonly que mostram se credenciais estão definidas (sem expor valores)

## Instalação e Migrações

### 1. Instalar dependências
```bash
pip install cryptography>=41.0.0
```

### 2. Criar migrações
```bash
cd /root/SinapUm
python manage.py makemigrations app_sinapum
```

### 3. Aplicar migrações
```bash
python manage.py migrate
```

## Exemplo de Uso

```python
from app_sinapum.models import ServicoExterno

# Criar serviço VPS InterServer
servico = ServicoExterno.objects.create(
    nome="VPS InterServer Principal",
    tipo_servico="interserver",
    ambiente="producao",
    ip_servidor="192.168.1.100",
    sistema_operacional="Ubuntu 22.04",
    porta_ssh=22,
    usuario_ssh="root",
    senha_ssh="minha_senha_segura",  # Será criptografada automaticamente
    url_painel_controle="https://my.interserver.net",
    usuario_painel="admin",
    senha_painel="senha_painel",  # Será criptografada automaticamente
    ativo=True
)

# Recuperar senha descriptografada
senha_ssh = servico.get_senha_ssh_decrypted()

# Criar serviço Twilio
twilio = ServicoExterno.objects.create(
    nome="Twilio Produção",
    tipo_servico="twilio",
    ambiente="producao",
    url_base="https://api.twilio.com",
    account_sid="ACxxxxxxxxxxxx",
    auth_token="token_secreto",  # Será criptografado automaticamente
    ativo=True
)
```

## Importante

⚠️ **Segurança**: 
- As credenciais são criptografadas usando o `SECRET_KEY` do Django
- Nunca compartilhe o `SECRET_KEY` em produção
- Faça backup seguro do `SECRET_KEY` para poder descriptografar dados se necessário

⚠️ **Criptografia**: 
- A criptografia ocorre automaticamente no método `save()`
- Valores já criptografados não são re-criptografados (detecção automática)
- A descriptografia deve ser feita apenas quando necessário

## Próximos Passos

1. Executar migrações após instalar a dependência `cryptography`
2. Testar criação de serviços no Django Admin
3. Implementar logs de acesso às credenciais (auditoria)
4. Considerar uso de variáveis de ambiente para SECRET_KEY em produção

