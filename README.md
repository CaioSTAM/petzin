# PetzIn

Sistema simples para gerenciar donos, pets e reservas de hospedagem, desenvolvido para o desafio de Desenvolvedor Full Stack Jr da Conecthus.

## Rodar com Docker

Pré-requisitos: Git e Docker com Compose. No Windows, abra o Docker Desktop usando containers Linux e aguarde `docker info` responder.

```powershell
git clone https://github.com/CaioSTAM/petzin.git
cd petzin
Copy-Item .env.example .env
```

Edite `.env` e substitua DB_PASSWORD por uma senha local. O arquivo fica fora do Git. Em Linux/macOS, use `cp .env.example .env`.

Na raiz do projeto:

```powershell
docker compose up --build -d --wait
```

A primeira execução baixa imagens e instala dependências; pode demorar alguns minutos. Não é necessário instalar Python, Node ou PostgreSQL na máquina para essa opção.

| Acesso | Endereço |
|---|---|
| Interface React | http://localhost:8080 |
| Documentação da API | http://localhost:8002/docs |
| Saúde do processo da API | http://localhost:8002/health |

O banco é inicializado com cinco espécies e os 15 canis. Donos, pets e reservas começam vazios. Cadastre um dono, depois os pets e então uma reserva.

O Docker usa um volume próprio, sem conectar ao PostgreSQL instalado na máquina. As portas 8080 e 8002 evitam as portas do desenvolvimento e podem ser alteradas por WEB_PORT e API_PORT no `.env`. O banco não publica porta no host.

### Porta ocupada ou segunda cópia na mesma máquina

Se já houver outra instalação em execução, escolha portas livres no `.env`. Para testar uma segunda cópia com banco e containers separados, defina também outro nome de projeto. Exemplo:

```dotenv
COMPOSE_PROJECT_NAME=petzin-copia
WEB_PORT=8082
API_PORT=8003
```

Mantenha DB_PASSWORD no arquivo e execute novamente `docker compose up --build -d --wait`. Nesse exemplo, a interface fica em http://localhost:8082 e a documentação em http://localhost:8003/docs. Troque esses valores se também estiverem ocupados. Só clonar em outra pasta não isola a instalação: o nome padrão do projeto é petzin.

### Parar, reiniciar e diagnosticar

```powershell
docker compose ps
docker compose logs --tail=100
docker compose down
docker compose up -d --wait
```

`down` preserva os dados no volume. Após alterar código, use novamente `docker compose up --build -d --wait`.

Para apagar **todos os dados da instalação Docker** e começar novamente:

```powershell
docker compose down -v
docker compose up --build -d --wait
```

O SQL de inicialização só roda com o volume vazio. Mudar DB_PASSWORD no `.env` não muda a senha de um banco já criado: mantenha a senha original ou recrie o volume de demonstração, sabendo que isso apaga seus dados. A migração 002 é apenas para instalações antigas com canil.numero; instalações novas aplicam somente 001.

Se a interface não abrir, confira `docker compose ps`, os logs e se a porta escolhida está livre. Se o comando não conectar ao Docker, aguarde o motor Linux do Docker Desktop iniciar. /health verifica o processo da API; falhas do banco são tratadas separadamente, com resposta 503 nas operações.

## Tecnologias

- Python/FastAPI: API REST, validação e documentação automática; Python foi escolhido pela maior familiaridade do candidato.
- PostgreSQL/Psycopg: SQL parametrizado, relacionamentos e transações explícitos, sem ORM.
- React com JavaScript: componentes para formulários e listagens, consumindo a API com fetch.
- Vite e CSS comum: desenvolvimento, build e estilo básico, sem biblioteca visual.
- Docker Compose/Nginx: serviços locais; Nginx serve o build e encaminha /api ao backend.

```text
backend/app/       API e regras de negócio
backend/tests/     testes de integração da API
frontend/src/      componentes e cliente HTTP
database/          estrutura e migração
tests/             testes de banco e guia da cobertura
docs/              PDF, decisões e conferência de requisitos
compose.yaml       serviços Docker
```

## Análise do modelo original

O JSON mistura dono, pets e reserva em um registro. "Rex e Bolinha" e "Labrador e Poodle" são textos concatenados: cada animal não tem identidade própria, e associar nome à raça depende de interpretar esses textos.

Se Carlos mudar de telefone, reservas que repetem esse telefone precisam ser atualizadas em vários lugares, podendo ficar inconsistentes. No modelo proposto, o telefone está em Dono e é atualizado uma vez; os pets continuam vinculados pelo ID.

Para consultar Rex individualmente, usamos o ID do pet. ReservaPet liga esse animal às reservas, sem depender do nome ou de quem foi hospedado junto. Se houvesse um histórico médico, cada registro clínico teria uma chave estrangeira pet_id, e a busca filtraria pelo ID do Rex. Assim, outro pet com o mesmo nome não misturaria os históricos. Essa relação descreve uma extensão do modelo; o desafio não especifica o cadastro de informações clínicas, que ficou fora da implementação.

valor_total_pago mistura o cálculo da hospedagem com comprovação de pagamento. Aqui a reserva guarda a tarifa aplicada e calcula o total pelo período. Não há registro de recebimentos ou quitação.

### Modelo corrigido

| Tabela | Responsabilidade |
|---|---|
| Dono | ID, nome e telefone. Um dono pode ter vários pets. |
| Espécie | ID, código estável e nome; identifica vários pets. |
| Pet | ID, nome, raça opcional, dono_id e especie_id. Cada pet tem um dono. |
| Canil | ID fixo de 1 a 15, que também identifica a acomodação. |
| Reserva | Um canil, entrada, saída, tarifa aplicada e status. |
| ReservaPet | Liga pets e reservas; a chave composta impede repetir o vínculo. |

O [SQL](database/001_estrutura.sql) apresenta chaves e restrições. As [decisões detalhadas](docs/requisitos-e-decisoes.md) registram dúvidas, suposições, motivos e limites.

Um pet pode participar de várias reservas ao longo do tempo. Cada reserva tem um ou dois participantes identificados em ReservaPet e ocupa exatamente um canil. Os dados cadastrais não precisam ser repetidos a cada hospedagem.

## Regras adotadas

- Existem 15 canis. Uma reserva usa um canil; dois canis correspondem a duas reservas.
- Um canil recebe um pet ou até dois cachorros do mesmo dono. Outras espécies ficam individualmente. Mesmo dono representa mesma família nesta versão.
- Datas inclusivas: entrada em 20/10 e saída em 22/10 são três diárias. Nova entrada nesse canil pode começar em 23/10. Não usamos horários.
- R$ 50 por canil/dia como tarifa de demonstração. Dois cachorros compartilhando não dobram o preço. A reserva preserva sua tarifa após um aumento para novas reservas.
- Editar datas recalcula o total com a tarifa original. Cancelar libera a vaga e mantém histórico; reserva cancelada não é editada nem reativada.
- Um pet não pode ter reservas ativas sobrepostas, mesmo em canis diferentes. Um canil não pode ter ocupações sobrepostas.
- Donos com pets e pets com reservas não são excluídos. Pet com histórico não troca dono ou espécie; nome e raça podem ser corrigidos.
- Telefone internacional obrigatório; nome e telefone do dono não são únicos. Raça desconhecida pode ficar vazia.
- Espécies têm cadastro próprio; a unicidade evita grafias equivalentes, mas não reconhece sinônimos.

Mesma família, contagem de diárias, uma reserva por canil, R$ 50 e políticas de alteração/cancelamento são interpretações ou decisões técnicas documentadas. O e-mail não define todos esses detalhes. Datas passadas são aceitas porque não há proibição no enunciado.

### Integridade e concorrência

Reserva e participantes são gravados na mesma transação. A API bloqueia primeiro os canis envolvidos, em ordem de ID, e depois os pets, também em ordem fixa, antes de verificar conflitos. Isso faz gravações concorrentes aguardarem sua vez e evita confirmações incompatíveis. Uma restrição de exclusão do PostgreSQL protege o período do canil.

A disponibilidade é uma consulta do momento; salvar valida novamente. Conflitos retornam 409, sem deixar alterações parciais. A regra do mesmo pet em canis distintos depende do fluxo da API; SQL manual não executa essa validação de negócio.

## API e execução sem Docker

A API permite CRUD de donos e pets, cadastro/listagem de espécies, consulta de canis e disponibilidade e criação, consulta, edição e cancelamento de reservas. Erros: 404 para IDs ausentes, 422 para entrada inválida, 409 para conflitos e 503 para banco indisponível.

Para desenvolvimento sem Docker, siga nesta ordem:

1. [Preparar PostgreSQL e aplicar a estrutura](database/README.md).
2. [Criar o ambiente Python e iniciar a API](backend/README.md).
3. [Instalar dependências e iniciar a interface](frontend/README.md).

Nesse modo, interface em http://127.0.0.1:5173 e API em http://127.0.0.1:8000. No Docker, use as portas 8080 e 8002.

## Testes e conferência

Com ambiente Python de desenvolvimento e PostgreSQL local preparados:

```powershell
& .\.venv\Scripts\python.exe -X utf8 -m pytest -q
```

São 47 casos de banco/API, com schemas isolados e registros fictícios. Dentro de frontend, `pnpm test` confere a regressão de resposta inválida e `pnpm build` verifica o build. Consulte o [guia dos testes](tests/README.md) e a [conferência da entrega](docs/verificacao-entrega.md).

Foram conferidos configuração Compose, build das imagens, subida com banco vazio, interface no navegador, integração com a API e preservação de registros após down/up. Os dados de teste foram mantidos em uma instalação Docker separada. A execução local sem Docker também foi verificada.

## Limites

Demonstração de uso interno, sem autenticação ou autorização. As portas Docker ficam restritas à máquina local; a configuração não está pronta para exposição pública. Não há pagamentos, módulo médico, notificações, dashboard, paginação ou persistência de rascunhos. Não versionar `.env`, senhas, pgpass ou backups.
