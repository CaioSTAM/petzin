# API PetzIn

API de cadastros com PostgreSQL: CRUD de donos e pets, consulta e cadastro de espécies e listagem de canis. Reservas serão acrescentadas no próximo bloco.

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

Retornos: 200 para consulta/atualização, 201 para criação, 204 para exclusão, 404 para recurso ausente, 409 para conflito de integridade, 422 para entrada inválida e 503 para conexão indisponível. Mensagens internas do banco não são expostas.

PUT recebe todos os campos obrigatórios. Nomes têm espaços externos removidos; campos desconhecidos e caracteres nulos são rejeitados. Telefone usa + e 8 a 15 algarismos, incluindo país e DDD; separadores comuns são removidos. A validação confere o formato, não a existência do número. Raça vazia vira null.

Espécies com nome ou código equivalente são recusadas. Sinônimos exigem cuidado no cadastro. Pet com histórico de reserva pode corrigir nome e raça, mas não trocar dono ou espécie, preservando as regras de compartilhamento.

## Organização

- `app/main.py`: inicia a aplicação, registra as rotas e trata indisponibilidade do banco.
- `app/database.py`: abre conexão; usada com `with` para fechar e confirmar/desfazer a transação automaticamente.
- `app/donos.py`, `pets.py`, `especies.py` e `canis.py`: rotas e SQL parametrizado por recurso.
- `app/schemas.py`: validação de entrada e formatos de resposta.

Neste bloco, não há camadas de serviço ou repositórios genéricos. Regras complexas de reserva serão separadas quando forem implementadas. A consulta por ID usa parâmetros do Psycopg; o valor recebido não é concatenado no SQL.

## Testes

```powershell
& .\.venv\Scripts\python.exe -X utf8 -m pytest -q
```

Esse comando executa os testes de banco e API. Os testes de API criam schemas exclusivos, aplicam a estrutura e removem seus schemas ao terminar. Usam registros fictícios, sem alterar os cadastros reais. Precisam de PostgreSQL acessível e permissão de criar schemas/extensão no banco local.

O [guia dos testes](../tests/README.md) explica o propósito de cada grupo e os limites da cobertura. A suíte foi simplificada para priorizar fluxos completos e regras de integridade.

Os testes de IDs inválidos usam uma conexão propositalmente indisponível para verificar que a entrada é recusada antes de abrir a conexão. O teste de indisponibilidade usa o mesmo princípio para conferir a resposta 503.

O TestClient usa httpx2, conforme a versão de Starlette instalada. Essa dependência é somente de desenvolvimento.
