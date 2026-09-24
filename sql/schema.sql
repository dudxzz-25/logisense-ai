-- LogiSense AI - schema relacional inicial

CREATE TABLE dim_transportadora (
    transportadora_id INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(40) NOT NULL,
    estado_sede CHAR(2) NOT NULL
);

CREATE TABLE dim_centro_distribuicao (
    cd_id INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL
);

CREATE TABLE dim_rota (
    rota_id INTEGER PRIMARY KEY,
    origem VARCHAR(100) NOT NULL,
    destino VARCHAR(100) NOT NULL,
    distancia_km NUMERIC(10,2) NOT NULL
);

CREATE TABLE fato_entrega (
    entrega_id INTEGER PRIMARY KEY,
    data_pedido DATE NOT NULL,
    data_prevista DATE NOT NULL,
    data_entrega DATE NOT NULL,
    transportadora_id INTEGER NOT NULL,
    cd_id INTEGER NOT NULL,
    rota_id INTEGER NOT NULL,
    valor_frete NUMERIC(12,2) NOT NULL,
    peso_kg NUMERIC(12,2) NOT NULL,
    status VARCHAR(30) NOT NULL,
    ocorrencia VARCHAR(80),
    sla_dias INTEGER NOT NULL,
    atraso_dias INTEGER NOT NULL,
    FOREIGN KEY (transportadora_id) REFERENCES dim_transportadora(transportadora_id),
    FOREIGN KEY (cd_id) REFERENCES dim_centro_distribuicao(cd_id),
    FOREIGN KEY (rota_id) REFERENCES dim_rota(rota_id)
);
