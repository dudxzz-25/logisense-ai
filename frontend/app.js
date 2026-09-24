const API_URL = "http://127.0.0.1:8000";


// ======================================================
// CORES DO DASHBOARD
// ======================================================

const COLORS = {
    primary: "#0f8aa6",
    primaryLight: "#12b8d4",
    primaryDark: "#0b6f85",

    textPrimary: "#17303a",
    textSecondary: "#58707a",
    textMuted: "#7f969f",

    grid: "rgba(24, 66, 80, 0.10)",

    tooltipBackground: "#f5fafb",
    tooltipBorder: "rgba(24, 66, 80, 0.16)",

    success: "#16a34a",
    warning: "#ca8a04",
    danger: "#dc2626"
};


// ======================================================
// CONFIGURAÇÃO GLOBAL DO CHART.JS
// ======================================================

Chart.defaults.color =
    COLORS.textSecondary;

Chart.defaults.font.family =
    'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';


// ======================================================
// FORMATADORES
// ======================================================

const formatNumber = (value) => {

    return new Intl.NumberFormat(
        "pt-BR"
    ).format(value);
};


const formatCurrency = (value) => {

    return new Intl.NumberFormat(
        "pt-BR",
        {
            style: "currency",
            currency: "BRL"
        }
    ).format(value);
};


const formatCompactCurrency = (value) => {

    return new Intl.NumberFormat(
        "pt-BR",
        {
            style: "currency",
            currency: "BRL",
            notation: "compact",
            maximumFractionDigits: 2
        }
    ).format(value);
};


const formatPercentage = (
    value,
    digits = 2
) => {

    return (
        Number(value)
            .toFixed(digits)
            .replace(".", ",")
        + "%"
    );
};


const formatMonth = (month) => {

    const [
        year,
        monthNumber
    ] = month.split("-");


    const date =
        new Date(
            Number(year),
            Number(monthNumber) - 1,
            1
        );


    return new Intl.DateTimeFormat(
        "pt-BR",
        {
            month: "short",
            year: "2-digit"
        }
    )
        .format(date)
        .replace(".", "");
};


// ======================================================
// NORMALIZAÇÃO DE TEXTO
// ======================================================

function normalizeText(text) {

    return text
        .normalize("NFD")
        .replace(
            /[\u0300-\u036f]/g,
            ""
        )
        .trim()
        .toLowerCase();
}


// ======================================================
// DATA LOCAL
// ======================================================

function getLocalDateString() {

    const today =
        new Date();


    const year =
        today.getFullYear();


    const month =
        String(
            today.getMonth() + 1
        ).padStart(
            2,
            "0"
        );


    const day =
        String(
            today.getDate()
        ).padStart(
            2,
            "0"
        );


    return `${year}-${month}-${day}`;
}


// ======================================================
// GET
// ======================================================

async function fetchData(endpoint) {

    const response =
        await fetch(
            `${API_URL}${endpoint}`
        );


    if (!response.ok) {

        throw new Error(
            `Erro ${response.status} ao acessar ${endpoint}`
        );
    }


    return response.json();
}


// ======================================================
// POST
// ======================================================

async function postData(
    endpoint,
    payload
) {

    const response =
        await fetch(
            `${API_URL}${endpoint}`,
            {
                method:
                    "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        payload
                    )
            }
        );


    const data =
        await response.json();


    if (!response.ok) {

        let message =
            `Erro ${response.status}`;


        if (data.detail) {

            if (
                typeof data.detail
                === "string"
            ) {

                message =
                    data.detail;

            } else {

                message =
                    JSON.stringify(
                        data.detail
                    );
            }
        }


        throw new Error(
            message
        );
    }


    return data;
}


// ======================================================
// STATUS DA API
// ======================================================

function updateApiStatus(online) {

    const statusText =
        document.getElementById(
            "apiStatus"
        );


    const statusDot =
        document.querySelector(
            ".status-dot"
        );


    if (
        !statusText
        || !statusDot
    ) {

        return;
    }


    if (online) {

        statusText.textContent =
            "Online";


        statusDot.style.background =
            COLORS.success;


        statusDot.style.boxShadow =
            "0 0 9px rgba(22, 163, 74, 0.48)";

    } else {

        statusText.textContent =
            "Offline";


        statusDot.style.background =
            COLORS.danger;


        statusDot.style.boxShadow =
            "0 0 9px rgba(220, 38, 38, 0.45)";
    }
}


// ======================================================
// SELECT GENÉRICO
// ======================================================

function populateSelect(
    selectId,
    items,
    valueFunction,
    labelFunction
) {

    const select =
        document.getElementById(
            selectId
        );


    if (!select) {

        console.warn(
            `Select não encontrado: ${selectId}`
        );

        return;
    }


    const previousValue =
        select.value;


    select.innerHTML =
        "";


    const defaultOption =
        document.createElement(
            "option"
        );


    defaultOption.value =
        "";


    defaultOption.textContent =
        "Selecione";


    select.appendChild(
        defaultOption
    );


    items.forEach(
        item => {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                valueFunction(
                    item
                );


            option.textContent =
                labelFunction(
                    item
                );


            select.appendChild(
                option
            );
        }
    );


    const stillExists =
        Array.from(
            select.options
        ).some(
            option =>
                option.value
                === previousValue
        );


    if (stillExists) {

        select.value =
            previousValue;
    }
}


// ======================================================
// CATÁLOGOS DINÂMICOS
// ======================================================

function renderCatalogos(catalogos) {

    populateSelect(
        "predictTransportadora",

        catalogos.transportadoras,

        item =>
            item.id,

        item =>
            `${item.nome} • ${item.estado_sede}`
    );


    populateSelect(
        "predictCd",

        catalogos
            .centros_distribuicao,

        item =>
            item.id,

        item =>
            `${item.nome} • ${item.cidade}/${item.estado}`
    );


    populateSelect(
        "predictRota",

        catalogos.rotas,

        item =>
            item.id,

        item =>
            `${item.origem} → ${item.destino} • ${formatNumber(
                item.distancia_km
            )} km`
    );
}


// ======================================================
// KPIs
// ======================================================

function renderKpis(kpis) {

    document.getElementById(
        "totalEntregas"
    ).textContent =
        formatNumber(
            kpis.entregas
        );


    document.getElementById(
        "sla"
    ).textContent =
        formatPercentage(
            kpis.sla_pct
        );


    document.getElementById(
        "taxaAtraso"
    ).textContent =
        formatPercentage(
            kpis.taxa_atraso_pct
        );


    document.getElementById(
        "custoTotal"
    ).textContent =
        formatCompactCurrency(
            kpis.custo_frete_total
        );
}


// ======================================================
// TOOLTIP PADRÃO
// ======================================================

function getTooltipOptions() {

    return {

        backgroundColor:
            COLORS.tooltipBackground,

        titleColor:
            COLORS.textPrimary,

        bodyColor:
            COLORS.textSecondary,

        borderColor:
            COLORS.tooltipBorder,

        borderWidth:
            1,

        padding:
            12,

        cornerRadius:
            10,

        displayColors:
            false
    };
}


// ======================================================
// GRÁFICO DE ATRASOS
// ======================================================

function renderAtrasoChart(
    serieMensal
) {

    const canvas =
        document.getElementById(
            "atrasoChart"
        );


    if (!canvas) {

        return;
    }


    const labels =
        serieMensal.map(
            item =>
                formatMonth(
                    item.mes
                )
        );


    const values =
        serieMensal.map(
            item =>
                item.taxa_atraso_pct
        );


    new Chart(
        canvas,
        {
            type:
                "line",

            data: {

                labels,

                datasets: [
                    {
                        label:
                            "Taxa de atraso",

                        data:
                            values,

                        borderColor:
                            COLORS.primary,

                        backgroundColor:
                            "rgba(18, 184, 212, 0.16)",

                        borderWidth:
                            2.5,

                        tension:
                            0.35,

                        fill:
                            true,

                        pointRadius:
                            3,

                        pointHoverRadius:
                            6,

                        pointBackgroundColor:
                            COLORS.primaryLight,

                        pointBorderColor:
                            "#f5fafb",

                        pointBorderWidth:
                            2
                    }
                ]
            },


            options: {

                responsive:
                    true,

                maintainAspectRatio:
                    false,


                interaction: {

                    intersect:
                        false,

                    mode:
                        "index"
                },


                plugins: {

                    legend: {
                        display:
                            false
                    },


                    tooltip: {

                        ...getTooltipOptions(),

                        callbacks: {

                            label:
                                context =>
                                    `Taxa de atraso: ${formatPercentage(
                                        context.raw
                                    )}`
                        }
                    }
                },


                scales: {

                    x: {

                        border: {
                            display:
                                false
                        },

                        grid: {
                            display:
                                false
                        },

                        ticks: {

                            color:
                                COLORS.textMuted,

                            maxRotation:
                                0,

                            autoSkip:
                                true,

                            maxTicksLimit:
                                10,

                            font: {
                                size:
                                    10
                            }
                        }
                    },


                    y: {

                        beginAtZero:
                            false,

                        border: {
                            display:
                                false
                        },

                        grid: {

                            color:
                                COLORS.grid,

                            drawTicks:
                                false
                        },

                        ticks: {

                            color:
                                COLORS.textMuted,

                            padding:
                                8,

                            font: {
                                size:
                                    10
                            },

                            callback:
                                value =>
                                    `${value}%`
                        }
                    }
                }
            }
        }
    );
}


// ======================================================
// GRÁFICO DE TRANSPORTADORAS
// ======================================================

function renderTransportadorasChart(
    transportadoras
) {

    const canvas =
        document.getElementById(
            "transportadorasChart"
        );


    if (!canvas) {

        return;
    }


    const ordenadas =
        [...transportadoras]
            .sort(
                (a, b) =>
                    b.sla_pct
                    - a.sla_pct
            );


    const labels =
        ordenadas.map(
            item =>
                item.nome_transportadora
        );


    const values =
        ordenadas.map(
            item =>
                item.sla_pct
        );


    new Chart(
        canvas,
        {
            type:
                "bar",

            data: {

                labels,

                datasets: [
                    {
                        label:
                            "SLA",

                        data:
                            values,

                        backgroundColor:
                            "rgba(15, 138, 166, 0.78)",

                        hoverBackgroundColor:
                            "rgba(18, 184, 212, 0.90)",

                        borderColor:
                            COLORS.primaryDark,

                        borderWidth:
                            1,

                        borderRadius:
                            7,

                        borderSkipped:
                            false,

                        barThickness:
                            20
                    }
                ]
            },


            options: {

                indexAxis:
                    "y",

                responsive:
                    true,

                maintainAspectRatio:
                    false,


                plugins: {

                    legend: {
                        display:
                            false
                    },


                    tooltip: {

                        ...getTooltipOptions(),

                        callbacks: {

                            label:
                                context =>
                                    `SLA: ${formatPercentage(
                                        context.raw
                                    )}`
                        }
                    }
                },


                scales: {

                    x: {

                        min:
                            0,

                        max:
                            100,

                        border: {
                            display:
                                false
                        },

                        grid: {
                            color:
                                COLORS.grid
                        },

                        ticks: {

                            color:
                                COLORS.textMuted,

                            font: {
                                size:
                                    10
                            },

                            callback:
                                value =>
                                    `${value}%`
                        }
                    },


                    y: {

                        border: {
                            display:
                                false
                        },

                        grid: {
                            display:
                                false
                        },

                        ticks: {

                            color:
                                COLORS.textSecondary,

                            font: {

                                size:
                                    11,

                                weight:
                                    "500"
                            }
                        }
                    }
                }
            }
        }
    );
}


// ======================================================
// ROTAS
// ======================================================

function renderRotas(rotas) {

    const tbody =
        document.getElementById(
            "rotasTable"
        );


    if (!tbody) {

        return;
    }


    const rotasCriticas =
        [...rotas]
            .sort(
                (a, b) =>
                    b.atraso_medio
                    - a.atraso_medio
            )
            .slice(
                0,
                5
            );


    tbody.innerHTML =
        "";


    rotasCriticas.forEach(
        rota => {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>
                    ${rota.origem}
                </td>

                <td>
                    ${rota.destino}
                </td>

                <td>
                    ${formatNumber(
                        rota.entregas
                    )}
                </td>

                <td>
                    ${rota.atraso_medio
                        .toFixed(2)
                        .replace(".", ",")}
                    dias
                </td>

                <td>
                    ${formatCurrency(
                        rota.custo_medio
                    )}
                </td>

            `;


            tbody.appendChild(
                row
            );
        }
    );
}


// ======================================================
// INSIGHTS
// ======================================================

function renderInsights(
    transportadoras,
    rotas,
    serieMensal
) {

    const container =
        document.getElementById(
            "insightsContainer"
        );


    if (!container) {

        return;
    }


    const transportadorasOrdenadas =
        [...transportadoras]
            .sort(
                (a, b) =>
                    a.sla_pct
                    - b.sla_pct
            );


    const piorTransportadora =
        transportadorasOrdenadas[0];


    const melhorTransportadora =
        transportadorasOrdenadas[
            transportadorasOrdenadas.length - 1
        ];


    const rotaCritica =
        [...rotas]
            .sort(
                (a, b) =>
                    b.atraso_medio
                    - a.atraso_medio
            )[0];


    const piorMes =
        [...serieMensal]
            .sort(
                (a, b) =>
                    b.taxa_atraso_pct
                    - a.taxa_atraso_pct
            )[0];


    const ultimoMes =
        serieMensal[
            serieMensal.length - 1
        ];


    const hoje =
        new Date();


    const mesAtual =
        `${hoje.getFullYear()}-${String(
            hoje.getMonth() + 1
        ).padStart(
            2,
            "0"
        )}`;


    const mesEmAndamento =
        ultimoMes.mes
        === mesAtual;


    const insights = [

        {
            titulo:
                "Transportadora com maior atenção",

            texto:
                `${piorTransportadora.nome_transportadora} apresenta o menor SLA da operação, com ${formatPercentage(
                    piorTransportadora.sla_pct
                )}.`
        },


        {
            titulo:
                "Melhor desempenho de SLA",

            texto:
                `${melhorTransportadora.nome_transportadora} lidera entre as transportadoras, com SLA de ${formatPercentage(
                    melhorTransportadora.sla_pct
                )}.`
        },


        {
            titulo:
                "Rota mais crítica",

            texto:
                `${rotaCritica.origem} → ${rotaCritica.destino} registra atraso médio de ${rotaCritica.atraso_medio
                    .toFixed(2)
                    .replace(".", ",")} dias e frete médio de ${formatCurrency(
                    rotaCritica.custo_medio
                )}.`
        },


        {
            titulo:
                "Pico de atrasos",

            texto:
                `${formatMonth(
                    piorMes.mes
                )} registrou a maior taxa de atraso da série: ${formatPercentage(
                    piorMes.taxa_atraso_pct
                )}.`
        }

    ];


    if (mesEmAndamento) {

        insights.push(
            {
                titulo:
                    "Período em andamento",

                texto:
                    `${formatMonth(
                        ultimoMes.mes
                    )} ainda é um mês parcial. O volume de ${formatNumber(
                        ultimoMes.entregas
                    )} entregas não deve ser comparado diretamente com meses já encerrados.`
            }
        );
    }


    container.innerHTML =
        insights
            .map(
                insight => `

                    <div class="insight-item">

                        <span class="insight-icon">
                            ✦
                        </span>

                        <div>

                            <strong>
                                ${insight.titulo}
                            </strong>

                            <p>
                                ${insight.texto}
                            </p>

                        </div>

                    </div>

                `
            )
            .join("");
}


// ======================================================
// MÉTRICAS DO MODELO
// ======================================================

function renderModelMetrics(metrics) {

    if (
        !metrics
        || metrics.status
        === "erro"
    ) {

        return;
    }


    const testMetrics =
        metrics.test_metrics;


    if (!testMetrics) {

        return;
    }


    const modelName =
        document.getElementById(
            "modelName"
        );


    const modelRocAuc =
        document.getElementById(
            "modelRocAuc"
        );


    const modelRecall =
        document.getElementById(
            "modelRecall"
        );


    const modelF1 =
        document.getElementById(
            "modelF1"
        );


    if (modelName) {

        modelName.textContent =
            metrics.modelo;
    }


    if (modelRocAuc) {

        modelRocAuc.textContent =
            Number(
                testMetrics.roc_auc
            ).toFixed(4);
    }


    if (modelRecall) {

        modelRecall.textContent =
            formatPercentage(
                testMetrics.recall
                * 100
            );
    }


    if (modelF1) {

        modelF1.textContent =
            Number(
                testMetrics.f1
            ).toFixed(4);
    }
}


// ======================================================
// CLASSE VISUAL DO RISCO
// ======================================================

function getRiskClass(riskLevel) {

    const normalized =
        riskLevel
            .toLowerCase()
            .trim();


    if (
        normalized
        === "muito alto"
    ) {

        return "risk-very-high";
    }


    if (
        normalized
        === "alto"
    ) {

        return "risk-high";
    }


    if (
        normalized
        === "moderado"
    ) {

        return "risk-moderate";
    }


    return "risk-low";
}


// ======================================================
// RESULTADO DA PREDIÇÃO
// ======================================================

function renderPrediction(prediction) {

    const placeholder =
        document.querySelector(
            ".prediction-placeholder"
        );


    const content =
        document.getElementById(
            "predictionContent"
        );


    if (placeholder) {

        placeholder
            .classList
            .add(
                "hidden"
            );
    }


    if (content) {

        content
            .classList
            .remove(
                "hidden"
            );
    }


    document.getElementById(
        "predictionScore"
    ).textContent =
        formatPercentage(
            prediction
                .score_risco_pct
        );


    const level =
        document.getElementById(
            "predictionLevel"
        );


    level.textContent =
        prediction.nivel_risco;


    level.classList.remove(
        "risk-low",
        "risk-moderate",
        "risk-high",
        "risk-very-high"
    );


    level.classList.add(
        getRiskClass(
            prediction.nivel_risco
        )
    );


    document.getElementById(
        "predictionModel"
    ).textContent =
        prediction.modelo;


    document.getElementById(
        "predictionThreshold"
    ).textContent =
        formatPercentage(
            prediction
                .threshold_pct
        );


    document.getElementById(
        "predictionDistance"
    ).textContent =
        `${formatNumber(
            prediction
                .distancia_km
        )} km`;


    document.getElementById(
        "predictionStatus"
    ).textContent =
        prediction
            .predicao_atraso
        ? "Risco de atraso"
        : "Dentro do limite";


    document.getElementById(
        "predictionRoute"
    ).textContent =
        `${prediction.transportadora} • ${prediction.rota} • ${prediction.centro_distribuicao}`;
}


// ======================================================
// ERRO DA PREDIÇÃO
// ======================================================

function renderPredictionError(message) {

    const placeholder =
        document.querySelector(
            ".prediction-placeholder"
        );


    const content =
        document.getElementById(
            "predictionContent"
        );


    if (content) {

        content
            .classList
            .add(
                "hidden"
            );
    }


    if (placeholder) {

        placeholder
            .classList
            .remove(
                "hidden"
            );


        placeholder.innerHTML = `

            <span
                class="prediction-placeholder-icon"
            >
                !
            </span>

            <h4>
                Não foi possível analisar
            </h4>

            <p>
                ${message}
            </p>

        `;
    }
}


// ======================================================
// FORMULÁRIO DE PREDIÇÃO
// ======================================================

function setupPredictionForm() {

    const form =
        document.getElementById(
            "predictionForm"
        );


    if (!form) {

        return;
    }


    const dateInput =
        document.getElementById(
            "predictDate"
        );


    if (
        dateInput
        && !dateInput.value
    ) {

        dateInput.value =
            getLocalDateString();
    }


    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const button =
                document.getElementById(
                    "predictButton"
                );


            const payload = {

                data_pedido:
                    document
                        .getElementById(
                            "predictDate"
                        ).value,

                transportadora_id:
                    Number(
                        document
                            .getElementById(
                                "predictTransportadora"
                            ).value
                    ),

                cd_id:
                    Number(
                        document
                            .getElementById(
                                "predictCd"
                            ).value
                    ),

                rota_id:
                    Number(
                        document
                            .getElementById(
                                "predictRota"
                            ).value
                    ),

                valor_frete:
                    Number(
                        document
                            .getElementById(
                                "predictFrete"
                            ).value
                    ),

                peso_kg:
                    Number(
                        document
                            .getElementById(
                                "predictPeso"
                            ).value
                    ),

                sla_dias:
                    Number(
                        document
                            .getElementById(
                                "predictSla"
                            ).value
                    )
            };


            try {

                button.disabled =
                    true;


                button
                    .classList
                    .add(
                        "loading-button"
                    );


                button
                    .querySelector(
                        "span"
                    )
                    .textContent =
                        "Analisando";


                const prediction =
                    await postData(
                        "/predict-delay",
                        payload
                    );


                renderPrediction(
                    prediction
                );


            } catch (error) {

                console.error(
                    "Erro na previsão:",
                    error
                );


                renderPredictionError(
                    error.message
                );


            } finally {

                button.disabled =
                    false;


                button
                    .classList
                    .remove(
                        "loading-button"
                    );


                button
                    .querySelector(
                        "span"
                    )
                    .textContent =
                        "Analisar risco";
            }
        }
    );
}


// ======================================================
// ITEM ATIVO DA SIDEBAR
// ======================================================

function setActiveMenuItem(
    activeItem
) {

    const menuItems =
        document.querySelectorAll(
            ".menu-item"
        );


    menuItems.forEach(
        item => {

            item.classList.remove(
                "active"
            );


            item.removeAttribute(
                "aria-current"
            );
        }
    );


    if (activeItem) {

        activeItem
            .classList
            .add(
                "active"
            );


        activeItem
            .setAttribute(
                "aria-current",
                "page"
            );
    }
}


// ======================================================
// EFEITO DE DESTAQUE DA SEÇÃO
// ======================================================

function highlightSection(section) {

    if (!section) {

        return;
    }


    section.classList.remove(
        "navigation-highlight"
    );


    void section.offsetWidth;


    section.classList.add(
        "navigation-highlight"
    );


    window.setTimeout(
        () => {

            section.classList.remove(
                "navigation-highlight"
            );

        },
        950
    );
}


// ======================================================
// LOCALIZA AS SEÇÕES
// ======================================================

function getNavigationSections() {

    const dashboardSection =
        document.querySelector(
            ".topbar"
        );


    const transportadorasSection =
        document
            .getElementById(
                "transportadorasChart"
            )
            ?.closest(
                ".panel"
            );


    const rotasSection =
        document
            .getElementById(
                "rotasTable"
            )
            ?.closest(
                ".panel"
            );


    const predictionSection =
        document.querySelector(
            ".prediction-section"
        )
        ||
        document
            .getElementById(
                "predictionForm"
            )
            ?.closest(
                ".panel"
            );


    const insightsSection =
        document
            .getElementById(
                "insightsContainer"
            )
            ?.closest(
                ".panel"
            );


    if (dashboardSection) {

        dashboardSection.id =
            "dashboard";
    }


    if (transportadorasSection) {

        transportadorasSection.id =
            "transportadoras";
    }


    if (rotasSection) {

        rotasSection.id =
            "rotas";
    }


    if (predictionSection) {

        predictionSection.id =
            "predicao-ml";
    }


    if (insightsSection) {

        insightsSection.id =
            "ai-insights";
    }


    return {

        dashboard:
            dashboardSection,

        transportadoras:
            transportadorasSection,

        rotas:
            rotasSection,

        "predicao-ml":
            predictionSection,

        "ai-insights":
            insightsSection
    };
}


// ======================================================
// DESCOBRE DESTINO PELO TEXTO
// ======================================================

function getMenuTarget(menuItem) {

    const text =
        normalizeText(
            menuItem.textContent
        );


    if (
        text.includes(
            "dashboard"
        )
    ) {

        return "dashboard";
    }


    if (
        text.includes(
            "transportadora"
        )
    ) {

        return "transportadoras";
    }


    if (
        text === "rotas"
        || text.includes(
            "rota"
        )
    ) {

        return "rotas";
    }


    if (
        text.includes(
            "predicao"
        )
    ) {

        return "predicao-ml";
    }


    if (
        text.includes(
            "insight"
        )
    ) {

        return "ai-insights";
    }


    return null;
}


// ======================================================
// SCROLL SUAVE
// ======================================================

function scrollToSection(
    section,
    behavior = "smooth",
    showHighlight = false
) {

    if (!section) {

        return;
    }


    const offset =
        24;


    const sectionTop =
        section
            .getBoundingClientRect()
            .top
        + window.scrollY
        - offset;


    window.scrollTo(
        {
            top:
                Math.max(
                    sectionTop,
                    0
                ),

            behavior
        }
    );


    if (showHighlight) {

        const delay =
            behavior === "smooth"
            ? 420
            : 50;


        window.setTimeout(
            () => {

                highlightSection(
                    section
                );

            },
            delay
        );
    }
}


// ======================================================
// SCROLLSPY
// ======================================================

function updateActiveMenuByScroll(
    sections,
    menuMap
) {

    const referenceLine =
        Math.min(
            190,
            window.innerHeight
            * 0.28
        );


    const visibleSections =
        Object
            .entries(
                sections
            )
            .filter(
                ([, section]) =>
                    section
            )
            .map(
                ([id, section]) => {

                    const rect =
                        section
                            .getBoundingClientRect();


                    return {
                        id,
                        section,
                        rect
                    };
                }
            );


    if (
        visibleSections.length
        === 0
    ) {

        return;
    }


    const currentActiveItem =
        document.querySelector(
            ".menu-item.active"
        );


    const currentTarget =
        currentActiveItem
        ? getMenuTarget(
            currentActiveItem
        )
        : null;


    const crossingSections =
        visibleSections.filter(
            item =>
                item.rect.top
                    <= referenceLine
                &&
                item.rect.bottom
                    >= referenceLine
        );


    let selectedSection =
        null;


    if (
        crossingSections.length
        > 0
    ) {

        const currentStillVisible =
            crossingSections.find(
                item =>
                    item.id
                    === currentTarget
            );


        if (currentStillVisible) {

            selectedSection =
                currentStillVisible;

        } else {

            selectedSection =
                crossingSections
                    .sort(
                        (a, b) =>
                            Math.abs(
                                a.rect.top
                                - referenceLine
                            )
                            -
                            Math.abs(
                                b.rect.top
                                - referenceLine
                            )
                    )[0];
        }

    } else {

        selectedSection =
            visibleSections
                .sort(
                    (a, b) =>
                        Math.abs(
                            a.rect.top
                            - referenceLine
                        )
                        -
                        Math.abs(
                            b.rect.top
                            - referenceLine
                        )
                )[0];
    }


    if (
        !selectedSection
        || !menuMap[
            selectedSection.id
        ]
    ) {

        return;
    }


    const selectedMenuItem =
        menuMap[
            selectedSection.id
        ];


    if (
        !selectedMenuItem
            .classList
            .contains(
                "active"
            )
    ) {

        setActiveMenuItem(
            selectedMenuItem
        );


        history.replaceState(
            null,
            "",
            `#${selectedSection.id}`
        );
    }
}


// ======================================================
// CONFIGURAÇÃO DA SIDEBAR
// ======================================================

function setupNavigation() {

    const menuItems =
        document.querySelectorAll(
            ".menu-item"
        );


    if (
        menuItems.length
        === 0
    ) {

        return;
    }


    const sections =
        getNavigationSections();


    const menuMap =
        {};


    menuItems.forEach(
        item => {

            const targetId =
                getMenuTarget(
                    item
                );


            if (
                !targetId
                || !sections[
                    targetId
                ]
            ) {

                return;
            }


            menuMap[
                targetId
            ] = item;


            item.setAttribute(
                "href",
                `#${targetId}`
            );


            item.addEventListener(
                "click",
                event => {

                    event.preventDefault();


                    const section =
                        sections[
                            targetId
                        ];


                    setActiveMenuItem(
                        item
                    );


                    history.pushState(
                        null,
                        "",
                        `#${targetId}`
                    );


                    scrollToSection(
                        section,
                        "smooth",
                        true
                    );
                }
            );
        }
    );


    // --------------------------------------------------
    // SCROLLSPY
    // --------------------------------------------------

    let scrollScheduled =
        false;


    window.addEventListener(
        "scroll",
        () => {

            if (
                scrollScheduled
            ) {

                return;
            }


            scrollScheduled =
                true;


            window.requestAnimationFrame(
                () => {

                    updateActiveMenuByScroll(
                        sections,
                        menuMap
                    );


                    scrollScheduled =
                        false;
                }
            );
        },
        {
            passive:
                true
        }
    );


    // --------------------------------------------------
    // ABERTURA DIRETA POR HASH
    // --------------------------------------------------

    const hash =
        window.location.hash
            .replace(
                "#",
                ""
            );


    if (
        hash
        && sections[hash]
    ) {

        if (
            menuMap[hash]
        ) {

            setActiveMenuItem(
                menuMap[hash]
            );
        }


        window.setTimeout(
            () => {

                scrollToSection(
                    sections[hash],
                    "auto",
                    true
                );

            },
            100
        );

    } else if (
        menuMap.dashboard
    ) {

        setActiveMenuItem(
            menuMap.dashboard
        );
    }
}


// ======================================================
// INICIALIZAÇÃO PRINCIPAL
// ======================================================

async function initializeDashboard() {

    try {

        const [
            kpis,
            transportadoras,
            rotas,
            serieMensal,
            modelMetrics,
            catalogos
        ] = await Promise.all(
            [

                fetchData(
                    "/kpis"
                ),

                fetchData(
                    "/transportadoras"
                ),

                fetchData(
                    "/rotas"
                ),

                fetchData(
                    "/serie-mensal"
                ),

                fetchData(
                    "/model-metrics"
                ),

                fetchData(
                    "/catalogos"
                )

            ]
        );


        renderKpis(
            kpis
        );


        renderAtrasoChart(
            serieMensal
        );


        renderTransportadorasChart(
            transportadoras
        );


        renderRotas(
            rotas
        );


        renderInsights(
            transportadoras,
            rotas,
            serieMensal
        );


        renderModelMetrics(
            modelMetrics
        );


        renderCatalogos(
            catalogos
        );


        updateApiStatus(
            true
        );


    } catch (error) {

        console.error(
            "Erro ao carregar dashboard:",
            error
        );


        updateApiStatus(
            false
        );


        const insightsContainer =
            document.getElementById(
                "insightsContainer"
            );


        if (insightsContainer) {

            insightsContainer.innerHTML = `

                <div class="insight-item">

                    <span class="insight-icon">
                        !
                    </span>

                    <div>

                        <strong>
                            Não foi possível carregar os dados
                        </strong>

                        <p>
                            Verifique se a API FastAPI
                            está executando em
                            http://127.0.0.1:8000.
                        </p>

                    </div>

                </div>

            `;
        }
    }
}


// ======================================================
// START
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupPredictionForm();

        setupNavigation();

        initializeDashboard();

    }
);