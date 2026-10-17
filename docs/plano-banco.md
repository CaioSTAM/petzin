# Implementação do banco PetzIn

**Objetivo:** implementar somente a estrutura do banco discutida na mentoria, preservando o cadastro de Dono já existente.

**Referência:** [requisitos e decisões](requisitos-e-decisoes.md).

**Execução:** autorizada pelo candidato em 17/10/2026; implementação nesta conversa, seguida de explicação e perguntas. Não autoriza gerar todo o backend ou frontend.

## Escopo

- Seis tabelas: dono, especie, pet, canil, reserva e reserva_pet.
- Datas inclusivas, saída no mesmo dia permitida, tarifa decimal positiva, status ativa/cancelada.
- Cinco espécies iniciais de demonstração; espécie com código estável para que a regra de cachorro não dependa do nome exibido.
- Quinze canis com id explícito de 1 a 15, também usado como número de identificação na interface, sem coluna numero separada.
- PKs, FKs, nomes não vazios, unicidade de espécies por nome sem distinção de caixa/espaços externos, proteção de referências e contra conflito de canil ativo.
- ReservaPet com chave composta; excluir fisicamente uma reserva remove apenas seus vínculos. A API deverá cancelar logicamente reservas, preservando o histórico.
- Quantidade de pets, compartilhamento por espécie/dono, conflito do mesmo pet e políticas de edição serão regras da API, ainda não implementada. A chave composta não limita a quantidade a dois.

## Arquivos

- `database/001_estrutura.sql`: criação das tabelas, índices, restrições e dados iniciais.
- `database/002_simplificar_canil.sql`: atualização das instalações que tinham id e numero em Canil.
- `tests/test_database.py`: testes reais via psql, isolados em schemas temporários e transações revertidas.
- `database/README.md`: aplicação, repetição, verificação e responsabilidades de cada camada.

## Passos e verificação

- [x] Escrever e executar os testes antes do SQL: observar falha por estrutura ausente.
- [x] Implementar o SQL mínimo para os contratos previstos.
- [x] Executar todos os testes e confirmar ausência de resíduos de teste.
- [x] Salvar backup do banco local fora do projeto antes da aplicação.
- [x] Aplicar o SQL em transação única, preservando Dono e seus registros.
- [x] Reaplicar para verificar repetição segura e conferir tabelas, restrições, espécies, canis e preservação do registro original.
- [x] Atualizar decisões; explicação e perguntas serão entregues ao candidato nesta conversa.

## Decisões de implementação

- Sem repositório Git inicializado: trabalhar na pasta atual, sem criar branch nem commit automaticamente.
- Usar restrição de exclusão do PostgreSQL com `btree_gist` para impedir sobreposição de canil no próprio banco, inclusive em concorrência. A proteção do pet continuará exigindo validação e coordenação no backend.
- Usar `codigo` em Espécie como identificação estável de negócio; ID permanece a chave estrangeira dos pets. A API não deverá permitir alterar esse código arbitrariamente.
- Raça opcional, exclusão lógica via status e sementes de demonstração seguem as propostas anteriores como escolhas de implementação, sem convertê-las em exigências da cliente.

## Resultado

21 testes passaram com `py -X utf8 -m unittest discover -s tests -v`. O primeiro ciclo teve falhas por ausência das novas tabelas. O teste concorrente foi validado também sem a restrição e falhou, como esperado, por aceitar duas reservas.

Dois testes inicialmente esperavam o SQLSTATE genérico de chave estrangeira (23503), mas PostgreSQL 18 informou 23001 para a exclusão RESTRICT. A expectativa foi corrigida para o comportamento observado, sem remover a proteção de produção.

Aplicação e repetição concluídas. Estado conferido: seis tabelas, um dono original preservado, cinco espécies, 15 canis, nenhum pet/reserva real de teste e zero schemas temporários restantes.

## Ajuste posterior: Canil com um identificador

Autorizado pelo candidato em 17/10/2026. SQL inicial atualizado e migração específica aplicada após backup, sem renumerar IDs. Referência de Reserva e restrição contra sobreposição preservadas; reaplicação dos dois scripts conferida. A suíte atual possui 25 testes aprovados, incluindo conversão com reserva vinculada e interrupção em caso de numeração antiga divergente.
