# Instruções para Mapear Pasta do Windows no Ubuntu

## Método 1: Via SMB/CIFS (Recomendado)

### Passo 1: Descobrir o caminho de rede do Windows

No Windows, abra o PowerShell e execute:
```powershell
# Descobrir o nome do computador
$env:COMPUTERNAME

# Descobrir o IP
ipconfig | Select-String "IPv4"
```

### Passo 2: Compartilhar a pasta (se necessário)

1. Clique com botão direito na pasta `C:\Users\lbule\OneDrive\Documentos\Source\evora`
2. Propriedades → Compartilhamento
3. Compartilhar... → Escolher usuário → Compartilhar
4. Anotar o caminho de rede (ex: `\\NOME-PC\evora`)

### Passo 3: Instalar ferramentas SMB no Ubuntu

```bash
sudo apt-get update
sudo apt-get install -y cifs-utils
```

### Passo 4: Criar ponto de montagem

```bash
sudo mkdir -p /mnt/evora_windows
```

### Passo 5: Montar a pasta

**Opção A: Com IP do Windows**
```bash
# Substitua 192.168.x.x pelo IP do seu Windows
sudo mount -t cifs //192.168.x.x/evora /mnt/evora_windows \
  -o username=lbule,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0777,dir_mode=0777
```

**Opção B: Com nome do computador**
```bash
# Substitua NOME-PC pelo nome do seu computador Windows
sudo mount -t cifs //NOME-PC/evora /mnt/evora_windows \
  -o username=lbule,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0777,dir_mode=0777
```

**Opção C: Com arquivo de credenciais (mais seguro)**
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

### Passo 6: Verificar montagem

```bash
ls -la /mnt/evora_windows
```

## Método 2: Via SSH/SFTP (Se o Windows tiver SSH)

Se você tiver SSH configurado no Windows (via OpenSSH ou WSL):

```bash
# Instalar sshfs
sudo apt-get install -y sshfs

# Criar ponto de montagem
sudo mkdir -p /mnt/evora_windows

# Montar via SSH
sshfs lbule@IP_DO_WINDOWS:/mnt/c/Users/lbule/OneDrive/Documentos/Source/evora /mnt/evora_windows
```

## Método 3: Via WSL (Se estiver usando WSL)

Se você estiver usando WSL no Windows, pode acessar diretamente:

```bash
# No WSL, a pasta do Windows está em:
/mnt/c/Users/lbule/OneDrive/Documentos/Source/evora
```

## Método 4: Copiar arquivos via SCP

Se preferir copiar os arquivos uma vez:

```bash
# Do Windows para Linux (executar no Windows PowerShell)
scp -r C:\Users\lbule\OneDrive\Documentos\Source\evora root@IP_DO_LINUX:/root/evora

# Ou do Linux para copiar do Windows (se tiver acesso)
scp -r lbule@IP_DO_WINDOWS:/mnt/c/Users/lbule/OneDrive/Documentos/Source/evora /root/evora
```

## Montagem Automática (Persistente)

Para montar automaticamente na inicialização, adicione ao `/etc/fstab`:

```bash
sudo nano /etc/fstab
```

Adicione a linha:
```
//NOME-PC/evora /mnt/evora_windows cifs credentials=~/.smbcredentials,uid=0,gid=0,iocharset=utf8,file_mode=0777,dir_mode=0777 0 0
```

## Desmontar

```bash
sudo umount /mnt/evora_windows
```

## Troubleshooting

### Erro: "mount error(13): Permission denied"
- Verifique se a pasta está compartilhada no Windows
- Verifique se o usuário tem permissão
- Tente adicionar `sec=ntlmv2` nas opções

### Erro: "Host is down"
- Verifique se o Windows está acessível na rede
- Teste: `ping IP_DO_WINDOWS`
- Verifique firewall do Windows

### Erro: "No route to host"
- Verifique conectividade de rede
- Verifique se SMB está habilitado no Windows

## Após Mapear

Uma vez mapeado, você pode acessar os arquivos em:
```bash
cd /mnt/evora_windows
ls -la
```

E eu poderei fazer as correções diretamente nos arquivos!

