# Mapeamento de Pasta Windows para Ubuntu

## Pré-requisitos

### No Windows:
1. **Compartilhar a pasta:**
   - Clique com o botão direito na pasta `C:\Users\marci\OneDrive\Documentos\GitHub\evora`
   - Selecione "Propriedades" → Aba "Compartilhamento"
   - Clique em "Compartilhar..." e adicione o usuário ou "Todos"
   - Anote o nome do compartilhamento (geralmente `evora`)

2. **Obter o IP do Windows:**
   - Abra o PowerShell ou CMD
   - Execute: `ipconfig`
   - Anote o endereço IPv4 (exemplo: `192.168.1.100`)

3. **Verificar credenciais:**
   - Você precisará do nome de usuário e senha do Windows
   - Ou criar um usuário específico para compartilhamento

### No Ubuntu:
1. **Instalar cifs-utils** (já instalado):
   ```bash
   sudo apt-get install -y cifs-utils
   ```

## Método 1: Montagem Manual (Temporária)

```bash
# Criar diretório de montagem
sudo mkdir -p /mnt/windows_evora

# Montar a pasta (substitua os valores)
sudo mount -t cifs //IP_WINDOWS/nome_compartilhamento /mnt/windows_evora \
  -o username=marci,password=SUA_SENHA,uid=$(id -u),gid=$(id -g),iocharset=utf8

# Exemplo:
# sudo mount -t cifs //192.168.1.100/evora /mnt/windows_evora \
#   -o username=marci,password=senha123,uid=$(id -u),gid=$(id -g),iocharset=utf8
```

## Método 2: Montagem Automática (Permanente)

### 1. Criar arquivo de credenciais (mais seguro):
```bash
sudo nano /etc/samba/credentials_windows
```

Adicione:
```
username=marci
password=SUA_SENHA
domain=WORKGROUP
```

Proteja o arquivo:
```bash
sudo chmod 600 /etc/samba/credentials_windows
```

### 2. Adicionar ao /etc/fstab:
```bash
sudo nano /etc/fstab
```

Adicione a linha (substitua IP e nome do compartilhamento):
```
//IP_WINDOWS/nome_compartilhamento /mnt/windows_evora cifs credentials=/etc/samba/credentials_windows,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0777,dir_mode=0777 0 0
```

### 3. Testar e montar:
```bash
# Testar a configuração
sudo mount -a

# Verificar se montou
df -h | grep windows_evora
```

## Método 3: Usando SMBClient (Acesso via linha de comando)

```bash
# Instalar smbclient
sudo apt-get install -y smbclient

# Listar compartilhamentos disponíveis
smbclient -L //IP_WINDOWS -U marci

# Acessar o compartilhamento
smbclient //IP_WINDOWS/evora -U marci
```

## Desmontar

```bash
sudo umount /mnt/windows_evora
```

## Solução de Problemas

### Erro: "mount error(13): Permission denied"
- Verifique as credenciais
- Verifique as permissões de compartilhamento no Windows

### Erro: "mount error(112): Host is down"
- Verifique se o Windows está acessível na rede
- Verifique o firewall do Windows

### Erro: "mount error(2): No such file or directory"
- Verifique se o caminho do compartilhamento está correto
- Use `smbclient -L //IP_WINDOWS` para listar compartilhamentos

### Verificar conectividade:
```bash
ping IP_WINDOWS
```

## Notas Importantes

1. **OneDrive:** Como a pasta está no OneDrive, certifique-se de que os arquivos estão sincronizados localmente no Windows
2. **Firewall:** O Windows pode bloquear conexões SMB. Verifique as regras de firewall
3. **SMB Versão:** Se houver problemas, tente especificar a versão do SMB:
   ```bash
   -o vers=3.0
   ```

