# Conferência da entrega

Fonte: PDF completo docs/desafio 3.pdf, incluindo o e-mail da cliente. Esta conferência distingue implementação de execução efetivamente verificada.

| Pedido | Implementação ou evidência |
|---|---|
| Analisar problemas do JSON original | README: identidade individual, repetição do telefone, nomes/raças concatenados e separação entre cálculo e pagamento. |
| Apresentar modelo corrigido | Seis tabelas descritas no README e implementadas em database/001_estrutura.sql. |
| API REST | FastAPI com cadastros e reservas; documentação em /docs. |
| Interface simples consumindo API | React com componentes por recurso, fetch, formulários e tabelas; conferência em navegador. |
| Nome, raça e dono do pet | Cadastro de pet com dono_id e raça opcional quando desconhecida; decisão documentada. |
| Cachorros, gatos e outros animais | Espécies controladas, com cadastro extensível e seleção de Outros na interface. |
| 15 canis | Inicialização SQL com IDs de 1 a 15 e consulta na API. |
| Compartilhamento de até dois cachorros da mesma família | Verificação de quantidade, código da espécie e mesmo dono; suposição de família documentada. |
| Entrada e saída | Datas validadas; contagem inclusiva escolhida e documentada. |
| Preço fixo por canil/dia | Decimal, tarifa aplicada preservada e total calculado por diárias. R$ 50 é exemplo escolhido. |
| Recusar quando não houver vaga no período | Teste com os 15 canis ocupados, disponibilidade vazia e recusa da reserva adicional; proteção de conflitos na gravação. |
| Datas inválidas e IDs inexistentes | Respostas 422 e 404; conflitos 409 e indisponibilidade 503. |
| Qualidade e organização | Módulos por recurso, SQL parametrizado, componentes por seção, handlers nomeados e funções auxiliares pequenas. |
| Repositório público | https://github.com/CaioSTAM/petzin, commits por bloco e revisão antes de integrar. |
| README com instalação, execução, tecnologias e análise | README central e instruções detalhadas de backend, frontend e banco. |
| Docker como diferencial | Compose, Dockerfiles, Nginx e inicialização automática; imagens construídas, três serviços executados com volume vazio e prontidão da API com consulta ao banco. |

## Verificações de funcionamento

- Banco e API: suíte de integração com schemas isolados, incluindo compartilhamento, datas, cobrança, cancelamento, rollback e concorrência.
- Frontend: build e teste de regressão do cliente HTTP. Fluxos de cadastro, edição, exclusão, reserva e cancelamento conferidos no navegador com banco isolado.
- Interface básica conferida em tela estreita e por teclado. Dados reais preservados.
- Docker: `docker compose config --quiet` e `docker compose up --build -d --wait` aprovados em projeto de teste com volume novo e portas 18080/18002. Banco inicial com cinco espécies e 15 canis; cadastros vazios.
- Pelo Nginx, criados um dono, dois pets e uma reserva de três diárias, com total de R$ 150. Conflito de pet retornou 409; período invertido retornou 422; disponibilidade conferida. Build React aberto no navegador, exibindo a reserva sem erros de execução.
- Após `down` sem remover volume e novo `up`, dono e reserva permaneceram. Cancelamento manteve histórico e liberou a vaga.
- O repositório foi consultado pela API pública do GitHub: público, com main como branch padrão.
- Suíte atual: 49 casos de banco/API aprovados. Inclui hotel lotado, prontidão com banco disponível e retorno 503 quando indisponível, mantendo /health acessível.
- Depois das melhorias de legibilidade e mensagens, conferi os formulários no navegador com banco isolado. O teste do cliente HTTP e o build React passaram.
- Compose reconstruído e iniciado com os três serviços saudáveis; /ready retornou 200 após consultar o banco. Os volumes existentes foram preservados.
