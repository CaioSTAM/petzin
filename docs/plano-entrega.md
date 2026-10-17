# Entrega PetzIn — implementação por blocos

Referência: [requisitos e decisões](requisitos-e-decisoes.md). Execução pelo assistente autorizada em 17/10/2026, com explicação a cada bloco e espaço para o candidato corrigir decisões. Perguntas de estudo ficam para depois da entrega funcional.

## Restrições

- React; Python/FastAPI; SQL parametrizado/Psycopg; PostgreSQL; Docker.
- Preservar dados existentes. Testes isolados, sem usar os cadastros reais como fixtures.
- Uma reserva usa um canil; dois canis correspondem a duas reservas.
- Datas inclusivas, sem horário, tarifa de demonstração R$ 50 por canil/dia.
- Não acrescentar autenticação, pagamentos, dashboard ou camadas genéricas.

## Bloco 1 — API e consultas de donos

Arquivos: backend/app/main.py (aplicação e erros de conexão), database.py (conexão), donos.py (consultas HTTP e SQL simples), backend/tests/test_donos.py, requirements e README.

- [x] Preparar ambiente virtual e dependências.
- [x] Testes com PostgreSQL isolado: listagem, dono existente, inexistente, ID inválido e indisponibilidade do banco.
- [x] Observar falhas antes das rotas.
- [x] Implementar GET /health, GET /api/donos e GET /api/donos/{id}.
- [x] Executar suíte completa e conferir aplicação local por HTTP.
- [x] Explicação do bloco preparada para entrega nesta conversa; próximo bloco é CRUD de cadastros.

Verificação: 33 testes passaram (25 de banco e 8 de API). Corrigido um caso identificado na revisão: conexão deve ser aberta dentro do endpoint, após a validação do ID, para que um ID inválido retorne 422 mesmo com o banco indisponível. Dependências diretas fixadas nas versões instaladas; TestClient usa httpx2 para compatibilidade com Starlette atual.

## Blocos seguintes

1. Completar CRUD de donos/pets, espécies e consulta de canis, com schemas e validações.
2. Reservas: CRUD, disponibilidade, compartilhamento, transação, proteção concorrente do pet e cobrança.
3. Frontend React simples, componentes e estados de carregamento/erro, integrado à API.
4. Docker, execução limpa, README final, revisão, Git e preparação do repositório público.

Cada bloco deverá ter verificações proporcionais, explicação curta e registro de decisões. Não afirmar que o projeto inteiro está pronto enquanto houver blocos pendentes. Publicação no repositório depende de identificar a conta e o destino corretos.
