# Teste de Recuperação de Imagens - VitrineZap

## Problema Identificado
O VitrineZap não estava conseguindo recuperar as imagens que foram enviadas (uploaded).

## Solução Implementada

### 1. Configuração do MEDIA_ROOT
Atualizado `setup/settings.py` para usar `/data/vitrinezap/images/` como diretório base para imagens:

```python
MEDIA_URL = '/media/'
VITRINEZAP_IMAGES_PATH = Path('/data/vitrinezap/images')
if VITRINEZAP_IMAGES_PATH.exists():
    MEDIA_ROOT = VITRINEZAP_IMAGES_PATH
    (MEDIA_ROOT / 'uploads').mkdir(parents=True, exist_ok=True)
else:
    MEDIA_ROOT = BASE_DIR / 'media'
```

### 2. Migração de Imagens
As imagens existentes foram copiadas de `/root/SinapUm/media/uploads/` para `/data/vitrinezap/images/uploads/`.

### 3. Estrutura de Diretórios
- **MEDIA_ROOT**: `/data/vitrinezap/images/`
- **Uploads**: `/data/vitrinezap/images/uploads/`
- **Produtos**: `/data/vitrinezap/images/produtos/`
- **Temp**: `/data/vitrinezap/images/temp/`
- **Thumbnails**: `/data/vitrinezap/images/thumbnails/`

### 4. Permissões
```bash
chmod -R 755 /data/vitrinezap/images
chown -R root:root /data/vitrinezap/images
```

## Como Testar

**Servidor**: `69.169.102.84`

**Nota Importante**: 
- **Porta 8000**: OpenMind AI Server (FastAPI/uvicorn)
- **Porta 80**: Django (SinapUm/VitrineZap) - Servidor principal

### 1. Verificar se o Django está rodando:
```bash
# Verificar serviço systemd
systemctl status sinapum-django

# Verificar se está escutando na porta 80
netstat -tulpn | grep :80
# ou
ss -tulpn | grep :80
```

### 2. Verificar se o servidor Django está servindo imagens:
```bash
# Acesse no navegador:
http://69.169.102.84/media/uploads/1580655e-e6fa-4ad2-a854-66b0846cc6d0.jpg

# Ou via curl:
curl -I http://69.169.102.84/media/uploads/1580655e-e6fa-4ad2-a854-66b0846cc6d0.jpg
```

### 2. Verificar configuração atual:
```bash
cd /root/SinapUm
source .venv/bin/activate  # ou venv/bin/activate
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MEDIA_ROOT)
>>> print(settings.MEDIA_URL)
```

### 3. Verificar imagens existentes:
```bash
ls -la /data/vitrinezap/images/uploads/
```

### 4. Fazer upload de nova imagem:
- Acesse: http://69.169.102.84/analyze/
- Faça upload de uma imagem
- Verifique se a imagem aparece corretamente após o upload

## Verificações Importantes

1. ✅ MEDIA_ROOT está apontando para `/data/vitrinezap/images/`
2. ✅ Diretório `uploads/` existe e tem permissões corretas
3. ✅ Imagens antigas foram migradas
4. ✅ URLs estão sendo geradas corretamente como `/media/uploads/filename.jpg`
5. ✅ Servidor Django está servindo arquivos estáticos (verificar `urls.py`)

## Próximos Passos

Se ainda houver problemas:

1. **Verificar se o servidor Django está rodando:**
   ```bash
   systemctl status sinapum-django
   # ou
   ps aux | grep manage.py
   ```

2. **Reiniciar o servidor:**
   ```bash
   systemctl restart sinapum-django
   # ou se rodando manualmente:
   python manage.py runserver 0.0.0.0:8000
   ```

3. **Verificar logs:**
   ```bash
   tail -f /var/log/django/error.log
   # ou logs do systemd:
   journalctl -u sinapum-django -f
   ```

4. **Verificar se a rota está funcionando:**
   - O `urls.py` deve ter: `urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`
   - Isso só funciona quando `DEBUG=True`. Em produção, use nginx ou outro servidor web.

## Em Produção

Em produção (DEBUG=False), configure o servidor web (nginx/apache) para servir arquivos estáticos:

```nginx
location /media/ {
    alias /data/vitrinezap/images/;
}
```

