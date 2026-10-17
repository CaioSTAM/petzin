import React, { useRef, useState } from 'react';
import { ConfirmAction, Field, FormActions, Table } from './components';

const empty = { nome: '', telefone: '' };

export default function Donos({ data, execute, busy }) {
  const [form, setForm] = useState(empty);
  const [id, setId] = useState(null);
  const firstField = useRef(null);
  function clear() { setForm(empty); setId(null); }
  async function save(event) {
    event.preventDefault();
    if (await execute(`donos${id ? `/${id}` : ''}`, id ? 'PUT' : 'POST', form, 'Dono salvo.')) clear();
  }
  return <section>
    <h2>Donos</h2>
    <h3>{id ? `Editar dono #${id}` : 'Cadastrar dono'}</h3>
    <form onSubmit={save}>
      <div className="fields">
        <Field label="Nome"><input ref={firstField} required value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} /></Field>
        <Field label="Telefone com país e DDD"><input type="tel" required placeholder="+55 (92) 99999-9999" value={form.telefone} onChange={(e) => setForm({ ...form, telefone: e.target.value })} /></Field>
      </div>
      <FormActions editing={id} busy={busy} onClear={clear} />
    </form>
    <h3>Donos cadastrados</h3>
    <Table headers={['ID', 'Nome', 'Telefone', 'Ações']} empty={!data.donos.length}>
      {data.donos.map((owner) => <tr key={owner.id}>
        <td>{owner.id}</td><td>{owner.nome}</td><td>{owner.telefone}</td>
        <td className="actions"><button disabled={busy} onClick={() => { setId(owner.id); setForm({ nome: owner.nome, telefone: owner.telefone }); firstField.current.focus(); }}>Editar</button>
          <ConfirmAction label="Excluir" description={`Excluir ${owner.nome}? Donos com pets não podem ser excluídos.`} busy={busy} onConfirm={async () => {
            const ok = await execute(`donos/${owner.id}`, 'DELETE', null, 'Dono excluído.');
            if (ok && id === owner.id) clear();
            return ok;
          }} /></td>
      </tr>)}
    </Table>
  </section>;
}
