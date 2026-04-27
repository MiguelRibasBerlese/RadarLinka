# 📡 RADAR — Agregador Inteligente de Eventos de Ribeirão Preto

[![Deploy](https://img.shields.io/badge/deploy-live-brightgreen?style=flat-square&logo=vercel)](https://radar-olive-five.vercel.app)
[![Python](https://img.shields.io/badge/python-3.12-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)](LICENSE)

> Agrega, normaliza e classifica automaticamente os eventos de Ribeirão Preto — e entrega tudo numa interface limpa de jornal impresso.

---

## O que é

RADAR é um pipeline de scraping + IA que coleta eventos de múltiplas fontes da cidade, filtra só o que acontece em Ribeirão Preto, classifica cada evento em uma das 8 categorias com o modelo `llama-3.3-70b-versatile` da Groq, e gera uma página estática pronta pra consumir.

Sem banco de dados. Sem servidor. Apenas um JSON e um HTML.

**Acesse em produção:** [radar-olive-five.vercel.app](https://radar-olive-five.vercel.app)

---

## Interface

```
┌─────────────────────────────────────────────────────────────┐
│  R A D A R              Ribeirão Preto · Semana atual        │
│  ─────────────────────────────────────────────────────────  │
│  🎵 Shows & Música   🎭 Teatro   🍷 Gastronomia   🎨 Arte   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Nome evento  │  │ Nome evento  │  │ Nome evento  │      │
│  │ Local · Data │  │ Local · Data │  │ Local · Data │      │
│  │ [Sympla]     │  │ [EmRibeirão] │  │ [Shopping]   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
Fundo #F7F3EE · Acento roxo #5B2D8E · Tipografia Playfair Display
```

---

## Como funciona

**1. Coleta**
Playwright abre Sympla, EmRibeirão e RibeirãoShopping. BeautifulSoup extrai os eventos. Tudo roda headless.

**2. Normaliza e classifica**
O normalizador filtra geograficamente para Ribeirão Preto e converte datas para ISO 8601. A Groq API então classifica cada evento em uma das 8 categorias usando `llama-3.3-70b-versatile` — zero regra manual.

**3. Gera e publica**
O renderer lê `events.json` e gera `index.html` com o layout jornal. O deploy no Vercel serve o arquivo estático. Pipeline roda semanalmente.

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Scraping | Python 3.12 · Playwright · BeautifulSoup4 |
| IA | Groq API (`llama-3.3-70b-versatile`) |
| Frontend | HTML/CSS/JS estático · Playfair Display |
| Deploy | Vercel (static) |
| Testes | pytest |

---

## Rodando localmente

### Pré-requisitos

- Python 3.12+
- Conta na [Groq](https://console.groq.com) para obter a API key

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/MiguelRibasBerlese/RadarLinka.git
cd RadarLinka

# 2. Crie e ative o ambiente virtual
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# 3. Instale as dependências
pip install -r scraper/requirements.txt

# 4. Instale o browser headless
playwright install chromium

# 5. Configure as variáveis de ambiente
cp .env.example .env   # ou crie manualmente
```

Edite o `.env` com suas credenciais:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
SHEETS_CSV_URL=https://docs.google.com/spreadsheets/d/.../export?format=csv
SHEETS_META_URL=https://docs.google.com/spreadsheets/d/.../export?format=csv&gid=...
```

```bash
# 6. Rode o pipeline completo (scraping → normalização → classificação → events.json)
python scraper/main.py

# 7. Gere o HTML a partir do events.json
python scraper/renderer.py

# 8. Abra no browser
# Linux/macOS
open web/index.html

# Windows
start web/index.html
```

---

## Testes

```bash
pytest tests/ -v
```

Cobertura atual: **19 testes** distribuídos em 4 módulos.

```
tests/test_scraper.py     — 4 testes  (conectividade e parsing das fontes)
tests/test_normalizer.py  — 7 testes  (filtro geográfico, datas ISO 8601)
tests/test_classifier.py  — 4 testes  (categorização via Groq)
tests/test_renderer.py    — 4 testes  (geração do HTML)
```

---

## Estrutura do projeto

```
radar/
├── .env                      # GROQ_API_KEY, SHEETS_CSV_URL, SHEETS_META_URL
├── .gitignore
├── vercel.json
├── scraper/
│   ├── config.py             # Configurações globais e constantes
│   ├── event_scraper.py      # Playwright + BeautifulSoup, 3 fontes
│   ├── event_normalizer.py   # Filtro geográfico RP, normalização ISO 8601
│   ├── ai_classifier.py      # Groq API, 8 categorias
│   ├── renderer.py           # Lê events.json, gera index.html
│   └── main.py               # Orquestrador do pipeline
├── web/
│   ├── events.json           # Eventos classificados (gerado pelo pipeline)
│   ├── index.html            # Interface jornal (gerada pelo renderer)
│   └── landing.html          # Página de apresentação do produto
└── tests/
    ├── test_scraper.py
    ├── test_normalizer.py
    ├── test_classifier.py
    └── test_renderer.py
```

---

## Fontes de dados

| Fonte | URL | Tipo |
|-------|-----|------|
| Sympla | sympla.com.br | Ingressos e eventos culturais |
| EmRibeirão | emribeirao.com.br | Agenda local |
| RibeirãoShopping | ribeiraoshopping.com.br | Eventos do shopping |

---

## Categorias suportadas

| Categoria | Descrição |
|-----------|-----------|
| 🎵 Shows & Música | Shows, festivais, apresentações ao vivo |
| 🎭 Teatro & Dança | Peças, espetáculos, performances |
| 🎨 Arte & Cultura | Exposições, museus, feiras culturais |
| 🍷 Gastronomia | Festivais gastronômicos, food parks, degustações |
| 🎓 Educação | Cursos, workshops, palestras, seminários |
| 👨‍👩‍👧 Família | Eventos infantis e para toda a família |
| 🏃 Esporte | Corridas, torneios, competições esportivas |
| 🎉 Festas & Baladas | Festas, baladas, eventos noturnos |

---

## Roadmap

### v2 — Ativações de marcas
- Painel para marcas locais patrocinarem categorias
- Destaque visual para eventos patrocinados no layout jornal
- Integração com Google Sheets para gestão editorial manual

### v3 — WhatsApp CRM
- Envio semanal automático da agenda por WhatsApp
- Segmentação por categoria de interesse do usuário
- Opt-in via link direto na landing page

---

## Contribuindo

Pull requests são bem-vindos. Para mudanças grandes, abra uma issue primeiro para discutir o que você quer mudar.

---

## Licença

[MIT](LICENSE) © 2025 Miguel Ribas Berlese
