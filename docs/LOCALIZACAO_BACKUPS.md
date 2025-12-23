# Localização dos Backups

## 📦 Onde os Backups São Salvos

Os backups criados pelo script `remover_pastas_antigas.sh` são salvos em:

```
/root/backup_openmind_remocao_YYYYMMDD_HHMMSS_*
```

### Formato dos Nomes

- **Base**: `/root/backup_openmind_remocao_`
- **Data/Hora**: `YYYYMMDD_HHMMSS` (exemplo: `20241215_143022`)
- **Sufixo**: Nome da pasta original

### Exemplos de Arquivos Criados

```
/root/backup_openmind_remocao_20241215_143022_openmind_ws.tar.gz
/root/backup_openmind_remocao_20241215_143022_openmind-ai.tar.gz
```

## 📋 Estrutura Completa

```
/root/
├── backup_openmind_remocao_20241215_143022_openmind_ws.tar.gz    (backup de /root/openmind_ws)
└── backup_openmind_remocao_20241215_143022_openmind-ai.tar.gz   (backup de /opt/openmind-ai)
```

## 🔍 Como Verificar os Backups

### Listar todos os backups do OpenMind

```bash
ls -lh /root/backup_openmind_remocao_*
```

### Ver tamanho dos backups

```bash
du -sh /root/backup_openmind_remocao_*
```

### Verificar conteúdo de um backup (sem extrair)

```bash
tar -tzf /root/backup_openmind_remocao_YYYYMMDD_HHMMSS_openmind_ws.tar.gz | head -20
```

## 🔄 Como Restaurar

### Restaurar `/root/openmind_ws`

```bash
tar -xzf /root/backup_openmind_remocao_YYYYMMDD_HHMMSS_openmind_ws.tar.gz -C /root/
```

### Restaurar `/opt/openmind-ai`

```bash
sudo tar -xzf /root/backup_openmind_remocao_YYYYMMDD_HHMMSS_openmind-ai.tar.gz -C /opt/
```

## 💾 Gerenciamento de Backups

### Listar todos os backups

```bash
ls -lht /root/backup_openmind_remocao_* | head -10
```

### Remover backups antigos (manter apenas os últimos 7 dias)

```bash
find /root/backup_openmind_remocao_* -mtime +7 -delete
```

### Mover backups para outro local

```bash
# Criar diretório de arquivo
mkdir -p /root/backups_antigos

# Mover backups com mais de 30 dias
find /root/backup_openmind_remocao_* -mtime +30 -exec mv {} /root/backups_antigos/ \;
```

## 📊 Informações dos Backups

O script mostra informações sobre os backups ao final da execução:

```
📦 Backups disponíveis em:
   /root/backup_openmind_remocao_20241215_143022_openmind_ws.tar.gz (1.2G)
   /root/backup_openmind_remocao_20241215_143022_openmind-ai.tar.gz (450M)
```

## ⚠️ Importante

- Os backups são criados **antes** da remoção das pastas
- Os backups são **comprimidos** (`.tar.gz`) para economizar espaço
- Os backups ficam em `/root/` para fácil acesso
- **Mantenha os backups** até confirmar que tudo está funcionando corretamente

## 🗑️ Limpeza de Backups

Após confirmar que tudo está funcionando (após alguns dias/semanas), você pode remover os backups:

```bash
# Remover backups específicos
rm /root/backup_openmind_remocao_YYYYMMDD_HHMMSS_*

# Ou remover todos os backups antigos (mais de 30 dias)
find /root/backup_openmind_remocao_* -mtime +30 -delete
```

