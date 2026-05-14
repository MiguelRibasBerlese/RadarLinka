# RADAR — Agregador Inteligente de Eventos

[![Deploy](https://img.shields.io/badge/deploy-live-brightgreen?style=flat-square&logo=vercel)](https://radar-olive-five.vercel.app)
[![Python](https://img.shields.io/badge/python-3.12-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)](LICENSE)

Agrega, normaliza e classifica automaticamente eventos de Ribeirão Preto e região — entregando tudo numa interface estática sem banco de dados.

**Produção:** [radar-olive-five.vercel.app](https://radar-olive-five.vercel.app)

---

## Como funciona

```
Scraping (8 fontes)
    │
    ▼
Normalização + Filtro geográfico
    │
    ▼
Deduplicação (URL + título)
    │
    ▼
Classificação híbrida
    ├─ Regras (palavras-chave) → maioria dos eventos
    └─ Groq llama-3.3-70b → apenas ambíguos
    │
    ▼
public/data/events.json
    │
    ▼
Frontend estático (Vercel)
```

O pipeline roda manualmente (`python -m pipeline.run`). O frontend lê `events.json` via fetch e renderiza os cards no browser — sem servidor, sem banco.

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Scraping | Python 3.12 · Playwright · BeautifulSoup4 · Requests |
| IA | Groq API (`llama-3.3-70b-versatile`) |
| Frontend | HTML/CSS/JS vanilla · Three.js · Outfit (Google Fonts) |
| Chatbot | ORBIT — serverless Python (`/api/chat.py`) + Groq |
| Deploy | Vercel (static + Python serverless) |

---

## Fontes de dados

| Fonte | Cobertura |
|-------|-----------|
| Sympla | 24 cidades (Ribeirão Preto + região até 200km) |
| EmRibeirão | Agenda local |
| RibeirãoShopping | Shopping centers |
| Eventoon | Plataforma regional |
| Sindtur | Turismo regional |
| Songkick | Shows nacionais com data em RP |
| Varal | Eventos culturais |
| SearchAPI (Google Events) | Cobertura complementar |

---

## Categorias

`Show` `Festa` `Feira` `Festival` `Teatro` `Esporte` `Corporativo` `Curso` `Exposição` `Religioso` `Turismo` `Infantil` `Outro`

A classificação usa regras de palavras-chave primeiro; só eventos ambíguos chegam à Groq API.

---

## Estrutura do projeto

```
radar/
├── pipeline/                   # Pipeline de dados
│   ├── run.py                  # Orquestrador principal
│   ├── settings.py             # Configurações e constantes
│   ├── sources/                # Scrapers por fonte
│   │   ├── sympla.py           # Playwright — 24 slugs de cidades
│   │   ├── emribeirao.py
│   │   ├── shopping.py
│   │   ├── eventoon.py
│   │   ├── sindtur.py
│   │   ├── songkick.py
│   │   ├── varal.py
│   │   └── searchapi.py        # Google Events via SearchAPI
│   ├── processors/
│   │   ├── normalizer.py       # Filtro geográfico + data ISO 8601
│   │   └── classifier.py       # Regras + Groq (com backoff e detecção TPD)
│   └── storage/
│       └── data_store.py       # Salva events.json ordenado por data
│
├── public/                     # Frontend (outputDirectory do Vercel)
│   ├── index.html
│   ├── css/styles.css
│   ├── js/
│   │   ├── app.js              # Filtros, render progressivo, busca
│   │   ├── loading.js          # Globo Three.js + starfield canvas
│   │   ├── chat.js             # ORBIT chatbot
│   │   ├── theme.js            # Dark/light mode
│   │   └── three.min.js        # Three.js r128 (local)
│   ├── data/events.json        # Gerado pelo pipeline
│   └── assets/
│       ├── images/
│       └── textures/           # nightmap.jpg, specular.png
│
├── api/
│   └── chat.py                 # Serverless — ORBIT (Groq)
│
├── vercel.json                 # outputDirectory: public, rota /api/chat
├── requirements.txt
└── .env                        # GROQ_API_KEY, SEARCHAPI_KEY
```

---

## Rodando localmente

### Pré-requisitos

- Python 3.12+
- Conta na [Groq](https://console.groq.com) (free tier: 100k tokens/dia)
- Conta na [SearchAPI](https://www.searchapi.io) (opcional — Google Events)

### Instalação

```bash
git clone https://github.com/MiguelRibasBerlese/RadarLinka.git
cd RadarLinka

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### Variáveis de ambiente

Crie um `.env` na raiz:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
SEARCHAPI_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx   # opcional
```

### Rodando o pipeline

```bash
# Windows (necessário para caracteres UTF-8 no terminal)
$env:PYTHONIOENCODING='utf-8'; python -m pipeline.run

# Linux/macOS
python -m pipeline.run
```

O pipeline passa por 3 etapas com barra de progresso:

```
ETAPA 1/3 — Coleta (~8 fontes, ~10min)
ETAPA 2/3 — Normalização e Filtro
ETAPA 3/3 — Classificação por IA (~2s por evento ambíguo)
```

Resultado salvo em `public/data/events.json`, ordenado por data.

> **Limite diário Groq:** o free tier tem 100k tokens/dia. Se o limite for atingido durante a classificação, o pipeline para imediatamente e salva o que já foi processado — sem desperdiçar tempo em backoff inútil.

### Visualizando o frontend

Abra `public/index.html` diretamente no browser, ou sirva com qualquer servidor estático:

```bash
cd public && python -m http.server 8000
# acesse http://localhost:8000
```

---

## Deploy

O projeto usa integração GitHub → Vercel. Cada push para `main` triggera um deploy automático.

Para atualizar os eventos em produção:

```bash
# 1. Rode o pipeline
$env:PYTHONIOENCODING='utf-8'; python -m pipeline.run

# 2. Commite e suba o events.json gerado
git add public/data/events.json
git commit -m "chore: atualizar eventos"
git push origin main
```

---

## Features do frontend

- **Loading screen** com globo 3D (Three.js) e starfield canvas
- **Filtros** colapsáveis: data (hoje/fim de semana/semana/mês), categoria, região, busca textual
- **Chips de filtros ativos** removíveis individualmente
- **Render progressivo** — 40 cards por vez via IntersectionObserver
- **Dark/light mode** com preferência salva no localStorage
- **ORBIT** — chatbot integrado alimentado pela Groq
- **Acessível** — navegação por teclado nos cards, aria-pressed nos chips, aria-label no chat

---

## Licença

[MIT](LICENSE) © 2025 Miguel Ribas Berlese
