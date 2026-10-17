# PetzIn — requisitos, dúvidas e decisões

Atualizado em 17/10/2026. Este documento registra as decisões discutidas durante a mentoria. A seção de execução ao final distingue o que já foi implementado do que ainda pertence às próximas etapas.

Fonte do desafio: [PDF completo](<desafio 3.pdf>). Prazo informado pelo candidato: 17/10/2026, às 15h, horário de Manaus.

## Como manter este registro

- Registrar cada dúvida de requisito ou regra de negócio e, logo abaixo, a interpretação escolhida e seu motivo.
- Distinguir o que a cliente pediu do que foi escolhido para completar uma informação ausente.
- Uma suposição aceita pelo candidato não passa a ser um requisito confirmado pela cliente.
- Registrar alternativas e limitações relevantes, sem transformar possibilidades em funcionalidades obrigatórias.
- Quando uma decisão mudar, marcar a anterior como substituída e atualizar os pontos afetados. Não manter regras contraditórias como vigentes.
- Atualizar este documento quando surgirem novas dúvidas ou esclarecimentos e antes de implementar a regra correspondente.
- Apresentar no README as decisões vigentes relevantes, com referência a este documento.

### Classificações

- **[CONFIRMADO PELO PDF]:** informação explícita do enunciado ou do e-mail completo.
- **[SUPOSIÇÃO TEMPORÁRIA]:** interpretação adotada para uma informação não definida pelo enunciado; indicar se aceita ou ainda proposta.
- **[PENDENTE DE RESPOSTA]:** ponto ainda não decidido ou que precisa de esclarecimento. Não significa, necessariamente, que uma pergunta já tenha sido enviada à empresa.
- **[MELHORIA OPCIONAL]:** possibilidade fora do núcleo combinado.
- **Decisão técnica:** forma escolhida para representar ou implementar uma necessidade; não atribuí-la à cliente.

## Requisitos confirmados

- Sistema web para gerenciar pets e reservas de hospedagem, substituindo planilhas.
- Cadastro de cachorros, gatos e outros animais, com nome, raça e identificação do dono.
- Reservas com datas de entrada e saída.
- Hotel com 15 canis.
- Até dois cachorros da mesma família podem compartilhar um canil.
- Cobrança de valor fixo por canil usado por dia; o valor numérico não foi informado.
- Recusa de reservas quando não houver disponibilidade no período.
- Análise crítica do modelo original e apresentação de modelagem que separe Donos, Pets e Reservas.
- API REST e interface simples consumindo a API, com atenção à componentização e integração.
- Tratamento de erros, especialmente datas inválidas e IDs inexistentes.
- Código em repositório Git público e README com instalação, execução, tecnologias, justificativas e análise.
- Docker citado como diferencial.

## Dúvidas e decisões

### 01. Conteúdo ausente do e-mail

**Dúvida:** o primeiro PDF tinha um trecho cortado que poderia conter regras importantes.

**Decisão:** não inventar a continuação. Após o recebimento do PDF completo, reler o documento e incorporar canis, compartilhamento, cobrança e disponibilidade ao núcleo.

**Motivo:** evitar implementação baseada em requisitos inexistentes.

**Status:** dúvida resolvida pelo PDF completo. A antiga pendência de formatação está encerrada; ambiguidades de negócio continuam registradas abaixo.

### 02. Quem usa o sistema?

**Dúvida:** os tutores dos animais também acessariam a aplicação?

**Suposição proposta:** uso interno pela proprietária e pelos funcionários. Dono de pet é um cadastro, sem significar uma conta de acesso.

**Motivo:** o enunciado apresenta uma ferramenta de gestão para o hotel e não descreve portal do tutor ou autenticação.

**Alternativa e limite:** acesso dos tutores exigiria definir autenticação, permissões e fluxos adicionais. Não foi incluído no escopo atual.

**Status:** [SUPOSIÇÃO TEMPORÁRIA], proposta na mentoria; sem confirmação explícita individual do candidato.

### 03. Dono, família e compartilhamento

**Dúvida:** o que significa “mesma família”? Um pet pode ter vários donos?

**Suposição aceita:** cada pet tem um dono cadastrado; para o compartilhamento, mesma família significa mesmo dono.

**Motivo:** oferece um critério verificável sem criar cadastro de famílias ou cotitularidade.

**Trade-off:** famílias com tutores cadastrados separadamente não serão reconhecidas automaticamente como uma única família.

**Como explicar:** o requisito exige conferir vínculo familiar; adotamos o dono comum como representação inicial e documentamos a interpretação.

**Status:** [SUPOSIÇÃO TEMPORÁRIA], aceita pelo candidato.

### 04. Limite de pets por canil

**Dúvida:** o limite de dois se aplica a todos os animais ou à quantidade de pets de um dono?

**Suposição aceita:** um dono pode cadastrar vários pets. Uma reserva comporta um pet ou dois cachorros do mesmo dono. Animais que não sejam cachorros ficam individualmente.

**Motivo:** a permissão de compartilhamento menciona especificamente cachorros. Não estendemos essa permissão a outras espécies.

**Trade-off:** outros compartilhamentos dependeriam de novo esclarecimento.

**Status:** limite para cachorros [CONFIRMADO PELO PDF]; interpretação para os demais casos [SUPOSIÇÃO TEMPORÁRIA], aceita.

### 05. Quantos canis uma reserva utiliza?

**Dúvida:** uma reserva pode agrupar vários canis?

**Suposição aceita:** uma reserva ocupa um único canil durante todo o período. Seus pets entram e saem juntos. Para usar dois canis, o dono terá duas reservas.

**Motivo:** atende ao fluxo descrito com menos relacionamentos e casos especiais.

**Alternativa e trade-off:** agrupar canis em uma reserva exigiria itens de acomodação e seus vínculos com os pets. A contratação agrupada fica fora desta versão.

**Status:** [SUPOSIÇÃO TEMPORÁRIA], aceita pelo candidato.

### 06. Datas, horários, ocupação e cobrança — decisão vigente

**Dúvida:** a saída libera o canil no mesmo dia? O dia da saída é cobrado? Sem horário, como garantir que o pet anterior já tenha sido retirado?

**Suposição aceita:** usar apenas datas. Entrada e saída são inclusivas tanto para ocupação quanto para cobrança. A data de saída representa o dia em que o animal será retirado; esse dia permanece reservado e é cobrado. Outra reserva no mesmo canil só pode começar no dia seguinte.

**Motivo:** manter a mesma contagem para dias ocupados e dias cobrados, sem depender de horários de retirada, entrada ou limpeza que não foram informados.

**Exemplos vigentes, a R$ 50 por diária e por canil:**

| Entrada | Saída | Diárias | Total | Próxima entrada possível |
|---|---|---|---|---|
| 20/10 | 22/10 | 3 | R$ 150 | 23/10 |
| 20/10 | 23/10 | 4 | R$ 200 | 24/10 |
| 20/10 | 20/10 | 1 | R$ 50 | 21/10 |

**Consequências para implementação e testes:**

- Quantidade de diárias: diferença em dias entre saída e entrada, mais um.
- Recusar saída anterior à entrada; datas iguais são permitidas e correspondem a uma diária.
- Dois períodos conflitam quando compartilham ao menos uma data no mesmo canil.
- Uma entrada no mesmo dia da saída de outra reserva é conflitante.
- Calcular disponibilidade considerando todo o período e somente reservas que ocupem o canil.
- Apresentar a convenção no formulário e na documentação.

**Trade-off:** mesmo uma retirada no início do dia mantém aquele dia bloqueado e cobrado. O sistema não representa trocas de ocupante dentro do mesmo dia.

**Como explicar:** como o desafio não define horários nem contagem de diária, adotamos uma convenção diária inclusiva e a tornamos explícita ao usuário.

**Status:** [SUPOSIÇÃO TEMPORÁRIA], aceita pelo candidato em 16/10/2026. Não é uma regra de cobrança confirmada pela cliente.

**Histórico substituído:** inicialmente propusemos saída exclusiva, permitindo outra entrada na mesma data e cobrança pela diferença entre datas. Depois foi sugerido bloquear a saída sem cobrar esse dia. Ambas as propostas foram substituídas pela regra inclusiva acima. A antiga exigência de saída estritamente posterior à entrada também foi substituída.

### 07. Valor da diária e preservação da tarifa

**Dúvida:** qual o preço? O valor pago do rascunho é o mesmo que o custo da hospedagem? Uma alteração de preço modifica reservas antigas?

**Decisão aceita:** usar R$ 50,00 por canil/dia como valor de demonstração. Guardar na reserva a tarifa aplicada e calcular o total usando essa tarifa e a contagem vigente. Compartilhar um canil não duplica a tarifa.

**Motivo:** manter a cobrança explicável e impedir que uma mudança na tarifa padrão altere automaticamente reservas anteriores.

**Distinção:** custo da hospedagem não comprova pagamento. Controle financeiro e pagamentos não integram o escopo atual.

**Escolhas de implementação:** NUMERIC(10,2) no banco; Decimal previsto para o futuro backend. Total calculado a partir das datas e da tarifa, sem duplicação desnecessária. Ao editar datas, preservar a tarifa já aplicada. A coluna decimal já foi implementada; cálculo e edição ainda dependem da API.

**Status:** cobrança por canil/dia [CONFIRMADO PELO PDF]; R$ 50 de exemplo e preservação da tarifa aceitos pelo candidato; contagem inclusiva conforme decisão 06.

### 08. Identidade, relacionamentos e normalização

**Dúvida:** como evitar repetir dados do dono e manter cada pet identificável, inclusive em reservas compartilhadas?

**Decisão aceita:** entidades Dono, Pet, Canil e Reserva, com associação ReservaPet; acrescentar Espécie conforme decisão 09. Pet referencia Dono e Espécie. Reserva referencia Canil. ReservaPet referencia Reserva e Pet.

**Motivo:** nomes podem se repetir e mudar. Identificadores mantêm os vínculos sem concatenar animais nem copiar o cadastro do dono em cada reserva.

**Detalhes discutidos:** dono_id em Pet não é único, pois um dono pode ter vários pets. ReservaPet usa chave primária composta (reserva_id, pet_id), que impede repetir o mesmo vínculo, mas não garante o limite de dois pets. Canil possui somente id, definido explicitamente entre 1 e 15 e usado também na interface; não possui dono fixo nem booleano de disponibilidade. O modelo anterior com id e numero foi substituído conforme decisão 15.

**Trade-off:** consultas precisam combinar tabelas relacionadas, em troca de evitar representações duplicadas do mesmo relacionamento.

**Status:** separação de Dono, Pet e Reserva [CONFIRMADO PELO PDF]; representação técnica discutida e aceita durante a mentoria.

### 09. Espécies, expansão da lista e duplicidades

**Dúvida:** uma lista fixa impediria cadastrar outros animais; texto livre produziria grafias diferentes e prejudicaria consultas e um eventual dashboard.

**Decisão aceita:** tabela Espécie, seleção por ID e cadastro de nova espécie em ação separada. A interface terá Cachorro, Gato e Outros; Outros permite pesquisar as demais espécies cadastradas. Pet guarda a espécie efetiva por especie_id, sem precisar guardar “Outros” como espécie.

**Motivo:** permitir ampliar a lista e concentrar a identificação das espécies em um cadastro único.

**Controle proposto:** impedir nomes equivalentes desconsiderando maiúsculas/minúsculas e espaços nas extremidades; mostrar opções existentes antes da inclusão. Essa proteção precisa existir no banco, não apenas na interface.

**Limitação aceita:** IDs e unicidade de nome não reconhecem sinônimos, como “Cão” e “Cachorro”. A consistência semântica depende de revisão humana. Não foi proposta identificação automática de sinônimos.

**Lista inicial implementada:** Cachorro e Gato, mencionados no PDF; Coelho, Hamster e Porquinho-da-índia como exemplos de demonstração. Não são catálogo aprovado pela cliente.

**Identificação estável implementada:** Espécie tem id, codigo e nome. O codigo permite reconhecer cachorro independentemente do nome exibido e do ID gerado no ambiente. A futura API deverá gerar códigos únicos para novas espécies e não permitir sua alteração pelo formulário comum.

**Alternativas substituídas:** texto complementar livre após “Outro”; posteriormente, lista fixa sem cadastro de novas espécies. A decisão vigente é o cadastro extensível e controlado acima.

**Como explicar:** a tabela centraliza a espécie e permite agrupar pets por ID; a qualidade de um dashboard ainda depende de evitar duplicidades de significado.

**Status:** [SUPOSIÇÃO TEMPORÁRIA] e decisão técnica aceitas; dashboard [MELHORIA OPCIONAL], fora da implementação atual.

### 10. Nome, telefone, raça e obrigatoriedade

**Dúvida:** quais informações são obrigatórias e quais são únicas?

**Decisão aceita para Dono:** id inteiro gerado pelo banco, nome e telefone obrigatórios. Nome e telefone não são únicos: pessoas podem compartilhar esses valores. A chave primária já garante unicidade e ausência de nulos para id.

**Telefone:** armazenar como texto, preservando código do país, DDD e número. Formato e validação exatos ainda precisam ser definidos; não presumir um único tamanho para todos os países.

**Escolha de implementação para raça:** permitir NULL quando desconhecida ou não aplicável. Não preencher automaticamente com SRD, pois ausência de informação não significa sem raça definida. Essa é uma interpretação técnica documentada, não uma exigência confirmada pela cliente.

**Motivo:** não exigir informação inventada nem usar dados cadastrais mutáveis como identidade.

**Escopo:** CPF e e-mail foram exemplos didáticos sobre unicidade, não requisitos acrescentados ao projeto.

**Status:** telefone obrigatório [SUPOSIÇÃO TEMPORÁRIA], aceita; raça opcional [SUPOSIÇÃO TEMPORÁRIA], adotada na implementação autorizada do banco.

### 11. CRUD, exclusões e preservação de histórico

**Dúvida:** quais operações entregar e o que acontece com registros referenciados quando alguém exclui um cadastro?

**Escopo aceito pelo candidato:** CRUD de donos, pets e reservas, além das regras centrais. Cadastro de espécies em operação separada, conforme decisão 09. Consulta dos 15 canis previamente cadastrados é a proposta atual; não há exigência expressa de CRUD de canis no PDF.

**Escolhas de implementação do banco:** bloquear exclusão física de dono com pets, de espécie com pets, de pet com reservas e de canil com reservas. Reserva tem status ativa/cancelada; a futura API deverá usar cancelamento lógico como operação de exclusão. O banco já ignora reservas canceladas no bloqueio de ocupação, mas a operação HTTP ainda não existe.

**Exclusão física excepcional:** se uma reserva for removida diretamente no banco, seus vínculos em ReservaPet são removidos junto; os pets não são excluídos. Isso não substitui o cancelamento lógico previsto para o fluxo normal.

**Motivo:** evitar apagar histórico ou deixar referências inválidas.

**Regras de edição a definir:** alterações devem revalidar disponibilidade sem considerar a própria reserva como conflito. Troca de dono ou espécie de um pet não pode invalidar silenciosamente o compartilhamento de reservas existentes.

**Status:** CRUD de donos, pets e reservas é requisito adicional aceito na conversa; políticas acima são escolhas de implementação documentadas. Restrições para alterar cadastros vinculados ainda precisam ser consolidadas na API.

### 12. Concorrência e gravação completa

**Dúvida:** duas solicitações podem encontrar a mesma vaga livre e confirmar reservas conflitantes? E o mesmo pet pode ser reservado simultaneamente em canis diferentes?

**Objetivo:** proteger canil e pets contra conflitos, inclusive concorrentes; gravar reserva e associações como uma operação indivisível.

**Estratégia vigente:** restrição de exclusão por canil e intervalo inclusivo no PostgreSQL, aplicada somente a reservas ativas, usando btree_gist. Ela protege criação, alteração e reativação mesmo com gravações concorrentes. Para evitar sobreposição de hospedagens do mesmo pet em canis diferentes, o futuro backend ainda precisará de transação e coordenação apropriadas.

**Motivo:** apenas consultar antes de inserir, ou apenas abrir uma transação sem coordenação adequada, não resolve a disputa.

**Alternativa substituída para canis:** usar somente bloqueios explícitos e verificação no backend. Optamos pela restrição no banco para manter a proteção mesmo em gravações diretas. Os conceitos de bloqueio continuam relevantes para outras regras.

**Trade-off:** a instalação inicial exige a extensão btree_gist e o aprendizado da restrição EXCLUDE. A proteção de canil não protege automaticamente o mesmo pet sendo reservado em outro canil.

**Status:** indisponibilidade deve impedir reservas [CONFIRMADO PELO PDF]; proteção concorrente de canil implementada e testada. Não sobrepor hospedagens do mesmo pet é interpretação de integridade a implementar no backend.

### 13. Histórico médico

**Dúvida:** a pergunta sobre buscar o histórico médico de Rex exige implementar prontuário?

**Interpretação proposta:** demonstrar que cada pet tem identidade própria e pode ter histórico individual. Não acrescentar módulo médico sem especificação dos dados e operações.

**Motivo:** a pergunta aparece na crítica ao modelo original, sem detalhar um prontuário.

**Status:** discussão da identificação individual [CONFIRMADO PELO PDF]; módulo médico [MELHORIA OPCIONAL], fora do escopo atual.

### 14. Stack e forma de trabalho

**Dúvida:** qual stack atende à avaliação e permite aprender, implementar e defender a solução no prazo?

**Escolha aceita:** React; Python e FastAPI; SQL parametrizado com Psycopg; PostgreSQL. Entrega local, testes essenciais, README e Docker.

**Motivo:** aproveitar familiaridade com Python e SQL e usar componentes explícitos no frontend, sem acrescentar um ORM ou aprender Java/Spring simultaneamente à primeira API.

**Alternativas discutidas:** Node/Express, Java/Spring Boot, SQLAlchemy/ORM e frontend sem framework. A proposta de frontend sem framework foi substituída pela escolha explícita de React pelo candidato.

**Trade-off:** aprender componentes, estado, propriedades e eventos de React; organizar manualmente consultas SQL e conversão dos resultados.

**Forma de trabalho vigente:** inicialmente, o candidato implementaria o núcleo com mentoria; depois autorizou a execução manual do banco pelo assistente. Em 17/10/2026, diante do prazo, autorizou implementar também o código da aplicação em blocos pequenos, com explicação e oportunidade de discordar das decisões a cada marco. Perguntas de estudo ficam para depois da entrega funcional. Essa orientação substitui a limitação anterior da autorização somente ao banco. Manter solução simples, verificável e compatível com a compreensão de um desenvolvedor júnior. Construir README durante as etapas e usar commits pequenos e coerentes.

**Status:** decisões técnicas e de trabalho aceitas; não são imposições do PDF.

### 15. Simplificação da identificação de Canil

**Dúvida:** por que manter id e numero com valores iguais? Essa separação resolve alguma necessidade atual?

**Alternativas:** manter um identificador interno e outro de exibição, permitindo renumeração independente; ou usar um único identificador estável para cada uma das 15 acomodações.

**Escolha autorizada pelo candidato:** manter somente id, inteiro e chave primária, com valores explícitos de 1 a 15. Não usar geração automática nesta tabela. Reserva continua referenciando canil_id.

**Motivo:** o desafio não apresenta necessidade de renumeração independente. Um único campo atende à identificação, às consultas e ao uso na interface.

**Trade-off:** o número passa a ser a identidade estável da acomodação; renumerações futuras precisam respeitar referências. Ter os dois campos seria tecnicamente válido, mas sua flexibilidade não é necessária neste escopo.

**Como explicar:** cada canil tem uma identificação fixa que também aparece na interface; não criamos uma segunda identificação sem uma necessidade concreta.

**Status:** decisão técnica aceita e aplicada em 17/10/2026. A quantidade de 15 canis é [CONFIRMADO PELO PDF]; usar IDs de 1 a 15 é nossa escolha técnica.

**Implementação:** instalação nova atualizada em 001_estrutura.sql e migração 002_simplificar_canil.sql para instalações anteriores. Os valores existentes coincidem; não houve renumeração. Chave estrangeira e proteção de ocupação preservadas. Backup anterior à alteração salvo fora do projeto. Os 25 testes passaram, incluindo conversão com reserva vinculada e recusa de IDs/números antigos divergentes.

### 16. Versionamento e repositório público

**Dúvida:** usar main e develop permanentes? Publicar ao final ou acompanhar os blocos desde agora?

**Escolha:** repositório público CaioSTAM/petzin, main com os blocos verificados e branches curtas por funcionalidade. Separar o trabalho existente em documentação, banco e consultas da API, com mensagens curtas. Novos blocos serão versionados conforme forem concluídos.

**Motivo:** manter rastreabilidade e revisão sem uma segunda branch permanente que não resolve uma necessidade atual do projeto individual.

**Trade-off:** main contém incrementos testados, mas o README deve informar claramente quais funcionalidades ainda estão pendentes. Um push pode enviar vários commits e preservar cada etapa.

**Status:** repositório e commits autorizados pelo candidato em 17/10/2026. Sem alteração artificial de datas do histórico.

**Fluxo de integração atualizado:** por ser um projeto individual, os próximos blocos não precisam de pull request. Antes de cada merge na main, revisar o código, corrigir os problemas encontrados e executar os testes; conferir novamente o resultado integrado antes de publicar. O PR inicial de cadastros foi fechado a pedido do candidato, mantendo o histórico do GitHub.

### 17. Validação e alterações dos cadastros

**Dúvidas:** qual formato de telefone aceitar? Como gerar códigos de espécies? Permitir trocar dono ou espécie de um pet que já participou de reservas?

**Escolhas:** telefone internacional com + e 8 a 15 algarismos, removendo espaços, parênteses, pontos e hífens. Código de espécie derivado do nome, sem acentos e com separadores padronizados; colisões de nome ou código retornam conflito. PUT recebe todos os campos obrigatórios. Raça vazia é salva como null. Nomes vazios, caracteres nulos e campos desconhecidos são recusados.

**Motivos:** ter dados previsíveis para consultas e formulários; responder com erro de entrada em vez de falha interna; manter o código de espécie estável para as regras de compartilhamento.

**Histórico:** pet vinculado a qualquer reserva, inclusive cancelada, não pode trocar dono ou espécie. Nome e raça podem ser corrigidos. Exclusão de dono com pets ou pet com reservas retorna conflito.

**Trade-offs:** a validação de telefone verifica formato, não existência. Códigos normalizados não detectam sinônimos. Bloquear alterações de vínculo com histórico é uma escolha conservadora desta versão, que não implementa transferência de propriedade nem versões históricas dos cadastros.

**Status:** decisões técnicas aplicadas na API em 17/10/2026, sem representar novos requisitos confirmados pela cliente.

### 18. Escopo dos testes

**Dúvida:** a suíte estava mais detalhada do que o necessário para uma entrega simples e dificultava o estudo do projeto.

**Escolha:** priorizar fluxos completos de cadastro, erros representativos e regras de integridade. Retirar testes SQL de situações já exercitadas pela API com PostgreSQL, algumas inspeções da estrutura interna e variações de erro de menor prioridade. Preservar a regressão do caractere nulo, a migração com reserva vinculada e a disputa simultânea por canil.

**Trade-off:** menos detalhamento por camada e menos combinações de erros. A redução não muda as validações da aplicação nem significa cobertura exaustiva. O guia tests/README.md registra o propósito dos grupos e os limites atuais.

**Status:** simplificação solicitada pelo candidato em 17/10/2026. A suíte passou de 59 para 35 casos executados; as contagens anteriores neste documento registram verificações históricas.

### 19. Operações e concorrência das reservas

**Dúvidas:** como tratar cancelamento, edição, aumento de tarifa e duas solicitações simultâneas para o mesmo pet em canis diferentes?

**Escolhas:** POST cria reserva ativa; PUT substitui canil, datas e participantes de reserva ativa; DELETE cancela sem apagar a reserva nem seus vínculos. Cancelamento repetido é aceito. Reserva cancelada não pode ser editada ou reativada. Uma nova hospedagem exige nova reserva.

**Cobrança:** tarifa de demonstração definida no backend e copiada para a reserva, sem receber preço do navegador. Alterar as datas recalcula o total com a tarifa original. Valores monetários usam Decimal e são enviados como texto com centavos. Datas passadas são aceitas, pois não houve regra da cliente proibindo cadastros retroativos.

**Concorrência:** bloquear os pets por ID em ordem fixa antes de validar conflitos e gravar. Na edição, incluir os participantes anteriores e os novos nos bloqueios. A transação confirma reserva e vínculos juntos ou desfaz tudo. A restrição de exclusão do banco protege a ocupação do canil; a API verifica também conflito do mesmo pet em outro canil.

**Motivo:** evitar gravação parcial e impedir que duas requisições confirmem hospedagens incompatíveis. A consulta de disponibilidade é informativa; a gravação precisa validar novamente.

**Trade-offs:** uma operação concorrente pode aguardar a outra e depois receber 409. A garantia para o mesmo pet depende de as gravações seguirem o fluxo da API; alterações SQL diretas não executam essas regras. Não há auditoria das versões anteriores de uma reserva editada, nem controle de pagamentos.

**Status:** decisões técnicas aplicadas em 17/10/2026, mantendo uma reserva por canil e as datas inclusivas já acordadas.

### 20. Interface React básica

**Pedido:** consumir a API com uma interface simples, sem foco em design elaborado nem técnicas avançadas de React.

**Escolhas:** React com JavaScript, Vite e CSS comum. Seções para donos, pets, reservas e espécies, com formulários e tabelas. Campos, selects e calendários nativos. Espécies divididas em Cachorro, Gato e Outros; a última opção revela outra seleção com as espécies restantes. Novas espécies são cadastradas em sua própria seção.

**Motivo:** permitir demonstrar os fluxos completos com poucos conceitos: componentes, estado, efeitos, eventos e fetch. Sem biblioteca visual, roteamento adicional, gráficos ou autenticação.

**Comportamento:** manter formulários montados entre seções para preservar rascunhos; bloquear botões enquanto salva; confirmar exclusão/cancelamento inline e mostrar erros da API. Um recarregamento completo da página descarta rascunhos. Atualizar dados busca as listas novamente, sem atualização automática por intervalo.

**Integração:** Vite encaminha /api ao backend durante desenvolvimento e preview local. A consulta de disponibilidade informa vagas do período; salvar sempre revalida no servidor. Ao editar, a consulta considera também a ocupação da própria reserva atual.

**Trade-offs:** sem busca personalizada de espécies, paginação ou estado persistido no navegador nesta versão. Select nativo permite navegação pelo teclado. A validação HTML melhora o preenchimento básico, mas as regras e os preços continuam sob responsabilidade da API.

**Status:** escopo solicitado e implementado em 17/10/2026. Fluxos conferidos no navegador com dados isolados, além do build da interface e dos testes do backend.

## Pontos para consolidar antes das respectivas implementações


## Verificações de maior valor

- Rejeitar datas inexistentes e saída anterior à entrada; aceitar datas iguais como uma diária.
- Recusar sobreposição inclusive no dia da saída; aceitar nova entrada no dia seguinte.
- Considerar todo o período ao procurar um canil livre.
- Validar pets existentes, sem repetição, e regras de quantidade, espécie e dono.
- Cobrar por canil/dia usando a tarifa aplicada, sem dobrar o preço por dois cachorros compartilhando.
- Proteger contra solicitações simultâneas conflitantes e contra gravação parcial.
- Revalidar regras em alterações e respeitar as políticas de exclusão que forem consolidadas.
- Reproduzir a execução do projeto seguindo o README e conferir o funcionamento com Docker.

## Execução da etapa do banco — 17/10/2026

- Autenticação local ajustada para o caminho real de APPDATA e o nome pgpass.conf; conteúdo permanece fora do projeto.
- Estrutura aplicada no banco petzin com seis tabelas, cinco espécies iniciais e 15 canis.
- Cadastro original de Dono preservado, conferido por comparação do conteúdo antes e depois da aplicação.
- Backup anterior à aplicação salvo fora do projeto, em pasta temporária local.
- Script reaplicado sem duplicar espécies ou canis.
- 21 testes automatizados passaram, incluindo duas conexões disputando o mesmo canil e proteção de datas inclusivas. O teste concorrente também foi executado sem a restrição no schema de teste: confirmou a falha esperada, demonstrando que detecta a ausência da proteção.
- Nenhum schema de teste permaneceu após a execução. Pets e reservas reais não foram criados pelos testes.
- API, interface React, validações entre pets, cálculo exposto de cobrança e Docker ainda não foram implementados.

## Primeiro bloco de API — 17/10/2026

- Implementadas consulta de donos por lista e ID e rota de saúde da API.
- SQL parametrizado via Psycopg e conexão aberta somente após validar o ID, com fechamento por contexto `with`.
- Respostas 404 para dono inexistente, 422 para ID inválido e 503 para indisponibilidade de conexão, sem expor detalhes internos.
- Suíte completa com 33 testes aprovados, mantendo 25 testes de banco e acrescentando 8 de API. Dados de API isolados em schemas de teste.
- Aplicação local iniciada na porta 8000, com documentação em /docs. CRUD de escrita, regras de reservas, interface e Docker continuam pendentes.
