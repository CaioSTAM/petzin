# PetzIn

Projeto de um sistema de hospedagem para animais, desenvolvido durante um desafio para Desenvolvedor Full Stack Jr.

## Estado atual

A estrutura PostgreSQL e os cadastros da API FastAPI estão implementados: CRUD de donos e pets, consulta/cadastro de espécies e listagem de canis. Regras de reservas, interface React e configuração Docker ainda estão em desenvolvimento.

## Tecnologias escolhidas

- React para formularios e listagens organizados em componentes.
- Python e FastAPI para a API, aproveitando a familiaridade do candidato com Python.
- SQL parametrizado com Psycopg para tornar consultas, relacionamentos e transações explícitos.
- PostgreSQL para persistência e garantias de integridade.
- Docker previsto para execução reproduzível após o funcionamento local.

## Análise do modelo original

O rascunho mistura dados do dono, de dois pets e da reserva. Isso repete informações cadastrais, dificulta corrigir telefones e não identifica cada animal de maneira estável. Nomes e raças concatenados não permitem estabelecer vínculos confiáveis nem consultar o histórico individual.

A proposta separa Dono, Espécie, Pet, Canil, Reserva e ReservaPet. Cada pet referencia seu dono e sua espécie. A reserva ocupa um canil por período, e ReservaPet identifica individualmente os animais participantes.

## Regras e suposições principais

- 15 canis, conforme o enunciado.
- Cada canil possui somente id explícito de 1 a 15, usado também como identificação na interface.
- Até dois cachorros do mesmo dono podem compartilhar um canil; o mesmo dono representa a mesma família nesta versão.
- Uma reserva utiliza um canil; outros animais ficam individualmente.
- Entrada e saída inclusivas para ocupação e cobrança. Saída em 22/10 libera nova entrada a partir de 23/10. Essa contagem é uma suposição documentada.
- R$ 50,00 por canil/dia como tarifa de demonstração, preservada na reserva.
- Espécies cadastradas separadamente, sem detecção automática de sinônimos.

As dúvidas, alternativas, motivos e limitações estão em [requisitos e decisões](docs/requisitos-e-decisoes.md).

## Preparar e verificar o banco

As instruções de instalação da estrutura, execução dos testes e divisão das regras entre banco e futura API estão em [database/README.md](database/README.md).

Não versionar senhas, arquivo pgpass ou backups locais.

## Próximas etapas

Para instalar, executar e testar a API, consulte [backend/README.md](backend/README.md). A documentação interativa fica em http://127.0.0.1:8000/docs quando a API estiver em execução.

Próximos blocos: implementar reservas na API, integrar os formulários React, acrescentar Docker e completar aqui as instruções de execução do projeto inteiro.
