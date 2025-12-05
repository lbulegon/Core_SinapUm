# Comandos de Teste - Leitura de Imagens e Geração de JSON

Este diretório contém scripts de teste para validar a leitura de imagens e geração de JSON no sistema OpenMind.

- python -m venv .venv
Windows
- .venv\Scripts\activate  
Linux
- source .venv/bin/activate
- railway --version  
- pip freeze > requirements.txt
- pip install -r requirements.txt
- npm i -g @railway/cli
- railway login
- railway link -p 50594409-8ec3-4211-9cf7-6f4ef2f9afc8
- railway up
- railway reload
- python manage.py startapp nome_do_app
- python manage.py collectstatic
- python manage.py makemigrations  
- python manage.py migrate
- python manage.py createsuperuser
- python manage.py gerafatura
- python manage.py escanear_portas --host 127.0.0.1 --inicio 31400 --fim 31409
- python manage.py extrair_pdf docs/exemplo.pdf





## 📋 Scripts Disponíveis

### 1. `test_image_json_simple.py`
**Teste Simplificado de Leitura de Imagens**

- ✅ Testa a leitura básica de imagens
- ✅ Valida formato, dimensões e tamanho
- ✅ Gera JSON com informações das imagens
- ✅ Valida estrutura do JSON

**Uso:**
```bash
cd /root/SinapUm/management/commands
python3 test_image_json_simple.py
```

**Saída:**
- `test_image_json_output_simple.json` - JSON gerado

---

### 2. `test_image_json_generation.py`
**Teste Completo de Geração de JSON**

- ✅ Carregamento de imagens via MockImageProvider
- ✅ Integração com casos de teste existentes
- ✅ Execução de casos de teste completos
- ✅ Geração e validação de JSON de resposta

**Uso:**
```bash
cd /root/SinapUm/management/commands
python3 test_image_json_generation.py
```

**Saída:**
- `test_image_json_output.json` - JSON gerado
- `test_image_json_report.txt` - Relatório detalhado

---

### 3. `test_image_content_analysis.py` ⭐
**Teste de Análise de Conteúdo de Imagens**

- ✅ **Analisa o conteúdo real das imagens através de VLM**
- ✅ Gera descrição textual do conteúdo
- ✅ Processa descrição através do LLM para gerar ações JSON
- ✅ **Valida se o JSON reflete corretamente o conteúdo analisado**

**Uso:**
```bash
cd /root/SinapUm/management/commands
python3 test_image_content_analysis.py
```

**Saída:**
- `image_content_analysis.json` - Resultados completos
- `image_content_analysis_report.txt` - Relatório detalhado

---

### 4. `test_openmind_images.py`
**Informações sobre Testes de Imagens**

- ✅ Lista casos de teste disponíveis
- ✅ Lista imagens de teste disponíveis
- ✅ Mostra instruções de uso

**Uso:**
```bash
cd /root/SinapUm/management/commands
python3 test_openmind_images.py
```

---

## 🔧 Configuração

### Diretórios

Os scripts estão localizados em:
```
/root/SinapUm/management/commands/
```

E acessam os recursos do OpenMind em:
```
/root/openmind_ws/OM1/
```

### Variáveis de Ambiente

Para usar a API do OpenMind, configure:

```bash
export OM1_API_KEY='sua_chave_aqui'
# ou
export OM_API_KEY='sua_chave_aqui'
```

Se não configurada, os testes usarão respostas mock quando necessário.

---

## 📊 Estrutura dos Testes

### Fluxo Básico

1. **Leitura de Imagens** → Valida formato e dimensões
2. **Análise de Conteúdo** (VLM) → Gera descrição textual
3. **Geração de JSON** (LLM) → Gera ações baseadas no conteúdo
4. **Validação** → Verifica coerência conteúdo vs JSON

### Validações Realizadas

- ✅ Existência e leitura de arquivos de imagem
- ✅ Formato, dimensões e tamanho
- ✅ Análise de conteúdo através de VLM
- ✅ Geração de descrições textuais
- ✅ Geração de ações JSON
- ✅ Coerência entre conteúdo analisado e JSON gerado
- ✅ Estrutura e validade do JSON

---

## 🚀 Execução Rápida

```bash
# Navegar para o diretório de comandos
cd /root/SinapUm/management/commands

# Executar teste simplificado
python3 test_image_json_simple.py

# Executar teste completo
python3 test_image_json_generation.py

# Executar análise de conteúdo
python3 test_image_content_analysis.py

# Ver informações sobre testes
python3 test_openmind_images.py
```

---

## 📁 Arquivos Gerados

Os scripts geram os seguintes arquivos no diretório de comandos:

- `test_image_json_output_simple.json` - Saída do teste simplificado
- `test_image_json_output.json` - Saída do teste completo
- `test_image_json_report.txt` - Relatório do teste completo
- `image_content_analysis.json` - Análise de conteúdo completa
- `image_content_analysis_report.txt` - Relatório de análise

---

## 🔍 Casos de Teste Suportados

Os scripts podem executar os seguintes casos de teste:

1. **coco_indoor_detection** - Detecção COCO em cena indoor
2. **open_ai_indoor_test** - Teste OpenAI VLM
3. **gemini_indoor_test** - Teste Gemini VLM
4. **vila_indoor_test** - Teste VILA VLM

---

## 📚 Documentação Adicional

Para mais informações, consulte:

- `/root/openmind_ws/OM1/TESTES_IMAGEM_JSON.md` - Documentação completa
- `/root/openmind_ws/OM1/ANALISE_CONTEUDO_IMAGEM.md` - Documentação de análise
- `/root/openmind_ws/OM1/RESUMO_TESTES.md` - Resumo dos testes

---

## 🐛 Solução de Problemas

### Erro: "Diretório do OpenMind não encontrado"
**Solução:** Verifique se `/root/openmind_ws/OM1` existe e está acessível.

### Erro: "PIL/Pillow não está disponível"
**Solução:** Instale com `pip install Pillow`

### Erro: "Caso de teste não encontrado"
**Solução:** Verifique se os casos de teste existem em `/root/openmind_ws/OM1/tests/integration/data/test_cases/`

### Erro: "Imagens não encontradas"
**Solução:** Verifique se as imagens existem em `/root/openmind_ws/OM1/tests/integration/data/images/`

---

## ✅ Status dos Scripts

- ✅ `test_image_json_simple.py` - Funcional
- ✅ `test_image_json_generation.py` - Funcional
- ✅ `test_image_content_analysis.py` - Funcional
- ✅ `test_openmind_images.py` - Funcional

Todos os scripts estão prontos para uso!

