# Interface React

Criei uma interface básica para consumir a API, com formulários e listagens de donos, pets, reservas e espécies. Usei React, Vite e CSS comum, sem biblioteca visual, roteador ou gerenciador de estado adicional.

## Executar

Pré-requisitos: Node.js 22.12 ou superior, pnpm 11 e a API em execução conforme [instruções do backend](../backend/README.md).

Dentro da pasta frontend:

```powershell
pnpm install --frozen-lockfile
pnpm dev
```

Abra http://127.0.0.1:5173. O Vite encaminha /api para http://127.0.0.1:8000. Não é preciso alterar o CORS da API para esse fluxo.

Para apontar a outro endereço de API no PowerShell, antes de iniciar o Vite:

```powershell
$env:PETZIN_API_URL = "http://127.0.0.1:8001"
pnpm dev
```

## Build

```powershell
pnpm build
pnpm preview
```

O build fica em dist. O preview é uma conferência local e também encaminha /api ao backend. Na execução Docker, o Nginx serve esse build e encaminha /api; siga o README da raiz para iniciar os três serviços.

## Organização

- main.jsx: carrega dados, mantém a seção selecionada e executa as operações da API.
- Donos.jsx, Pets.jsx, Reservas.jsx e Especies.jsx: formulário e listagem de cada recurso.
- components.jsx: campos identificados, botões, tabela, confirmação e formatação.
- api.js: fetch e tradução das respostas de erro para mensagens.
- styles.css: estilo básico e ajuste para telas estreitas.

Os formulários ficam montados ao alternar seções para preservar o que foi digitado. Ao recarregar a página, rascunhos não são mantidos. Campos obrigatórios e datas usam validação nativa do navegador; a API continua validando todas as regras. Selects e calendários seguem a interface do navegador/sistema operacional.

Depois de uma alteração, as listas são recarregadas. O botão Atualizar dados permite buscar mudanças feitas por outra janela. A disponibilidade é informativa; a API valida novamente ao salvar. No formulário de edição, a reserva atual também aparece como ocupação na consulta de disponibilidade.

## Conferência funcional

Usar banco isolado ou registros de demonstração para estas verificações:

1. Cadastrar, editar e excluir um dono sem pets.
2. Cadastrar um pet vinculado a um dono; conferir edição, raça opcional e exclusão sem histórico.
3. Cadastrar uma espécie e selecioná-la em Outros no cadastro do pet.
4. Criar reserva dos dias 20 a 22 e conferir três diárias e R$ 150; editar a saída para 23 e conferir R$ 200.
5. Tentar excluir pet com reserva e conferir a mensagem de conflito. Cancelar a reserva e conferir que o histórico permanece.
6. Consultar disponibilidade, conferir mensagens de falha da API e usar Atualizar dados para tentar novamente.
7. Alternar seções com formulário preenchido, navegar por teclado e conferir a tabela em tela estreita.

Conferi esses fluxos no navegador com um schema PostgreSQL exclusivo e o removi ao terminar. Não acrescentei uma suíte de testes de componentes; mantive os testes automatizados do backend para suas regras.

`pnpm test` executa um teste de regressão do cliente HTTP: resposta HTML no lugar de JSON deve gerar mensagem de erro, em vez de causar tela branca. Depois de trocar branches com o Vite aberto, reinicie o servidor e confira o navegador, pois a troca temporária dos arquivos de configuração pode afetar o encaminhamento da API.
