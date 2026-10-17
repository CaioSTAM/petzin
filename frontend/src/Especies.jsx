import React, { useState } from 'react';
import { Field, Table } from './components';

export default function Especies({ data, execute, busy }) {
  const [nome, setNome] = useState('');
  return <section>
    <h2>Espécies</h2>
    <p>Confira a lista antes de cadastrar para evitar nomes diferentes para a mesma espécie.</p>
    <form onSubmit={async (event) => {
      event.preventDefault();
      if (await execute('especies', 'POST', { nome }, 'Espécie cadastrada.')) setNome('');
    }}>
      <Field label="Nome da espécie"><input required value={nome} onChange={(e) => setNome(e.target.value)} /></Field>
      <button disabled={busy}>{busy ? 'Salvando…' : 'Cadastrar espécie'}</button>
    </form>
    <h3>Espécies cadastradas</h3>
    <Table headers={['ID', 'Nome']} empty={!data.especies.length}>
      {data.especies.map((species) => <tr key={species.id}><td>{species.id}</td><td>{species.nome}</td></tr>)}
    </Table>
  </section>;
}
