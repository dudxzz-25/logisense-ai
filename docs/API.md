# API Reference — LogiSense AI

Base local:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## GET /

Retorna informações básicas da aplicação.

Exemplo:

```json
{
  "project": "LogiSense AI",
  "status": "online",
  "version": "0.4.0",
  "machine_learning": true
}
```

---

## GET /kpis

Retorna os principais indicadores da operação.

Campos:

- `entregas`
- `entregas_atrasadas`
- `taxa_atraso_pct`
- `sla_pct`
- `custo_frete_total`
- `custo_frete_medio`

---

## GET /transportadoras

Retorna métricas agregadas por transportadora.

Campos principais:

- `nome_transportadora`
- `entregas`
- `atraso_medio`
- `custo_medio`
- `sla_pct`

---

## GET /rotas

Retorna métricas agregadas por rota.

Campos principais:

- `origem`
- `destino`
- `entregas`
- `atraso_medio`
- `custo_medio`
- `distancia_km`

---

## GET /serie-mensal

Retorna a evolução mensal da operação.

Campos:

- `mes`
- `entregas`
- `atrasadas`
- `custo_frete`
- `taxa_atraso_pct`

---

## GET /catalogos

Retorna os dados utilizados nos selects dinâmicos do frontend.

Estrutura:

```json
{
  "transportadoras": [],
  "centros_distribuicao": [],
  "rotas": []
}
```

---

## GET /ml-status

Informa se o artefato de ML foi carregado corretamente.

Exemplo:

```json
{
  "status": "online",
  "modelo_carregado": true,
  "modelo": "LogisticRegression",
  "threshold": 0.5444
}
```

---

## GET /model-metrics

Retorna o conteúdo do arquivo `backend/ml/metrics.json`.

Inclui:

- modelo selecionado;
- threshold;
- baseline;
- métricas do teste;
- métricas dos modelos na validação;
- períodos de treino, validação e teste;
- features.

---

## POST /predict-delay

Executa a inferência de risco de atraso.

### Request

```json
{
  "data_pedido": "2026-09-24",
  "transportadora_id": 5,
  "cd_id": 2,
  "rota_id": 3,
  "valor_frete": 980,
  "peso_kg": 780,
  "sla_dias": 1
}
```

### Validações

- `transportadora_id >= 1`
- `cd_id >= 1`
- `rota_id >= 1`
- `valor_frete > 0`
- `peso_kg > 0`
- `1 <= sla_dias <= 30`

Os IDs também precisam existir nos catálogos carregados pela API.

### Response

```json
{
  "modelo": "LogisticRegression",
  "score_risco_pct": 89.48,
  "threshold_pct": 54.44,
  "nivel_risco": "Muito alto",
  "predicao_atraso": true,
  "transportadora": "VelozOne",
  "centro_distribuicao": "CD Cajamar",
  "rota": "São Paulo/SP -> Belo Horizonte/MG",
  "distancia_km": 590,
  "sla_dias": 1
}
```

### Erros possíveis

- `422`: payload inválido ou ID inexistente;
- `503`: artefato do modelo não pôde ser carregado.
