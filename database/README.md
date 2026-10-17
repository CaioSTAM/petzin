# Banco de dados PetzIn

Requer PostgreSQL 18 e Python 3 para os testes. A aplicação usará Psycopg, mas estes testes chamam o cliente `psql` diretamente e não exigem dependências Python adicionais.

## Aplicar a estrutura

No PowerShell, a partir da raiz do projeto:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -X -h localhost -p 5432 -U postgres -d petzin -v ON_ERROR_STOP=1 --single-transaction -f database/001_estrutura.sql
```

O banco `petzin` deve existir. O comando pede senha, a menos que exista autenticação configurada localmente. No Windows, o cliente pode usar `%APPDATA%\postgresql\pgpass.conf`. Esse arquivo fica fora do projeto e não deve ser versionado.

`--single-transaction` confirma a aplicação inteira ou desfaz em caso de falha. `ON_ERROR_STOP` interrompe no primeiro erro.

O script conserva a tabela Dono criada na mentoria. Objetos já existentes não são recriados, e sementes são incluídas sem duplicar os respectivos códigos/IDs. Isso permite repetir esta instalação inicial; não substitui migrações futuras de alteração de estrutura. Um objeto existente com estrutura incompatível exige investigação, não remoção automática.

### Atualizar quem já possuía id e numero em Canil

O banco local desta mentoria já foi atualizado. Para outro banco com a estrutura antiga, execute primeiro:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -X -h localhost -p 5432 -U postgres -d petzin -v ON_ERROR_STOP=1 --single-transaction -f database/002_simplificar_canil.sql
```

Depois é possível reaplicar `001_estrutura.sql`. Instalações novas precisam somente de `001_estrutura.sql`, que já contém o modelo simplificado.

A atualização confere se os valores antigos de id e numero coincidem, remove numero e a geração automática e mantém a chave primária e as referências. Se houver divergência, interrompe para revisão sem renumerar registros silenciosamente. Não é necessário recriar o banco ou apagar reservas.

## Tabelas

| Tabela | Referências e responsabilidade |
|---|---|
| dono | Responsável, com nome e telefone obrigatórios, sem unicidade desses dados. |
| especie | Nome de exibição e código estável. Nome único após remover espaços externos e ignorar caixa. |
| pet | Um dono e uma espécie existentes; raça pode ser desconhecida. |
| canil | Somente id, inteiro entre 1 e 15, definido explicitamente; identifica também a acomodação na interface. Sem dono fixo ou disponibilidade armazenada. |
| reserva | Um canil, entrada/saída inclusivas, tarifa decimal aplicada e status ativa/cancelada. |
| reserva_pet | Chave composta reserva/pet, sem repetição do vínculo. |

Não usamos ID de espécie fixo no código da futura API. O código `cachorro` identifica essa espécie independentemente do nome de exibição ou do ID gerado no ambiente. Inclusão de outras espécies deverá produzir código único; alterações desse código não serão expostas pelo CRUD comum.

Canil usa um único identificador porque não existe necessidade apresentada de renumerar a acomodação independentemente de suas referências. Essa simplificação não se aplica a nomes de donos ou pets, que não identificam unicamente seus registros.

## Regras garantidas pelo banco

- Identidade, referências existentes e campos essenciais preenchidos.
- Nomes equivalentes de espécies não duplicados; sinônimos ainda exigem revisão humana.
- Saída igual ou posterior à entrada; datas finitas.
- Tarifa decimal positiva, com padrão de demonstração de R$ 50,00.
- Apenas status ativa ou cancelada.
- Um pet não pode aparecer duas vezes na mesma reserva.
- Um canil não pode ter duas reservas ativas que compartilhem qualquer data, mesmo quando as gravações são simultâneas. Atualizações e reativações também respeitam essa restrição.
- Donos, espécies, pets e canis referenciados não podem ser excluídos fisicamente.

A proteção de período usa a extensão `btree_gist` e uma restrição `EXCLUDE`: considera o mesmo canil e a interseção dos intervalos de datas. As extremidades são inclusivas. Uma saída em 22/10 conflita com outra entrada em 22/10; entrada em 23/10 é permitida.

## Regras implementadas na API

- Exigir um pet ou dois cachorros do mesmo dono na reserva.
- Impedir que o mesmo pet participe de hospedagens ativas sobrepostas, mesmo em canis diferentes, inclusive em solicitações simultâneas.
- Gravar reserva e seus vínculos numa única transação. O SQL permite criar a reserva antes dos vínculos dentro dessa transação; a API deve conferir sua composição antes de confirmar.
- Proteger mudanças de dono/espécie que invalidariam reservas existentes.
- Normalizar e validar telefone e demais entradas, retornar erros compreensíveis e tratar conflitos de banco.
- Cancelar logicamente pela operação de exclusão da API, preservando histórico. A exclusão física de uma reserva remove somente seus vínculos em reserva_pet, nunca os pets.
- Calcular diárias como `(saída - entrada) + 1` e multiplicar pela tarifa aplicada. O banco não armazena total nem comprovação de pagamento.

Essas regras são executadas pela API; o schema sozinho não as garante. Consulte [as rotas e o funcionamento das transações](../backend/README.md). Escritas SQL diretas devem respeitar as mesmas regras.

## Executar os testes

```powershell
py -X utf8 -m unittest discover -s tests -v
```

O padrão de conexão é localhost, porta 5432, usuário postgres e banco petzin. Pode ser alterado por PGHOST, PGPORT, PGUSER e PGDATABASE; PSQL_PATH permite informar outro caminho do cliente.

Os testes comuns criam um schema temporário dentro de uma transação e desfazem tudo ao terminar. O teste concorrente precisa de duas conexões: cria um schema exclusivo, confirma uma disputa real e remove esse schema ao final. Nenhum caso cadastra dados de demonstração nas tabelas reais da aplicação.

O usuário dos testes precisa poder criar schemas e a extensão `btree_gist`. Em ambientes compartilhados, use banco de teste dedicado. O banco local de desenvolvimento desta mentoria usa postgres.

## Decisões e limites

As hipóteses da cliente e o raciocínio estão em [requisitos e decisões](../docs/requisitos-e-decisoes.md). A lista inicial adicional de espécies é demonstrativa. Não há módulo médico, pagamentos, autenticação ou dashboard nesta etapa.
