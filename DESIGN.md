# Interface PetzIn

Interface interna de demonstração, em português, para consumir a API. O candidato pediu explicitamente um visual básico, sem elaboração de design.

- Fundo branco, texto escuro, fonte Arial do sistema, links e ações principais azuis. Sem imagens, animações, gráficos ou bibliotecas de componentes.
- Navegação por botões: Donos, Pets, Reservas e Espécies. Cada seção tem formulário e tabela. Canis são escolhidos na reserva.
- CSS em frontend/src/styles.css. Campos e botões nativos; selects e calendários seguem a apresentação do navegador/sistema operacional.
- Formulários preservam valores ao alternar seções. Salvamento bloqueia repetição; erros aparecem em texto e confirmações usam uma região de status.
- Exclusão/cancelamento exige confirmação inline, com nome do registro. Não usar diálogos nativos do navegador.
- Em tela estreita, campos ocupam a largura disponível e tabelas podem rolar horizontalmente.
- A API é a autoridade para regras de reserva e valores monetários. Disponibilidade consultada não garante a confirmação posterior.

Este arquivo registra escolhas simples do projeto; não haverá geração de propostas visuais nem um sistema de design adicional.
