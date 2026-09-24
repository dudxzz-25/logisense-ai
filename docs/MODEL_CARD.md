# Model Card — LogiSense AI Delay Risk

## Visão geral

O modelo de Machine Learning do LogiSense AI classifica o **risco de atraso** de uma nova entrega a partir de características operacionais conhecidas antes da conclusão da entrega.

O objetivo é demonstrar um fluxo completo de ML aplicado a logística: preparação dos dados, feature engineering, divisão temporal, comparação de algoritmos, seleção de threshold, persistência do modelo e inferência via API.

> Este modelo foi treinado com **dados sintéticos** e deve ser interpretado como demonstração de portfólio, não como sistema de decisão em produção.

---

## Problema

### Target

```python
atrasou = atraso_dias > 0
```

- `0`: entrega sem atraso;
- `1`: entrega com atraso.

### Tipo de problema

Classificação binária supervisionada com classes desbalanceadas.

---

## Dados

Período total utilizado no experimento:

```text
01/01/2025 a 23/09/2026
```

Divisão cronológica:

| Conjunto | Proporção | Período |
|---|---:|---|
| Treino | 70% | 01/01/2025 a 21/03/2026 |
| Validação | 15% | 21/03/2026 a 23/06/2026 |
| Teste | 15% | 23/06/2026 a 23/09/2026 |

A separação temporal foi utilizada para aproximar um cenário real em que o modelo aprende com dados anteriores e é avaliado em dados futuros.

---

## Features

### Numéricas

- `valor_frete`
- `peso_kg`
- `sla_dias`
- `distancia_km`
- `frete_por_kg`
- `km_por_dia_sla`
- `mes`
- `dia_semana`
- `fim_semana`

### Categóricas

- `transportadora_nome`
- `cd_nome`
- `rota`

### Features derivadas

```python
frete_por_kg = valor_frete / peso_kg
km_por_dia_sla = distancia_km / sla_dias
```

Informações temporais também são extraídas da data do pedido.

---

## Pipeline

As variáveis numéricas passam por `StandardScaler`.

As variáveis categóricas são transformadas com `OneHotEncoder(handle_unknown="ignore")`.

Foram avaliados:

- Logistic Regression;
- Random Forest;
- Extra Trees.

A métrica principal de comparação no conjunto de validação foi **PR-AUC**, por ser útil em cenários com classe positiva menos frequente.

---

## Validação

| Modelo | ROC-AUC | PR-AUC | F1 | Recall |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.7160 | 0.4099 | 0.4735 | 0.6840 |
| Random Forest | 0.7028 | 0.4017 | 0.4463 | 0.4519 |
| Extra Trees | 0.7044 | 0.4067 | 0.4572 | 0.5605 |

Modelo selecionado:

```text
LogisticRegression
```

---

## Threshold

O threshold de decisão foi otimizado no conjunto de validação para maximizar o F1-score.

```text
threshold = 0.5444
```

Após a seleção, o modelo escolhido é retreinado com treino + validação e avaliado uma única vez no conjunto de teste.

---

## Resultado final

| Métrica | Valor |
|---|---:|
| Accuracy | 0.6783 |
| Balanced Accuracy | 0.6544 |
| Precision | 0.3464 |
| Recall | 0.6133 |
| F1-score | 0.4427 |
| ROC-AUC | 0.7127 |
| PR-AUC | 0.3741 |

Matriz de confusão:

```text
[[991, 434],
 [145, 230]]
```

O conjunto de teste possui **1.800 registros**.

Baseline de accuracy da classe majoritária:

```text
0.7917
```

Por isso, accuracy não é usada isoladamente para julgar o modelo. Recall, F1, PR-AUC e Balanced Accuracy ajudam a avaliar melhor a capacidade de identificar atrasos.

---

## Saída da API

O endpoint `POST /predict-delay` retorna um **score de risco**.

Exemplo:

```json
{
  "modelo": "LogisticRegression",
  "score_risco_pct": 89.48,
  "threshold_pct": 54.44,
  "nivel_risco": "Muito alto",
  "predicao_atraso": true
}
```

### Importante

`score_risco_pct` **não deve ser interpretado como probabilidade calibrada**.

No projeto, o valor é usado como score relativo para comparar o resultado com o threshold de decisão e construir faixas de risco.

---

## Faixas de risco

A API utiliza o threshold salvo junto com o artefato do modelo:

| Faixa | Regra |
|---|---|
| Baixo | score < threshold - 0.15 |
| Moderado | threshold - 0.15 ≤ score < threshold |
| Alto | threshold ≤ score < threshold + 0.20 |
| Muito alto | score ≥ threshold + 0.20 |

---

## Limitações

- dados totalmente sintéticos;
- ausência de variáveis externas como clima, trânsito e feriados;
- score não calibrado como probabilidade;
- não há explicabilidade por predição;
- não há monitoramento de drift;
- não há retreinamento automático;
- não foi realizado teste em dados de uma operação real.

---

## Possíveis evoluções

- calibração probabilística;
- SHAP ou outra técnica de explicabilidade;
- avaliação de custo de falso positivo/falso negativo;
- monitoramento de data drift;
- monitoramento de model drift;
- validação em dados reais;
- pipeline automatizado de retreinamento.
