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

## Bloco 2 — CRUD de cadastros

Arquivos: app/donos.py, pets.py, especies.py e canis.py; schemas.py para validação de entrada e formato de resposta; fixtures compartilhadas e testes de integração.

- [x] Escrever testes para criação, atualização completa via PUT, exclusão e referências inexistentes.
- [x] Observar falhas antes dos endpoints de escrita.
- [x] Implementar CRUD de donos e pets, GET/POST de espécies e GET de canis.
- [x] Normalizar telefone internacional, nomes e raça opcional; rejeitar campos desconhecidos.
- [x] Responder 404 para recurso ausente, 409 para conflito de integridade e 422 para dados inválidos.
- [x] Bloquear troca de dono/espécie de pet com histórico, preservando a interpretação de família das reservas.
- [x] Executar suíte completa, revisão e verificação HTTP; atualizar documentação e criar commit na branch de cadastros.

Escolhas: PUT recebe a representação completa editável; telefone internacional com + e 8 a 15 algarismos após remover separadores comuns; códigos de espécies derivados do nome sem acentos e tratados como imutáveis. Essas são decisões técnicas documentadas, não novos pedidos da cliente.

Verificação: 59 testes aprovados, com PostgreSQL em schemas isolados. Revisão identificou um caractere de texto que causava erro interno; entrada passou a ser recusada com 422, coberta por quatro testes de regressão. Aplicação reiniciada e rotas conferidas por HTTP.

## Bloco 3 — Reservas

Escopo autorizado: CRUD de reservas e disponibilidade, sem iniciar React ou Docker. Usar os seis modelos existentes; não alterar o schema do banco.

1. Escrever testes do ciclo completo, datas inclusivas, compartilhamento inválido, referências, rollback e concorrência canil/pet; observar as falhas antes de implementar.
2. Acrescentar Periodo, ReservaInput e ReservaResponse em schemas.py. Datas em ordem, um ou dois pets distintos; dinheiro em Decimal.
3. Implementar reservas.py: consultas, transação de criação/edição, bloqueio ordenado dos pets, revalidação de conflitos, cancelamento com histórico e tarifa preservada.
4. Acrescentar GET /api/canis/disponiveis com datas e registrar o router de reservas. Retornar 409 para conflito de ocupação do banco.
5. Conferir suíte completa e HTTP local, revisar, corrigir, documentar e integrar à main sem PR.

Revisão prioritária: mesmo pet em canis diferentes, conflito na edição sem alteração parcial, preservação da tarifa após aumento e cancelamento liberando vaga sem apagar histórico.

Verificação: 47 testes aprovados, incluindo 12 novos casos de reservas. Revisão do código sem impedimentos. HTTP local conferido para listagem, documentação, disponibilidade e período invertido (422). Cadastros reais preservados e schemas de teste removidos.

## Bloco 4 — Interface React simples

Escopo: consumir a API existente com formulários e listagens, sem design elaborado e sem iniciar Docker.

- Componentes por recurso, fetch centralizado, campos e tabelas compartilhados.
- Cadastro/edição/exclusão de donos e pets; cadastro de espécies; criação/edição/cancelamento de reservas e disponibilidade.
- Campos nativos, seleção de dono/espécie/canil, mensagens de erro e confirmação inline.
- Conferência em navegador com schema isolado, largura de celular, teclado e recuperação de erro; build e suíte do backend antes de integrar à main.

## Bloco 5 — Docker e entrega

Escopo autorizado: compor banco, API e interface, inicializar banco vazio, documentar instalação e conferir requisitos do PDF completo.

1. Compose com PostgreSQL 18, API Python e build React servido por Nginx; banco em volume separado do PostgreSQL local.
2. Aplicar 001_estrutura.sql somente na inicialização do volume; aguardar saúde do banco e da API antes dos serviços dependentes.
3. Usar .env fora do Git, exemplo público sem credencial real, API em 8002 e interface em 8080 para evitar as portas do desenvolvimento.
4. Validar configuração, build e subida limpa; conferir interface/API e persistência após reiniciar. Se o Docker não iniciar na máquina, registrar o impedimento exato sem alegar validação de containers.
5. Completar README, análise do modelo original, mapa de requisitos e limites; executar verificações disponíveis e revisão antes do merge.

Resultado: configuração, build de imagens, inicialização de volume vazio, fluxo por Nginx/API e persistência após down/up verificados. Os 47 testes de banco/API, teste do cliente HTTP e build React passaram. Docker Desktop foi recuperado sem apagar discos após falhar na inicialização. A conferência detalhada está em verificacao-entrega.md.

## Blocos seguintes

1. Estudar o fluxo completo e as decisões para apresentação do candidato.

Cada bloco deverá ter verificações proporcionais, explicação curta e registro de decisões. Não afirmar que o projeto inteiro está pronto enquanto houver blocos pendentes. Publicação no repositório depende de identificar a conta e o destino corretos.
