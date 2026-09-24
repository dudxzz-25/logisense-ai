from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ============================================================
# CAMINHOS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw"

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "delay_model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"


# ============================================================
# DADOS
# ============================================================

print("\n============================================")
print(" LogiSense AI - Machine Learning V2")
print("============================================\n")


entregas = pd.read_csv(
    DATA_DIR / "entregas.csv",
    parse_dates=[
        "data_pedido",
        "data_prevista",
        "data_entrega",
    ],
)

transportadoras = pd.read_csv(
    DATA_DIR / "transportadoras.csv"
).rename(
    columns={
        "nome": "transportadora_nome"
    }
)

rotas = pd.read_csv(
    DATA_DIR / "rotas.csv"
)

centros = pd.read_csv(
    DATA_DIR / "centros_distribuicao.csv"
).rename(
    columns={
        "nome": "cd_nome",
        "cidade": "cd_cidade",
        "estado": "cd_estado",
    }
)


df = (
    entregas
    .merge(
        transportadoras,
        on="transportadora_id",
        how="left"
    )
    .merge(
        rotas,
        on="rota_id",
        how="left"
    )
    .merge(
        centros,
        on="cd_id",
        how="left"
    )
)


# ============================================================
# TARGET
# ============================================================

df["atrasou"] = (
    df["atraso_dias"] > 0
).astype(int)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

df["rota"] = (
    df["origem"]
    + " -> "
    + df["destino"]
)


df["mes"] = (
    df["data_pedido"]
    .dt.month
)


df["dia_semana"] = (
    df["data_pedido"]
    .dt.dayofweek
)


df["fim_semana"] = (
    df["dia_semana"] >= 5
).astype(int)


df["frete_por_kg"] = (
    df["valor_frete"]
    / df["peso_kg"].clip(lower=0.01)
)


df["km_por_dia_sla"] = (
    df["distancia_km"]
    / df["sla_dias"].clip(lower=1)
)


# ============================================================
# FEATURES
# ============================================================

numeric_features = [
    "valor_frete",
    "peso_kg",
    "sla_dias",
    "distancia_km",
    "frete_por_kg",
    "km_por_dia_sla",
    "mes",
    "dia_semana",
    "fim_semana",
]


categorical_features = [
    "transportadora_nome",
    "cd_nome",
    "rota",
]


feature_columns = (
    numeric_features
    + categorical_features
)


df_model = (
    df[
        feature_columns
        + [
            "atrasou",
            "data_pedido"
        ]
    ]
    .sort_values("data_pedido")
    .reset_index(drop=True)
)


# ============================================================
# DIVISÃO TEMPORAL
#
# 70% treino
# 15% validação
# 15% teste
# ============================================================

n = len(df_model)

train_end = int(n * 0.70)
validation_end = int(n * 0.85)


train = df_model.iloc[
    :train_end
].copy()


validation = df_model.iloc[
    train_end:validation_end
].copy()


test = df_model.iloc[
    validation_end:
].copy()


X_train = train[feature_columns]
y_train = train["atrasou"]

X_validation = validation[feature_columns]
y_validation = validation["atrasou"]

X_test = test[feature_columns]
y_test = test["atrasou"]


print(
    f"Treino:     "
    f"{train['data_pedido'].min().date()} "
    f"até "
    f"{train['data_pedido'].max().date()} "
    f"({len(train)} registros)"
)

print(
    f"Validação:  "
    f"{validation['data_pedido'].min().date()} "
    f"até "
    f"{validation['data_pedido'].max().date()} "
    f"({len(validation)} registros)"
)

print(
    f"Teste:      "
    f"{test['data_pedido'].min().date()} "
    f"até "
    f"{test['data_pedido'].max().date()} "
    f"({len(test)} registros)"
)


# ============================================================
# PRÉ-PROCESSAMENTO
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            StandardScaler(),
            numeric_features,
        ),
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features,
        ),
    ]
)


# ============================================================
# MODELOS
# ============================================================

models = {

    "LogisticRegression":
        LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            solver="liblinear",
            random_state=42,
        ),

    "RandomForest":
        RandomForestClassifier(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=4,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),

    "ExtraTrees":
        ExtraTreesClassifier(
            n_estimators=400,
            min_samples_leaf=4,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
}


# ============================================================
# FUNÇÃO DE MÉTRICAS
# ============================================================

def evaluate(
    y_true,
    probabilities,
    threshold=0.5
):

    predictions = (
        probabilities >= threshold
    ).astype(int)

    return {

        "accuracy":
            accuracy_score(
                y_true,
                predictions
            ),

        "balanced_accuracy":
            balanced_accuracy_score(
                y_true,
                predictions
            ),

        "precision":
            precision_score(
                y_true,
                predictions,
                zero_division=0
            ),

        "recall":
            recall_score(
                y_true,
                predictions,
                zero_division=0
            ),

        "f1":
            f1_score(
                y_true,
                predictions,
                zero_division=0
            ),

        "roc_auc":
            roc_auc_score(
                y_true,
                probabilities
            ),

        "pr_auc":
            average_precision_score(
                y_true,
                probabilities
            ),

        "confusion_matrix":
            confusion_matrix(
                y_true,
                predictions
            ).tolist()
    }


# ============================================================
# TREINAR E COMPARAR MODELOS
# ============================================================

results = {}

trained_models = {}


print("\n============================================")
print(" COMPARAÇÃO DE MODELOS")
print("============================================")


for name, classifier in models.items():

    print(
        f"\nTreinando {name}..."
    )


    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "classifier",
                classifier
            )
        ]
    )


    pipeline.fit(
        X_train,
        y_train
    )


    probabilities = (
        pipeline.predict_proba(
            X_validation
        )[:, 1]
    )


    metrics = evaluate(
        y_validation,
        probabilities,
        threshold=0.5
    )


    results[name] = metrics

    trained_models[name] = pipeline


    print(
        f"ROC-AUC: {metrics['roc_auc']:.4f}"
    )

    print(
        f"PR-AUC:  {metrics['pr_auc']:.4f}"
    )

    print(
        f"F1:      {metrics['f1']:.4f}"
    )

    print(
        f"Recall:  {metrics['recall']:.4f}"
    )


# ============================================================
# MELHOR MODELO
#
# Escolha usando PR-AUC, mais apropriado para
# classificação desbalanceada.
# ============================================================

best_model_name = max(
    results,
    key=lambda name:
        results[name]["pr_auc"]
)


best_model = trained_models[
    best_model_name
]


print("\n============================================")

print(
    f"Melhor modelo na validação: "
    f"{best_model_name}"
)

print("============================================")


# ============================================================
# OTIMIZAÇÃO DO THRESHOLD
#
# Escolhido somente na validação.
# ============================================================

validation_probabilities = (
    best_model.predict_proba(
        X_validation
    )[:, 1]
)


precision_values, recall_values, thresholds = (
    precision_recall_curve(
        y_validation,
        validation_probabilities
    )
)


f1_values = (
    2
    * precision_values[:-1]
    * recall_values[:-1]
    / (
        precision_values[:-1]
        + recall_values[:-1]
        + 1e-10
    )
)


best_index = np.argmax(
    f1_values
)


best_threshold = float(
    thresholds[best_index]
)


print(
    f"\nThreshold selecionado: "
    f"{best_threshold:.4f}"
)


print(
    f"F1 de validação no threshold: "
    f"{f1_values[best_index]:.4f}"
)


# ============================================================
# TREINO FINAL
#
# Agora usamos treino + validação.
# O teste continua intocado.
# ============================================================

train_final = pd.concat(
    [
        train,
        validation
    ],
    ignore_index=True
)


X_train_final = (
    train_final[
        feature_columns
    ]
)


y_train_final = (
    train_final[
        "atrasou"
    ]
)


final_classifier = models[
    best_model_name
]


final_model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            final_classifier
        ),
    ]
)


print("\nTreinando modelo final...")


final_model.fit(
    X_train_final,
    y_train_final
)


# ============================================================
# TESTE FINAL
# ============================================================

test_probabilities = (
    final_model.predict_proba(
        X_test
    )[:, 1]
)


test_metrics = evaluate(
    y_test,
    test_probabilities,
    threshold=best_threshold
)


baseline_accuracy = float(
    y_test
    .value_counts(
        normalize=True
    )
    .max()
)


print("\n============================================")
print(" RESULTADO FINAL NO TESTE")
print("============================================")


print(
    f"\nModelo:             "
    f"{best_model_name}"
)


print(
    f"Threshold:          "
    f"{best_threshold:.4f}"
)


print(
    f"Accuracy:           "
    f"{test_metrics['accuracy']:.4f}"
)


print(
    f"Balanced Accuracy:  "
    f"{test_metrics['balanced_accuracy']:.4f}"
)


print(
    f"Precision:          "
    f"{test_metrics['precision']:.4f}"
)


print(
    f"Recall:             "
    f"{test_metrics['recall']:.4f}"
)


print(
    f"F1-score:           "
    f"{test_metrics['f1']:.4f}"
)


print(
    f"ROC-AUC:            "
    f"{test_metrics['roc_auc']:.4f}"
)


print(
    f"PR-AUC:             "
    f"{test_metrics['pr_auc']:.4f}"
)


print(
    f"Baseline Accuracy:  "
    f"{baseline_accuracy:.4f}"
)


print("\nMatriz de confusão:")

print(
    np.array(
        test_metrics[
            "confusion_matrix"
        ]
    )
)


# ============================================================
# SALVAR MODELO + CONFIGURAÇÃO
# ============================================================

artifact = {

    "model":
        final_model,

    "threshold":
        best_threshold,

    "model_name":
        best_model_name,

    "features":
        feature_columns,
}


joblib.dump(
    artifact,
    MODEL_PATH
)


# ============================================================
# SALVAR MÉTRICAS
# ============================================================

metrics_json = {

    "versao": "2.0",

    "modelo":
        best_model_name,

    "threshold":
        round(
            best_threshold,
            4
        ),

    "baseline_accuracy":
        round(
            baseline_accuracy,
            4
        ),

    "test_metrics": {

        key:
            round(float(value), 4)
            if key != "confusion_matrix"
            else value

        for key, value
        in test_metrics.items()
    },

    "modelos_validacao": {

        model_name: {

            metric:
                round(float(value), 4)
                if metric
                != "confusion_matrix"
                else value

            for metric, value
            in model_metrics.items()
        }

        for model_name, model_metrics
        in results.items()
    },

    "periodos": {

        "treino_inicio":
            str(
                train[
                    "data_pedido"
                ].min().date()
            ),

        "treino_fim":
            str(
                train[
                    "data_pedido"
                ].max().date()
            ),

        "validacao_inicio":
            str(
                validation[
                    "data_pedido"
                ].min().date()
            ),

        "validacao_fim":
            str(
                validation[
                    "data_pedido"
                ].max().date()
            ),

        "teste_inicio":
            str(
                test[
                    "data_pedido"
                ].min().date()
            ),

        "teste_fim":
            str(
                test[
                    "data_pedido"
                ].max().date()
            ),
    },

    "features":
        feature_columns,
}


with open(
    METRICS_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        metrics_json,
        file,
        ensure_ascii=False,
        indent=4
    )


print("\n============================================")

print(
    f"Modelo V2 salvo em:\n"
    f"{MODEL_PATH}"
)

print(
    f"\nMétricas salvas em:\n"
    f"{METRICS_PATH}"
)

print("============================================\n")