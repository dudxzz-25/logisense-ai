from pathlib import Path
import csv
import math
import random
from datetime import date, timedelta


# ============================================================
# CONFIGURAÇÃO
# ============================================================

random.seed(42)

ROOT = Path(__file__).resolve().parent

OUT = ROOT / "data" / "raw"

OUT.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DIMENSÕES
# ============================================================

transportadoras = [
    (
        1,
        "RotaSul Logística",
        "Rodoviária",
        "SP",
    ),
    (
        2,
        "MoveXpress",
        "Rodoviária",
        "PR",
    ),
    (
        3,
        "Nexa Cargo",
        "Rodoviária",
        "MG",
    ),
    (
        4,
        "Atlas Transportes",
        "Rodoviária",
        "SC",
    ),
    (
        5,
        "VelozOne",
        "Rodoviária",
        "GO",
    ),
]


centros = [
    (
        1,
        "CD Guarulhos",
        "Guarulhos",
        "SP",
    ),
    (
        2,
        "CD Cajamar",
        "Cajamar",
        "SP",
    ),
    (
        3,
        "CD Campinas",
        "Campinas",
        "SP",
    ),
    (
        4,
        "CD Curitiba",
        "Curitiba",
        "PR",
    ),
]


rotas = [
    (
        1,
        "São Paulo/SP",
        "Rio de Janeiro/RJ",
        430,
    ),
    (
        2,
        "São Paulo/SP",
        "Campinas/SP",
        100,
    ),
    (
        3,
        "São Paulo/SP",
        "Belo Horizonte/MG",
        590,
    ),
    (
        4,
        "Curitiba/PR",
        "São Paulo/SP",
        410,
    ),
    (
        5,
        "Campinas/SP",
        "Ribeirão Preto/SP",
        220,
    ),
    (
        6,
        "São Paulo/SP",
        "Curitiba/PR",
        410,
    ),
    (
        7,
        "São Paulo/SP",
        "Santos/SP",
        80,
    ),
    (
        8,
        "São Paulo/SP",
        "Sorocaba/SP",
        100,
    ),
]


# ============================================================
# SALVAR DIMENSÕES
# ============================================================

with open(
    OUT / "transportadoras.csv",
    "w",
    newline="",
    encoding="utf-8",
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "transportadora_id",
            "nome",
            "tipo",
            "estado_sede",
        ]
    )

    writer.writerows(
        transportadoras
    )


with open(
    OUT / "centros_distribuicao.csv",
    "w",
    newline="",
    encoding="utf-8",
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "cd_id",
            "nome",
            "cidade",
            "estado",
        ]
    )

    writer.writerows(
        centros
    )


with open(
    OUT / "rotas.csv",
    "w",
    newline="",
    encoding="utf-8",
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "rota_id",
            "origem",
            "destino",
            "distancia_km",
        ]
    )

    writer.writerows(
        rotas
    )


# ============================================================
# PERFIS DE RISCO
#
# Valores usados somente pelo SIMULADOR.
# Eles representam diferenças operacionais fictícias.
# ============================================================

risco_transportadora = {
    1: -0.25,
    2: -0.10,
    3: 0.05,
    4: 0.20,
    5: 0.35,
}


risco_cd = {
    1: -0.05,
    2: 0.10,
    3: 0.00,
    4: 0.12,
}


risco_rota = {
    1: 0.08,
    2: -0.08,
    3: 0.22,
    4: 0.06,
    5: 0.02,
    6: 0.10,
    7: -0.12,
    8: -0.06,
}


risco_sla = {
    1: 0.65,
    2: 0.30,
    3: 0.05,
    4: -0.12,
    5: -0.25,
}


# ============================================================
# FUNÇÕES
# ============================================================

def sigmoid(value):

    return (
        1
        / (
            1
            + math.exp(-value)
        )
    )


def calcular_probabilidade_atraso(
    pedido,
    rota,
    transportadora,
    cd,
    sla,
    peso,
):

    # --------------------------------------------------------
    # Risco base
    # --------------------------------------------------------

    score = -2.00


    # --------------------------------------------------------
    # Transportadora
    # --------------------------------------------------------

    score += risco_transportadora[
        transportadora[0]
    ]


    # --------------------------------------------------------
    # Centro de distribuição
    # --------------------------------------------------------

    score += risco_cd[
        cd[0]
    ]


    # --------------------------------------------------------
    # Rota específica
    # --------------------------------------------------------

    score += risco_rota[
        rota[0]
    ]


    # --------------------------------------------------------
    # Distância
    #
    # Rotas mais longas apresentam maior exposição
    # operacional.
    # --------------------------------------------------------

    distancia = rota[3]

    score += (
        (distancia - 250)
        / 300
    )


    # --------------------------------------------------------
    # SLA
    #
    # Prazos mais apertados aumentam o risco.
    # --------------------------------------------------------

    score += risco_sla[
        sla
    ]


    # --------------------------------------------------------
    # Peso
    # --------------------------------------------------------

    if peso > 700:

        score += 0.22

    elif peso > 400:

        score += 0.08


    # --------------------------------------------------------
    # Dia da semana
    #
    # Pequeno aumento de risco próximo ao fim de semana.
    # --------------------------------------------------------

    dia_semana = (
        pedido.weekday()
    )

    if dia_semana == 4:

        score += 0.12

    elif dia_semana >= 5:

        score += 0.18


    # --------------------------------------------------------
    # Sazonalidade
    # --------------------------------------------------------

    mes = pedido.month

    if mes in [11, 12]:

        score += 0.18

    elif mes in [1, 2]:

        score += 0.08


    # --------------------------------------------------------
    # Converter score em probabilidade
    # --------------------------------------------------------

    probabilidade = sigmoid(
        score
    )


    # Evita extremos irreais.

    probabilidade = max(
        0.03,
        min(
            probabilidade,
            0.75
        )
    )


    return probabilidade


# ============================================================
# GERAR ENTREGAS
# ============================================================

start = date(
    2025,
    1,
    1
)


rows = []


for entrega_id in range(
    1,
    12001
):

    # --------------------------------------------------------
    # Dados conhecidos antes da entrega
    # --------------------------------------------------------

    pedido = (
        start
        + timedelta(
            days=random.randint(
                0,
                630
            )
        )
    )


    rota = random.choice(
        rotas
    )


    transportadora = (
        random.choice(
            transportadoras
        )
    )


    cd = random.choice(
        centros
    )


    sla = random.choice(
        [
            1,
            2,
            2,
            3,
            3,
            4,
            5,
        ]
    )


    peso = round(
        random.uniform(
            5,
            900
        ),
        2
    )


    # --------------------------------------------------------
    # Valor do frete
    # --------------------------------------------------------

    valor_frete = round(

        25

        + rota[3]
        * random.uniform(
            0.9,
            2.1
        )

        + peso
        * random.uniform(
            0.03,
            0.12
        ),

        2
    )


    # --------------------------------------------------------
    # Probabilidade de atraso
    # --------------------------------------------------------

    atraso_prob = (
        calcular_probabilidade_atraso(
            pedido=pedido,
            rota=rota,
            transportadora=transportadora,
            cd=cd,
            sla=sla,
            peso=peso,
        )
    )


    atrasou = (
        random.random()
        < atraso_prob
    )


    # --------------------------------------------------------
    # Gravidade do atraso
    # --------------------------------------------------------

    if atrasou:

        if atraso_prob >= 0.50:

            atraso = random.choices(
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                    7,
                ],
                weights=[
                    10,
                    20,
                    24,
                    20,
                    16,
                    10,
                ],
                k=1,
            )[0]

        elif atraso_prob >= 0.30:

            atraso = random.choices(
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                ],
                weights=[
                    25,
                    30,
                    22,
                    15,
                    8,
                ],
                k=1,
            )[0]

        else:

            atraso = random.choices(
                [
                    1,
                    2,
                    3,
                ],
                weights=[
                    55,
                    32,
                    13,
                ],
                k=1,
            )[0]

    else:

        atraso = 0


    # --------------------------------------------------------
    # Datas
    # --------------------------------------------------------

    prevista = (
        pedido
        + timedelta(
            days=sla
        )
    )


    entregue = (
        prevista
        + timedelta(
            days=atraso
        )
    )


    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status = (

        "Entregue com atraso"

        if atraso > 0

        else "Entregue no prazo"

    )


    # --------------------------------------------------------
    # Ocorrências
    #
    # Geradas APÓS o resultado da entrega.
    # Por isso não devem ser usadas para previsão.
    # --------------------------------------------------------

    ocorrencias = [
        "Sem ocorrência",
        "Trânsito intenso",
        "Avaria",
        "Falha operacional",
        "Endereço incorreto",
        "Restrição de acesso",
        "Problema mecânico",
    ]


    if atrasou:

        ocorrencia = random.choices(
            ocorrencias,
            weights=[
                34,
                18,
                9,
                13,
                8,
                8,
                10,
            ],
            k=1,
        )[0]

    else:

        ocorrencia = random.choices(
            ocorrencias,
            weights=[
                91,
                3,
                1,
                2,
                1,
                1,
                1,
            ],
            k=1,
        )[0]


    # --------------------------------------------------------
    # Linha
    # --------------------------------------------------------

    rows.append(
        [
            entrega_id,
            pedido.isoformat(),
            prevista.isoformat(),
            entregue.isoformat(),
            transportadora[0],
            cd[0],
            rota[0],
            valor_frete,
            peso,
            status,
            ocorrencia,
            sla,
            atraso,
        ]
    )


# ============================================================
# SALVAR ENTREGAS
# ============================================================

with open(
    OUT / "entregas.csv",
    "w",
    newline="",
    encoding="utf-8",
) as file:

    writer = csv.writer(
        file
    )


    writer.writerow(
        [
            "entrega_id",
            "data_pedido",
            "data_prevista",
            "data_entrega",
            "transportadora_id",
            "cd_id",
            "rota_id",
            "valor_frete",
            "peso_kg",
            "status",
            "ocorrencia",
            "sla_dias",
            "atraso_dias",
        ]
    )


    writer.writerows(
        rows
    )


# ============================================================
# RESUMO
# ============================================================

total = len(
    rows
)


atrasadas = sum(
    1
    for row in rows
    if row[-1] > 0
)


taxa_atraso = (
    atrasadas
    / total
    * 100
)


print(
    "\n============================================"
)

print(
    " LogiSense AI - Dataset Sintético V2"
)

print(
    "============================================"
)


print(
    f"\nArquivos gerados em:\n{OUT}"
)


print(
    f"\nEntregas geradas: "
    f"{total:,}"
)


print(
    f"Entregas atrasadas: "
    f"{atrasadas:,}"
)


print(
    f"Taxa de atraso: "
    f"{taxa_atraso:.2f}%"
)


print(
    "\nDataset sintético gerado com "
    "fatores operacionais simulados."
)


print(
    "============================================\n"
)