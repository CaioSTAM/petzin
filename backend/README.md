# API PetzIn

Primeiro bloco: consulta de donos com dados reais do PostgreSQL. Cadastro, edição, exclusão, pets e reservas ainda serão acrescentados.

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

Retornos: 200 para consulta válida, 404 quando o dono não existe, 422 para ID inválido e 503 quando a conexão com o banco está indisponível. Não expor mensagens internas de conexão ao usuário.

## Organização

- `app/main.py`: inicia a aplicação, registra as rotas e trata indisponibilidade do banco.
- `app/database.py`: abre conexão; usada com `with` para fechar e confirmar/desfazer a transação automaticamente.
- `app/donos.py`: rotas e consultas SQL simples de donos, com formato de resposta definido.

Neste bloco, não há camadas de serviço ou repositórios genéricos. Regras complexas de reserva serão separadas quando forem implementadas. A consulta por ID usa parâmetros do Psycopg; o valor recebido não é concatenado no SQL.

## Testes

```powershell
& .\.venv\Scripts\python.exe -X utf8 -m pytest -q
```

Esse comando executa os testes de banco e API. Os testes de API criam schemas exclusivos, aplicam a estrutura e removem seus schemas ao terminar. Usam registros fictícios, sem alterar os cadastros reais. Precisam de PostgreSQL acessível e permissão de criar schemas/extensão no banco local.

Os testes de IDs inválidos usam uma conexão propositalmente indisponível para verificar que a entrada é recusada antes de abrir a conexão. O teste de indisponibilidade usa o mesmo princípio para conferir a resposta 503.

O TestClient usa httpx2, conforme a versão de Starlette instalada. Essa dependência é somente de desenvolvimento.
