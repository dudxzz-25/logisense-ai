from pathlib import Path
from functools import lru_cache
from datetime import date
import json

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field


# ============================================================
# CAMINHOS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data" / "raw"

MODEL_PATH = (
    ROOT
    / "backend"
    / "ml"
    / "delay_model.joblib"
)

METRICS_PATH = (
    ROOT
    / "backend"
    / "ml"
    / "metrics.json"
)


# ============================================================
# API
# ============================================================

app = FastAPI(
    title="LogiSense AI API",
    description=(
        "API de inteligência logística com análises "
        "operacionais e Machine Learning."
    ),
    version="0.4.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELO DE ENTRADA DA PREVISÃO
# ============================================================

class DelayPredictionRequest(BaseModel):

    data_pedido: date

    transportadora_id: int = Field(
        ge=1
    )

    cd_id: int = Field(
        ge=1
    )

    rota_id: int = Field(
        ge=1
    )

    valor_frete: float = Field(
        gt=0
    )

    peso_kg: float = Field(
        gt=0
    )

    sla_dias: int = Field(
        ge=1,
        le=30
    )


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

def load():

    entregas = pd.read_csv(
        DATA / "entregas.csv",
        parse_dates=[
            "data_pedido",
            "data_prevista",
            "data_entrega",
        ],
    )


    transportadoras = (
        pd.read_csv(
            DATA / "transportadoras.csv"
        )
        .rename(
            columns={
                "nome": "nome_transportadora"
            }
        )
    )


    rotas = pd.read_csv(
        DATA / "rotas.csv"
    )


    centros = (
        pd.read_csv(
            DATA / "centros_distribuicao.csv"
        )
        .rename(
            columns={
                "nome": "nome_cd",
                "cidade": "cidade_cd",
                "estado": "estado_cd",
            }
        )
    )


    df = (
        entregas
        .merge(
            transportadoras,
            on="transportadora_id",
            how="left",
        )
        .merge(
            rotas,
            on="rota_id",
            how="left",
        )
        .merge(
            centros,
            on="cd_id",
            how="left",
        )
    )


    return df


# ============================================================
# CARREGAMENTO DAS DIMENSÕES
# ============================================================

def load_dimensions():

    transportadoras = (
        pd.read_csv(
            DATA / "transportadoras.csv"
        )
        .rename(
            columns={
                "nome": "nome_transportadora"
            }
        )
    )


    rotas = pd.read_csv(
        DATA / "rotas.csv"
    )


    centros = (
        pd.read_csv(
            DATA / "centros_distribuicao.csv"
        )
        .rename(
            columns={
                "nome": "nome_cd",
                "cidade": "cidade_cd",
                "estado": "estado_cd",
            }
        )
    )


    return (
        transportadoras,
        rotas,
        centros
    )


# ============================================================
# CARREGAMENTO DO MODELO
# ============================================================

@lru_cache
def load_ml_artifact():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Modelo não encontrado em: {MODEL_PATH}"
        )


    return joblib.load(
        MODEL_PATH
    )


# ============================================================
# CLASSIFICAÇÃO DE RISCO
# ============================================================

def get_risk_level(
    score,
    threshold
):

    if score >= threshold + 0.20:

        return "Muito alto"


    if score >= threshold:

        return "Alto"


    if score >= threshold - 0.15:

        return "Moderado"


    return "Baixo"


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "project": "LogiSense AI",
        "status": "online",
        "version": "0.4.0",
        "machine_learning": True,
    }


# ============================================================
# CATÁLOGOS
# ============================================================

@app.get("/catalogos")
def catalogos():

    transportadoras = (
        pd.read_csv(
            DATA / "transportadoras.csv"
        )
        .sort_values("nome")
    )


    centros = (
        pd.read_csv(
            DATA / "centros_distribuicao.csv"
        )
        .sort_values("nome")
    )


    rotas = (
        pd.read_csv(
            DATA / "rotas.csv"
        )
        .sort_values(
            [
                "origem",
                "destino",
            ]
        )
    )


    return {

        "transportadoras": [
            {
                "id": int(
                    row.transportadora_id
                ),
                "nome": row.nome,
                "tipo": row.tipo,
                "estado_sede":
                    row.estado_sede,
            }

            for row
            in transportadoras.itertuples(
                index=False
            )
        ],


        "centros_distribuicao": [
            {
                "id": int(
                    row.cd_id
                ),
                "nome": row.nome,
                "cidade": row.cidade,
                "estado": row.estado,
            }

            for row
            in centros.itertuples(
                index=False
            )
        ],


        "rotas": [
            {
                "id": int(
                    row.rota_id
                ),
                "origem": row.origem,
                "destino": row.destino,
                "distancia_km": float(
                    row.distancia_km
                ),
            }

            for row
            in rotas.itertuples(
                index=False
            )
        ],
    }


# ============================================================
# STATUS DO MACHINE LEARNING
# ============================================================

@app.get("/ml-status")
def ml_status():

    try:

        artifact = load_ml_artifact()


        return {
            "status": "online",
            "modelo_carregado": True,
            "modelo": artifact.get(
                "model_name",
                "desconhecido"
            ),
            "threshold": round(
                float(
                    artifact.get(
                        "threshold",
                        0
                    )
                ),
                4
            ),
        }


    except Exception as error:

        return {
            "status": "erro",
            "modelo_carregado": False,
            "erro": str(error),
        }


# ============================================================
# MÉTRICAS DO MODELO
# ============================================================

@app.get("/model-metrics")
def model_metrics():

    if not METRICS_PATH.exists():

        return {
            "status": "erro",
            "mensagem":
                "Arquivo metrics.json não encontrado."
        }


    try:

        with open(
            METRICS_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            metrics = json.load(
                file
            )


        return metrics


    except Exception as error:

        return {
            "status": "erro",
            "mensagem":
                "Não foi possível carregar as métricas.",
            "erro": str(error),
        }


# ============================================================
# KPIs
# ============================================================

@app.get("/kpis")
def kpis():

    df = load()


    total = len(df)


    atrasadas = int(
        (
            df["atraso_dias"] > 0
        ).sum()
    )


    taxa_atraso = round(
        atrasadas
        / total
        * 100,
        2
    )


    frete_total = round(
        float(
            df[
                "valor_frete"
            ].sum()
        ),
        2
    )


    frete_medio = round(
        float(
            df[
                "valor_frete"
            ].mean()
        ),
        2
    )


    sla = round(
        float(
            (
                df["atraso_dias"]
                == 0
            ).mean()
            * 100
        ),
        2
    )


    return {
        "entregas":
            total,

        "entregas_atrasadas":
            atrasadas,

        "taxa_atraso_pct":
            taxa_atraso,

        "sla_pct":
            sla,

        "custo_frete_total":
            frete_total,

        "custo_frete_medio":
            frete_medio,
    }


# ============================================================
# TRANSPORTADORAS
# ============================================================

@app.get("/transportadoras")
def transportadoras():

    df = load()


    g = (
        df
        .groupby(
            "nome_transportadora",
            as_index=False,
        )
        .agg(
            entregas=(
                "entrega_id",
                "count",
            ),
            atraso_medio=(
                "atraso_dias",
                "mean",
            ),
            custo_medio=(
                "valor_frete",
                "mean",
            ),
        )
    )


    sla = (
        df
        .assign(
            no_prazo=
                df[
                    "atraso_dias"
                ].eq(0)
        )
        .groupby(
            "nome_transportadora",
            as_index=False,
        )
        .agg(
            sla_pct=(
                "no_prazo",
                "mean",
            )
        )
    )


    sla["sla_pct"] = (
        sla["sla_pct"]
        * 100
    )


    g = g.merge(
        sla,
        on="nome_transportadora",
        how="left",
    )


    g = g.sort_values(
        "sla_pct",
        ascending=True,
    )


    return (
        g
        .round(2)
        .to_dict(
            orient="records"
        )
    )


# ============================================================
# ROTAS
# ============================================================

@app.get("/rotas")
def rotas():

    df = load()


    g = (
        df
        .groupby(
            [
                "origem",
                "destino",
            ],
            as_index=False,
        )
        .agg(
            entregas=(
                "entrega_id",
                "count",
            ),
            atraso_medio=(
                "atraso_dias",
                "mean",
            ),
            custo_medio=(
                "valor_frete",
                "mean",
            ),
            distancia_km=(
                "distancia_km",
                "first",
            ),
        )
        .sort_values(
            "atraso_medio",
            ascending=False,
        )
    )


    return (
        g
        .round(2)
        .to_dict(
            orient="records"
        )
    )


# ============================================================
# SÉRIE MENSAL
# ============================================================

@app.get("/serie-mensal")
def serie_mensal():

    df = load()


    df["mes"] = (
        df[
            "data_pedido"
        ]
        .dt
        .to_period("M")
        .astype(str)
    )


    g = (
        df
        .groupby(
            "mes",
            as_index=False,
        )
        .agg(
            entregas=(
                "entrega_id",
                "count",
            ),
            atrasadas=(
                "atraso_dias",
                lambda s:
                    int(
                        (
                            s > 0
                        ).sum()
                    ),
            ),
            custo_frete=(
                "valor_frete",
                "sum",
            ),
        )
    )


    g["taxa_atraso_pct"] = (
        g["atrasadas"]
        / g["entregas"]
        * 100
    ).round(2)


    return (
        g
        .round(2)
        .to_dict(
            orient="records"
        )
    )


# ============================================================
# PREVISÃO DE RISCO DE ATRASO
# ============================================================

@app.post("/predict-delay")
def predict_delay(
    payload: DelayPredictionRequest
):

    try:

        artifact = load_ml_artifact()


    except Exception as error:

        raise HTTPException(
            status_code=503,
            detail=(
                "Não foi possível carregar "
                f"o modelo: {error}"
            )
        )


    model = artifact[
        "model"
    ]


    threshold = float(
        artifact[
            "threshold"
        ]
    )


    model_name = artifact[
        "model_name"
    ]


    (
        transportadoras_df,
        rotas_df,
        centros_df
    ) = load_dimensions()


    # --------------------------------------------------------
    # TRANSPORTADORA
    # --------------------------------------------------------

    transportadora = (
        transportadoras_df[
            transportadoras_df[
                "transportadora_id"
            ]
            == payload.transportadora_id
        ]
    )


    if transportadora.empty:

        raise HTTPException(
            status_code=422,
            detail=(
                "transportadora_id "
                "não encontrado."
            )
        )


    transportadora = (
        transportadora.iloc[0]
    )


    # --------------------------------------------------------
    # CENTRO
    # --------------------------------------------------------

    centro = (
        centros_df[
            centros_df[
                "cd_id"
            ]
            == payload.cd_id
        ]
    )


    if centro.empty:

        raise HTTPException(
            status_code=422,
            detail=
                "cd_id não encontrado."
        )


    centro = (
        centro.iloc[0]
    )


    # --------------------------------------------------------
    # ROTA
    # --------------------------------------------------------

    rota = (
        rotas_df[
            rotas_df[
                "rota_id"
            ]
            == payload.rota_id
        ]
    )


    if rota.empty:

        raise HTTPException(
            status_code=422,
            detail=
                "rota_id não encontrado."
        )


    rota = (
        rota.iloc[0]
    )


    # --------------------------------------------------------
    # FEATURE ENGINEERING
    # --------------------------------------------------------

    distancia_km = float(
        rota[
            "distancia_km"
        ]
    )


    dia_semana = (
        payload
        .data_pedido
        .weekday()
    )


    fim_semana = int(
        dia_semana >= 5
    )


    frete_por_kg = (
        payload.valor_frete
        / max(
            payload.peso_kg,
            0.01
        )
    )


    km_por_dia_sla = (
        distancia_km
        / max(
            payload.sla_dias,
            1
        )
    )


    rota_nome = (
        f"{rota['origem']}"
        f" -> "
        f"{rota['destino']}"
    )


    features = pd.DataFrame(
        [
            {
                "valor_frete":
                    payload.valor_frete,

                "peso_kg":
                    payload.peso_kg,

                "sla_dias":
                    payload.sla_dias,

                "distancia_km":
                    distancia_km,

                "frete_por_kg":
                    frete_por_kg,

                "km_por_dia_sla":
                    km_por_dia_sla,

                "mes":
                    payload
                    .data_pedido
                    .month,

                "dia_semana":
                    dia_semana,

                "fim_semana":
                    fim_semana,

                "transportadora_nome":
                    transportadora[
                        "nome_transportadora"
                    ],

                "cd_nome":
                    centro[
                        "nome_cd"
                    ],

                "rota":
                    rota_nome,
            }
        ]
    )


    score = float(
        model
        .predict_proba(
            features
        )[0][1]
    )


    predicao_atraso = bool(
        score >= threshold
    )


    nivel_risco = (
        get_risk_level(
            score,
            threshold
        )
    )


    return {
        "modelo":
            model_name,

        "score_risco_pct":
            round(
                score * 100,
                2
            ),

        "threshold_pct":
            round(
                threshold * 100,
                2
            ),

        "nivel_risco":
            nivel_risco,

        "predicao_atraso":
            predicao_atraso,

        "transportadora":
            transportadora[
                "nome_transportadora"
            ],

        "centro_distribuicao":
            centro[
                "nome_cd"
            ],

        "rota":
            rota_nome,

        "distancia_km":
            distancia_km,

        "sla_dias":
            payload.sla_dias,
    }