# Testes essenciais

Os testes verificam os fluxos principais e as regras que poderiam deixar dados inconsistentes. Não tentam testar todas as combinações de entrada.

Execute na raiz do projeto, com PostgreSQL disponível:

```powershell
& .\.venv\Scripts\python.exe -X utf8 -m pytest -q
```

## O que cada grupo protege

| Arquivo | Por que existe |
|---|---|
| `backend/tests/test_cadastros.py` | Confere os fluxos de dono e pet, espécies, canis, validação de entrada e proteção de cadastros com vínculos. |
| `backend/tests/test_donos.py` | Confere respostas básicas da API: saúde, recurso ausente, ID inválido e banco indisponível. |
| `tests/test_database.py` | Confere as regras de datas, tarifa, vínculos de reserva e ocupação dos canis, inclusive duas conexões disputando o mesmo canil. Também protege a migração que simplificou a identificação dos canis. |

Os fluxos de CRUD seguem a sequência criar → consultar → editar → excluir. São uma forma de verificar o uso normal do cadastro do começo ao fim.

Os testes de API usam o banco real em schemas exclusivos; não simulam as consultas SQL. Por isso, situações como excluir um dono com pets são verificadas pela API, sem repetir um teste SQL separado para a mesma situação. Isso reduz repetição, mas não oferece a mesma cobertura detalhada de cada camada isoladamente.

Mantivemos um caso de texto com caractere nulo porque ele já revelou um erro interno. O teste garante que essa entrada receba 422. Os demais casos da mesma validação compartilhada foram retirados.

O teste concorrente usa duas conexões: a primeira mantém uma reserva ainda sem confirmação, e a segunda tenta ocupar o mesmo canil no mesmo período. Só uma deve ser aceita. Esse caso é mais trabalhoso, mas protege uma regra central do desafio.

Os schemas de teste são removidos ao terminar. Os cadastros reais não são usados como dados de teste.

## Limites atuais

A suíte atual tem 35 casos executados, incluindo variações parametrizadas. Foram retirados casos repetidos entre API e banco, algumas verificações da estrutura interna e variações de erro de menor prioridade. Não houve mudança nas regras da aplicação.

As rotas de reservas ainda não estão implementadas. Os testes de banco sobre ocupação não substituem os futuros testes de compartilhamento, cobrança e reserva pela API.
