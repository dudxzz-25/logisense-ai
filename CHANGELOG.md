# Changelog

Todas as mudanças relevantes do LogiSense AI serão registradas neste arquivo.

## [0.4.0] — 2026-09-24

### Adicionado
- endpoint `GET /catalogos`;
- endpoint `GET /ml-status`;
- endpoint `GET /model-metrics`;
- endpoint `POST /predict-delay`;
- integração do modelo de Machine Learning com a API;
- formulário de simulação de risco no frontend;
- score de risco e classificação em quatro níveis;
- métricas do modelo no dashboard;
- selects dinâmicos consumindo dados da API;
- navegação funcional pela sidebar;
- scroll suave, scrollspy e hash na URL;
- destaque visual das seções;
- identidade visual em azul acinzentado e ciano;
- documentação de API;
- Model Card;
- Data Dictionary;
- Changelog;
- thumbnail para demonstração;
- vídeo de demonstração em `docs/demo.mp4`;
- link da thumbnail diretamente para a demo.

### Alterado
- redesign completo da interface;
- gráficos atualizados para a nova identidade visual;
- README reestruturado para apresentação de portfólio;
- roadmap atualizado;
- `.gitignore` e `.gitattributes` revisados.

### Machine Learning
- comparação entre Logistic Regression, Random Forest e Extra Trees;
- split temporal 70/15/15;
- seleção por PR-AUC;
- threshold otimizado por F1-score;
- artefato final persistido com Joblib;
- métricas persistidas em `metrics.json`.

---

## [0.3.0]

### Adicionado
- dashboard inicial;
- KPIs logísticos;
- gráfico de evolução de atrasos;
- ranking de transportadoras;
- tabela de rotas críticas;
- insights operacionais;
- estrutura inicial da API FastAPI.

---

## [0.1.0]

### Adicionado
- estrutura inicial do projeto;
- gerador de dados sintéticos;
- primeiros arquivos CSV;
- schema SQL inicial.
