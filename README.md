# LogiSense AI

**Logistics Intelligence & Operations Copilot**

Projeto de portfólio para análise de operações logísticas com **Python, SQL, FastAPI, dashboard web e IA**.

## Objetivo

Construir uma aplicação que permita:

- acompanhar KPIs logísticos;
- investigar atrasos, SLA, custos e ocorrências;
- comparar transportadoras, rotas e centros de distribuição;
- consultar os dados em linguagem natural;
- gerar respostas e visualizações orientadas por dados.

## MVP - Fase 1

Nesta primeira versão já temos:

- geração de dados sintéticos;
- schema SQL relacional;
- API em FastAPI;
- endpoints de KPIs, transportadoras, rotas e séries temporais;
- dashboard web inicial;
- base pronta para adicionar o **Modo IA**.

## Estrutura

```text
logisense-ai/
├── backend/
│   ├── app/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── sql/
│   └── schema.sql
├── generate_data.py
└── README.md
```

## Como executar

### 1. Gerar os dados

```bash
python generate_data.py
```

### 2. Iniciar a API

```bash
cd backend
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API ficará em:

```text
http://127.0.0.1:8000
```

Documentação automática:

```text
http://127.0.0.1:8000/docs
```

### 3. Abrir o dashboard

Com a API rodando, abra `frontend/index.html` no navegador.

## Próximas fases

1. Persistir dados em PostgreSQL.
2. Criar modelo estrela analítico.
3. Adicionar filtros e gráficos avançados.
4. Implementar o Modo IA.
5. Criar geração dinâmica de gráficos.
6. Adicionar detecção de anomalias e previsão.
7. Dockerizar e publicar o projeto.
