# PetzIn — requisitos, dúvidas e decisões

Usei o [PDF completo](<desafio 3.pdf>), incluindo o e-mail da cliente, como referência. Registrei abaixo as dúvidas que afetam o funcionamento, as escolhas que fiz e seus limites.

Uma suposição adotada para completar o enunciado não equivale a uma confirmação da cliente.

## Requisitos do enunciado

- Sistema web para gerenciar pets e reservas de hospedagem.
- Cadastro de cachorros, gatos e outros animais, com nome, raça e dono.
- Reservas com entrada e saída, em um hotel com 15 canis.
- Compartilhamento de um canil por até dois cachorros da mesma família.
- Valor fixo por canil usado por dia e recusa quando não houver vaga no período.
- Análise do modelo original e proposta que separe donos, pets e reservas.
- API REST, interface simples com componentes e integração, tratamento de exceções.
- Repositório público e README com instalação, execução, tecnologias e análise. Docker é um diferencial.

## 1. Quem acessa o sistema?

**Dúvida:** os tutores também acessam a aplicação?

**Suposição:** adotei uso interno pela proprietária e pelos funcionários. Dono é um cadastro, sem conta de acesso.

**Motivo e limite:** o enunciado não descreve portal do tutor, autenticação ou permissões. Esses fluxos ficaram fora da versão entregue.

## 2. Dono, família e compartilhamento

**Dúvida:** o que significa mesma família? Um pet pode ter vários donos?

**Suposição:** cada pet tem um dono cadastrado; usei mesmo dono como critério de mesma família.

**Motivo e limite:** é uma relação verificável sem criar cadastro de famílias ou cotitularidade. Tutores cadastrados separadamente não serão reconhecidos como uma família.

## 3. Quantos animais cabem no canil?

**Dúvida:** o limite vale para todos os animais ou para todos os pets do dono?

**Decisão:** um dono pode ter vários pets. Uma reserva recebe um pet ou dois cachorros do mesmo dono. Outras espécies ficam individualmente.

**Motivo e limite:** o PDF autoriza compartilhar especificamente entre cachorros. Não estendi essa permissão a gatos ou outras espécies sem esclarecimento da cliente.

## 4. Quantos canis uma reserva utiliza?

**Dúvida:** uma reserva pode agrupar vários canis?

**Suposição:** uma reserva ocupa um único canil durante todo o período. Seus pets entram e saem juntos. Dois canis exigem duas reservas.

**Motivo e limite:** essa representação atende ao fluxo com menos relacionamentos. Agrupar acomodações exigiria itens de reserva e um vínculo de cada pet com esses itens.

## 5. Datas, horários e diárias

**Dúvida:** a saída libera o canil no mesmo dia? Esse dia é cobrado? Como garantir que o animal anterior já saiu sem registrar horário?

**Suposição:** usei somente datas, com entrada e saída inclusivas na ocupação e na cobrança. A retirada ocorre na data de saída, que continua reservada. A próxima entrada pode começar no dia seguinte.

**Motivo:** manter a mesma contagem para ocupação e cobrança, sem presumir horários de retirada ou limpeza.

| Entrada | Saída | Diárias | Total a R$ 50 | Próxima entrada |
|---|---|---|---|---|
| 20/10 | 22/10 | 3 | R$ 150 | 23/10 |
| 20/10 | 23/10 | 4 | R$ 200 | 24/10 |
| 20/10 | 20/10 | 1 | R$ 50 | 21/10 |

O cálculo é a diferença entre saída e entrada, mais um. Datas iguais representam uma diária; saída anterior à entrada é inválida. Períodos que compartilham uma data conflitam no mesmo canil.

**Alternativas consideradas:** saída exclusiva; ou bloquear o dia da saída sem cobrá-lo. Descartei ambas para manter a contagem coerente nesta versão.

**Limite:** uma retirada pela manhã mantém o dia cobrado e bloqueado. Essa convenção não foi definida pela cliente e precisaria de confirmação em uso real. Aceitei datas passadas porque não há proibição no enunciado.

## 6. Tarifa e pagamento

**Dúvida:** qual o valor da diária? Aumentar o preço muda reservas antigas? O total comprova pagamento?

**Decisão:** adotei R$ 50 por canil/dia como exemplo. A reserva guarda a tarifa aplicada; editar datas recalcula o total com essa tarifa. Dois cachorros no mesmo canil não dobram o preço.

**Motivo:** preservar a condição da reserva após uma mudança no preço padrão. Usei NUMERIC(10,2) no banco e Decimal no Python para os centavos. O total é calculado, sem outra coluna para repetir o resultado.

**Limite:** o PDF exige cobrança por canil/dia, mas não informa o preço. Total da hospedagem não comprova recebimento; pagamentos e quitação ficaram fora do escopo. O navegador não define a tarifa.

## 7. Identidade e relacionamentos

**Dúvida:** como identificar cada pet e evitar repetir o telefone do dono em cada hospedagem?

**Decisão técnica:** separei Dono, Pet, Espécie, Canil, Reserva e ReservaPet. Pet referencia dono e espécie; reserva referencia canil. ReservaPet liga os participantes à reserva.

**Motivo:** nomes podem repetir ou mudar. O telefone fica em Dono e é atualizado uma vez. Cada pet pode ser consultado por ID, mesmo quando hospedado com outro animal.

Dono possui vários pets, então dono_id não é único em Pet. A chave composta (reserva_id, pet_id) impede repetir o mesmo vínculo, mas não limita a reserva a dois animais: essa regra é validada pela API.

## 8. Espécies e duplicidade

**Dúvida:** lista fixa limita os animais atendidos; texto livre gera grafias diferentes e prejudica consultas.

**Decisão:** usei um cadastro extensível de espécies e seleção por ID. Cachorro e Gato aparecem na seleção principal; Outros revela as demais espécies cadastradas. O pet guarda a espécie efetiva, sem uma espécie genérica chamada Outros.

**Motivo:** centralizar a identificação e permitir novas espécies. Nome normalizado e código único impedem duplicidades de caixa, espaços externos ou códigos equivalentes. O código estável identifica cachorro sem depender do nome exibido ou do ID gerado.

**Limites:** não há detecção automática de sinônimos, como Cão e Cachorro. Conferir a lista antes de incluir continua necessário. Um futuro dashboard poderia agrupar por especie_id, mas dependeria dessa consistência semântica.

A lista inicial tem Cachorro, Gato, Coelho, Hamster e Porquinho-da-índia. Os três últimos são exemplos, não um catálogo aprovado pela cliente. Descartei texto livre após Outros e lista fechada sem cadastro. Mantive select nativo, sem busca personalizada nesta versão.

## 9. Campos obrigatórios e unicidade

**Dúvida:** nome e telefone identificam uma pessoa? Como preencher raça desconhecida?

**Decisão:** o dono tem ID gerado, nome e telefone obrigatórios. Nome e telefone não são únicos: pessoas podem compartilhar esses valores. CPF e e-mail não foram acrescentados ao modelo.

**Telefone:** armazenei texto com +, país, DDD e número, com 8 a 15 algarismos após remover separadores comuns. A validação confere formato, não a existência do número.

**Raça:** permiti null quando desconhecida ou não aplicável. Não preenchi automaticamente com SRD, pois falta de informação não significa ausência de raça definida.

**Motivo e limite:** evitar dados inventados e identidade baseada em campos mutáveis. Obrigatoriedade do telefone e raça opcional são interpretações adotadas, não regras detalhadas pelo PDF.

## 10. CRUD, exclusão e histórico

**Dúvida:** excluir cadastros deve apagar suas reservas? Como tratar cancelamento e edição?

**Decisão:** implementei CRUD de donos e pets, criação/consulta/edição/cancelamento de reservas, cadastro/listagem de espécies e consulta dos canis fixos. Não há CRUD de canis nesta versão.

DELETE de reserva cancela e preserva os vínculos; repeti-lo retorna 204. Reserva cancelada não é editada nem reativada. Outra hospedagem exige nova reserva. Editar reserva ativa revalida disponibilidade, excluindo a própria reserva da busca de conflitos.

**Motivo:** liberar a ocupação sem apagar o histórico. Dono com pets e pet com reservas não podem ser excluídos. Pet com histórico pode corrigir nome e raça, mas não trocar dono ou espécie, evitando invalidar o compartilhamento já registrado.

**Limites:** não há transferência de propriedade nem versões históricas de cadastros. O banco protege as referências; se uma reserva for apagada por SQL direto, seus vínculos são removidos em cascata, sem apagar pets. A API utiliza cancelamento lógico.

## 11. Concorrência e gravação completa

**Dúvida:** duas pessoas podem consultar a mesma vaga livre e confirmar juntas? E reservar o mesmo pet em canis diferentes?

**Decisão técnica:** gravei reserva e participantes na mesma transação. Na criação, bloqueio primeiro os canis envolvidos por ID em ordem crescente, depois os pets também por ID. Na edição, bloqueio antes a reserva atual e incluo canil anterior/destino e pets anteriores/novos nos bloqueios. Só depois consulto conflitos e gravo.

**Motivo:** apenas consultar disponibilidade ou abrir uma transação sem coordenar as gravações não resolve a disputa. A consulta após os bloqueios considera a confirmação da operação concorrente. Uma falha desfaz a operação inteira.

Usei FOR NO KEY UPDATE nos canis e FOR UPDATE nos pets. A restrição EXCLUDE do PostgreSQL, com btree_gist, também protege períodos inclusivos de reservas ativas do mesmo canil. O bloqueio anterior do canil evita a disputa entre inserções simultâneas no índice de exclusão.

**Limites:** operações no mesmo canil podem aguardar mesmo para períodos diferentes; aceitei esse custo em transações curtas para 15 canis. A restrição do banco não protege o mesmo pet em outro canil: essa garantia depende do fluxo da API. Não há auditoria das versões anteriores de reservas editadas.

## 12. Histórico médico de Rex

**Dúvida:** a pergunta do PDF exige implementar prontuário?

**Interpretação:** tratei a pergunta como análise da identidade individual. Um registro clínico poderia referenciar pet_id, permitindo buscar Rex sem misturar outro animal com o mesmo nome.

**Motivo e limite:** o enunciado não define campos ou operações médicas. Documentei essa extensão do modelo, sem implementar um módulo clínico.

## 13. Identificação do canil

**Dúvida:** manter id e numero com os mesmos valores resolve alguma necessidade?

**Decisão técnica:** mantive apenas id, com valores explícitos de 1 a 15, sem geração automática. Ele também identifica a acomodação na interface.

**Motivo e limite:** não há necessidade de renumeração independente. Uma mudança futura deve respeitar as referências. A migração 002 atende instalações antigas com numero e preserva os vínculos; novas instalações usam somente 001.

## 14. Stack e organização

**Dúvida:** qual stack permite entregar e explicar a solução com clareza?

**Decisão:** escolhi Python/FastAPI pela familiaridade com Python, PostgreSQL e SQL parametrizado com Psycopg para explicitar as consultas, e React com JavaScript para os componentes da interface. Mantive funções por recurso, sem ORM ou camadas genéricas.

**Motivo e limite:** concentrei o esforço nas regras e integração. SQL manual exige cuidado com parâmetros e transações. Java/Spring e ORM eram alternativas válidas, mas exigiriam aprender mais ferramentas durante esta entrega.

## 15. Interface simples

**Dúvida:** como consumir a API sem acrescentar complexidade de frontend?

**Decisão:** usei Vite, CSS comum, formulários e tabelas com controles nativos. Separei componentes por recurso e funções de salvar, editar e excluir. Erros de salvamento aparecem perto do botão; exclusões e cancelamentos pedem confirmação na própria tela.

**Motivo e limite:** componentes, estado, efeitos e fetch são suficientes para os fluxos. Não acrescentei biblioteca visual, roteamento, paginação ou gráficos. Trocar de seção mantém rascunhos; recarregar a página os descarta. Disponibilidade é informativa e sempre revalidada ao salvar. Na edição, a consulta ainda considera a ocupação da própria reserva.

## 16. Docker e prontidão

**Dúvida:** como iniciar a aplicação inteira e saber se ela pode acessar o banco?

**Decisão:** reuni PostgreSQL 18, API e React servido pelo Nginx no Compose. O banco tem volume próprio e não publica porta. A API e a interface ficam vinculadas à máquina local. O SQL inicial roda apenas com volume vazio.

**Motivo:** executar sem instalar os runtimes no host. O Compose aguarda o banco e usa /ready, que conecta e executa SELECT 1, antes de iniciar a interface. /health verifica somente o processo. Falha de conexão ou autenticação retorna 503 em /ready.

**Limites:** senha vem de .env fora do Git; mudá-la não altera a senha de um banco já criado. Remover volume apaga os dados. Não há configuração para produção pública, TLS ou autenticação de usuários. SELECT 1 verifica conexão, sem validar cada tabela ou regra da aplicação.

## 17. Testes e versionamento

**Dúvida:** quais verificações têm mais valor para este escopo?

**Decisão:** priorizei CRUD completo, erros representativos, cobrança, compartilhamento, cancelamento, edição conflitante, lotação dos 15 canis e concorrência. Os testes usam schemas isolados e registros fictícios; o [guia dos testes](../tests/README.md) descreve os grupos e os limites.

**Motivo e limite:** cobrir as regras que podem causar inconsistência sem repetir todas as variações em cada camada. Não há cobertura exaustiva de edições e cancelamentos simultâneos. Mantive branches curtas, revisão antes do merge e main com os incrementos verificados, sem uma develop permanente para este projeto individual.
