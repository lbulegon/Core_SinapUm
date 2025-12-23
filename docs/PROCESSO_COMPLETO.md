# Processo Completo: Mapear e Corrigir Código Évora/Vitrinezap

## Passo a Passo

### 1. Preparar o Windows

#### 1.1. Descobrir informações de rede
No Windows PowerShell:
```powershell
# Nome do computador
$env:COMPUTERNAME

# IP local
ipconfig | Select-String "IPv4"
```

#### 1.2. Compartilhar a pasta (se necessário)
1. Clique com botão direito em `C:\Users\lbule\OneDrive\Documentos\Source\evora`
2. Propriedades → Compartilhamento → Compartilhar...
3. Escolha o usuário e clique em Compartilhar
4. Anote o caminho de rede (ex: `\\NOME-PC\evora`)

### 2. Mapear no Ubuntu

#### 2.1. Instalar ferramentas
```bash
sudo apt-get update
sudo apt-get install -y cifs-utils
```

#### 2.2. Criar ponto de montagem
```bash
sudo mkdir -p /mnt/evora_windows
```

#### 2.3. Montar a pasta

**Opção A: Com IP (mais confiável)**
```bash
# Substitua 192.168.x.x pelo IP do Windows
sudo mount -t cifs //192.168.x.x/evora /mnt/evora_windows \
  -o username=lbule,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0777,dir_mode=0777
```

**Opção B: Com nome do computador**
```bash
# Substitua NOME-PC pelo nome do seu computador
sudo mount -t cifs //NOME-PC/evora /mnt/evora_windows \
  -o username=lbule,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0777,dir_mode=0777
```

**Opção C: Com arquivo de credenciais (recomendado)**
```bash
# Criar arquivo de credenciais
cat > ~/.smbcredentials << EOF
username=lbule
password=SUA_SENHA_AQUI
domain=WORKGROUP
EOF
chmod 600 ~/.smbcredentials

# Montar
sudo mount -t cifs //NOME-PC/evora /mnt/evora_windows \
  -o credentials=~/.smbcredentials,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0777,dir_mode=0777
```

#### 2.4. Verificar montagem
```bash
ls -la /mnt/evora_windows
```

Se você ver os arquivos do Évora, a montagem funcionou! ✅

### 3. Aplicar Correções Automaticamente

```bash
# Executar script de correção
sudo /root/corrigir_evora_apos_mapear.sh
```

O script irá:
- ✅ Corrigir todas as referências de porta 8000 → 8001
- ✅ Verificar endpoints
- ✅ Listar arquivos que podem precisar de atenção manual

### 4. Verificar Correções

```bash
# Ver arquivos modificados
cd /mnt/evora_windows
grep -r "8001" . --include="*.js" --include="*.ts" --include="*.py" | head -20

# Verificar configurações
grep -r "OPENMIND_AI_URL\|openmind" . --include="*.env*" --include="*.js" --include="*.ts" | head -20
```

### 5. Testar Integração

Após as correções, teste a integração:
1. Inicie o servidor do Évora/Vitrinezap
2. Tente fazer upload de uma imagem de produto
3. Verifique se a análise funciona corretamente

## Alternativa: Copiar Arquivos

Se o mapeamento não funcionar, você pode copiar os arquivos:

### Do Windows para Linux (via SCP)
No Windows PowerShell:
```powershell
scp -r C:\Users\lbule\OneDrive\Documentos\Source\evora root@IP_DO_LINUX:/root/evora
```

### Depois, aplicar correções:
```bash
# Ajustar caminho no script
sed -i 's|/mnt/evora_windows|/root/evora|g' /root/corrigir_evora_apos_mapear.sh

# Executar correções
sudo /root/corrigir_evora_apos_mapear.sh
```

## Troubleshooting

### Erro: "mount error(13): Permission denied"
- Verifique se a pasta está compartilhada
- Tente adicionar `sec=ntlmv2` nas opções:
```bash
sudo mount -t cifs //NOME-PC/evora /mnt/evora_windows \
  -o username=lbule,sec=ntlmv2,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0777,dir_mode=0777
```

### Erro: "Host is down"
- Verifique conectividade: `ping IP_DO_WINDOWS`
- Verifique firewall do Windows
- Certifique-se de que o compartilhamento de arquivos está habilitado

### Arquivos não aparecem após montagem
- Verifique permissões: `ls -la /mnt/evora_windows`
- Tente com `uid=0,gid=0` para acesso root

## Montagem Automática (Opcional)

Para montar automaticamente na inicialização, adicione ao `/etc/fstab`:

```bash
sudo nano /etc/fstab
```

Adicione:
```
//NOME-PC/evora /mnt/evora_windows cifs credentials=~/.smbcredentials,uid=0,gid=0,iocharset=utf8,file_mode=0777,dir_mode=0777 0 0
```

## Desmontar

```bash
sudo umount /mnt/evora_windows
```

## Arquivos Criados

- `/root/INSTRUCOES_MAPEAMENTO.md` - Instruções detalhadas de mapeamento
- `/root/mapear_pasta_evora.sh` - Script auxiliar de mapeamento
- `/root/corrigir_evora_apos_mapear.sh` - Script de correção automática
- `/root/CORRECOES_EVORA_VITRINEZAP.md` - Guia de correções manuais

