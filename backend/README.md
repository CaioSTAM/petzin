# API PetzIn

Implementei a API com FastAPI e PostgreSQL para gerenciar donos, pets, espécies, canis e reservas, incluindo a consulta de disponibilidade.

## Executar no Windows

Na raiz do projeto, com Python 3.14 e o banco preparado conforme [instruções do banco](../database/README.md):

```powershell
py -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Se o ambiente virtual já existir e as dependências estiverem instaladas, execute somente o último comando.

Documentação interativa: http://127.0.0.1:8000/docs.

Por padrão, a conexão usa localhost, porta 5432, banco petzin e usuário postgres. A senha vem da configuração local de autenticação PostgreSQL, fora do projeto. Outra conexão pode ser indicada pela variável DATABASE_URL, em formato URI PostgreSQL ou parâmetros libpq. Senhas não devem ser incluídas no código nem no repositório.

## Rotas implementadas

| Método e caminho | Comportamento |
|---|---|
| GET /health | Confirma que a API está respondendo; não verifica o banco. |
| GET /ready | Verifica a conexão com o banco com SELECT 1; retorna 503 em caso de indisponibilidade. |
| GET /api/donos | Lista donos por ID. |
| GET /api/donos/{dono_id} | Consulta um dono com ID inteiro positivo. |
| POST /api/donos | Cadastra dono com nome e telefone. |
| PUT /api/donos/{dono_id} | Substitui nome e telefone do dono. |
| DELETE /api/donos/{dono_id} | Exclui dono sem pets vinculados. |
| GET /api/pets | Lista pets; aceita filtro opcional dono_id. |
| GET /api/pets/{pet_id} | Consulta um pet. |
| POST /api/pets | Cadastra pet com nome, dono_id, especie_id e raça opcional. |
| PUT /api/pets/{pet_id} | Substitui os campos editáveis do pet. |
| DELETE /api/pets/{pet_id} | Exclui pet sem reservas vinculadas. |
| GET /api/especies | Lista as espécies cadastradas. |
| POST /api/especies | Cadastra espécie pelo nome, gerando código estável. |
| GET /api/canis | Lista os 15 canis. |
| GET /api/canis/disponiveis | Lista canis livres; exige data_entrada e data_saida na consulta. |
| GET /api/reservas | Lista reservas ativas e canceladas com pets e cobrança. |
| GET /api/reservas/{reserva_id} | Consulta uma reserva. |
| POST /api/reservas | Reserva um canil para um ou dois pets. |
| PUT /api/reservas/{reserva_id} | Altera canil, datas e pets de uma reserva ativa. |
| DELETE /api/reservas/{reserva_id} | Cancela a reserva, mantendo o histórico; retorna 204. |

Retornos: 200 para consulta/atualização, 201 para criação, 204 para exclusão, 404 para recurso ausente, 409 para conflito de integridade, 422 para entrada inválida e 503 para conexão indisponível. Mensagens internas do banco não são expostas.

PUT recebe todos os campos obrigatórios. Nomes têm espaços externos removidos; campos desconhecidos e caracteres nulos são rejeitados. Telefone usa + e 8 a 15 algarismos, incluindo país e DDD; separadores comuns são removidos. A validação confere o formato, não a existência do número. Raça vazia vira null.

Espécies com nome ou código equivalente são recusadas. Sinônimos exigem cuidado no cadastro. Pet com histórico de reserva pode corrigir nome e raça, mas não trocar dono ou espécie, preservando as regras de compartilhamento.

## Reservas

POST e PUT recebem canil_id, pet_ids (lista de um ou dois IDs), data_entrada e data_saida no formato AAAA-MM-DD. Exemplo de corpo:

```json
{"canil_id": 5, "pet_ids": [1, 2], "data_entrada": "2026-10-20", "data_saida": "2026-10-22"}
```

Os IDs dos pets devem existir. Dois pets só podem compartilhar se ambos forem cachorros do mesmo dono. Outras espécies ficam individualmente. A resposta contém diarias, tarifa_diaria e valor_total. Valores monetários são enviados como texto decimal para preservar centavos: "50.00" e "150.00", por exemplo.

Entrada e saída contam na ocupação e na cobrança: 20 a 22 são três diárias; o canil só fica disponível a partir de 23. Datas iguais correspondem a uma diária. Datas passadas são aceitas, pois o enunciado não definiu proibição.

A tarifa de novas reservas fica em TARIFA_DIARIA, no módulo reservas.py, inicialmente R$ 50. O valor aplicado é salvo na reserva. PUT recalcula os dias e o total com a tarifa original, mesmo que o valor para novas reservas tenha mudado. A API não recebe preço enviado pelo cliente.

DELETE cancela e libera a ocupação; não apaga os vínculos com pets. Repetir o cancelamento retorna 204. Não há reativação nem edição de reserva cancelada; uma nova hospedagem exige nova reserva.

A disponibilidade é uma consulta do momento, não uma garantia de vaga até a confirmação. Ao gravar, a API verifica novamente os conflitos. A transação bloqueia primeiro os canis envolvidos, em ordem de ID, depois os pets, também em ordem de ID, e grava reserva e vínculos juntos. Na edição, inclui o canil anterior e o destino. O bloqueio do canil evita impasses entre inserções concorrentes na restrição de exclusão; essa restrição permanece como proteção de integridade do banco. O mesmo pet também não pode ocupar reservas ativas simultâneas em canis diferentes.

## Organização

- `app/main.py`: inicia a aplicação, registra as rotas e trata indisponibilidade do banco.
- `app/database.py`: abre conexão; usada com `with` para fechar e confirmar/desfazer a transação automaticamente.
- `app/donos.py`, `pets.py`, `especies.py` e `canis.py`: rotas e SQL parametrizado por recurso.
- `app/schemas.py`: validação de entrada e formatos de resposta.
- `app/reservas.py`: rotas, validação de compartilhamento e conflitos, transações e cálculo da cobrança.

Optei por manter as regras de reserva em funções do próprio módulo, sem criar camadas de serviço ou repositórios genéricos. `preparar_gravacao_reserva` coordena quatro passos: bloquear canis, bloquear pets, validar participantes e verificar conflitos. Todos usam a conexão e a transação do endpoint. Usei parâmetros do Psycopg nas consultas, sem concatenar os valores recebidos no SQL.

## Testes

```powershell
& .\.venv\Scripts\python.exe -X utf8 -m pytest -q
```

Esse comando executa os testes de banco e API. Os testes de API criam schemas exclusivos, aplicam a estrutura e removem seus schemas ao terminar. Usam registros fictícios, sem alterar os cadastros reais. Precisam de PostgreSQL acessível e permissão de criar schemas/extensão no banco local.

O [guia dos testes](../tests/README.md) explica o propósito de cada grupo e os limites da cobertura. Simplifiquei a suíte para priorizar fluxos completos e regras de integridade.

Os testes de IDs inválidos usam uma conexão propositalmente indisponível para verificar que a entrada é recusada antes de abrir a conexão. O teste de indisponibilidade usa o mesmo princípio para conferir a resposta 503.

O TestClient usa httpx2, conforme a versão de Starlette instalada. Essa dependência é somente de desenvolvimento.
