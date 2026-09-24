# Roadmap — LogiSense AI

## Concluído

### Fundação e dados
- [x] Gerador de dados sintéticos
- [x] Base logística com 12.000 entregas
- [x] Estrutura relacional inicial em SQL
- [x] Dados de transportadoras, CDs e rotas

### Backend
- [x] API FastAPI
- [x] KPIs operacionais
- [x] Métricas por transportadora
- [x] Métricas por rota
- [x] Série temporal mensal
- [x] Catálogos dinâmicos para o frontend
- [x] Status e métricas do modelo
- [x] Endpoint de inferência `POST /predict-delay`

### Machine Learning
- [x] Feature engineering
- [x] Split temporal treino/validação/teste
- [x] Comparação entre Logistic Regression, Random Forest e Extra Trees
- [x] Seleção por PR-AUC
- [x] Otimização de threshold por F1-score
- [x] Modelo final salvo com Joblib
- [x] Métricas persistidas em JSON
- [x] Integração do modelo com a API e o frontend

### Frontend
- [x] Dashboard responsivo
- [x] KPIs
- [x] Gráficos com Chart.js
- [x] Tabela de rotas críticas
- [x] Insights automáticos
- [x] Simulador de risco de atraso
- [x] Catálogos dinâmicos
- [x] Sidebar funcional
- [x] Scroll suave e scrollspy
- [x] Identidade visual própria
- [x] Acessibilidade básica
- [x] Vídeo de demonstração publicado no YouTube e integrado ao README
- [x] Thumbnail da demo
- [x] README final de portfólio
- [x] API Reference
- [x] Model Card
- [x] Data Dictionary
- [x] Changelog

## Próximas evoluções

### Dados e arquitetura
- [ ] PostgreSQL
- [ ] ETL estruturado
- [ ] Modelo estrela analítico
- [ ] Testes de qualidade de dados

### Produto e UX
- [ ] Filtros por período
- [ ] Filtros por transportadora e CD
- [ ] Análise geográfica / mapa de rotas
- [ ] Melhorias adicionais para mobile

### Machine Learning
- [ ] Explicabilidade com SHAP ou abordagem equivalente
- [ ] Calibração probabilística
- [ ] Monitoramento de data drift
- [ ] Monitoramento de model drift
- [ ] Retreinamento automatizado

### Engenharia
- [x] Smoke tests automatizados
- [x] CI com GitHub Actions
- [ ] Ampliar cobertura de testes
- [ ] Docker
- [ ] CD / deploy automatizado
- [ ] Deploy em cloud
- [ ] Autenticação
