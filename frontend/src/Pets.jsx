import React, { useRef, useState } from 'react';
import { ConfirmAction, Field, FormActions, Table } from './components';

const empty = { nome: '', dono_id: '', especie_id: '', raca: '' };

export default function Pets({ data, execute, busy }) {
  const [form, setForm] = useState(empty);
  const [id, setId] = useState(null);
  const [other, setOther] = useState(false);
  const firstField = useRef(null);
  const common = data.especies.filter((s) => ['cachorro', 'gato'].includes(s.codigo));
  const others = data.especies.filter((s) => !['cachorro', 'gato'].includes(s.codigo));
  function clear() { setForm(empty); setId(null); setOther(false); }
  return <section>
    <h2>Pets</h2>
    <h3>{id ? `Editar pet #${id}` : 'Cadastrar pet'}</h3>
    {!data.donos.length && <p>Cadastre um dono antes de cadastrar seu pet.</p>}
    <form onSubmit={async (event) => {
      event.preventDefault();
      const body = { ...form, dono_id: Number(form.dono_id), especie_id: Number(form.especie_id), raca: form.raca.trim() || null };
      if (await execute(`pets${id ? `/${id}` : ''}`, id ? 'PUT' : 'POST', body, 'Pet salvo.')) clear();
    }}>
      <div className="fields">
        <Field label="Nome do pet"><input ref={firstField} required value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} /></Field>
        <Field label="Dono"><select required value={form.dono_id} onChange={(e) => setForm({ ...form, dono_id: e.target.value })}>
          <option value="">Selecione</option>{data.donos.map((o) => <option key={o.id} value={o.id}>{o.nome} (#{o.id})</option>)}
        </select></Field>
        <Field label="Espécie"><select required value={other ? 'outros' : form.especie_id} onChange={(e) => {
          setOther(e.target.value === 'outros');
          setForm({ ...form, especie_id: e.target.value === 'outros' ? '' : e.target.value });
        }}>
          <option value="">Selecione</option>{common.map((s) => <option key={s.id} value={s.id}>{s.nome}</option>)}<option value="outros">Outros</option>
        </select></Field>
        {other && <Field label="Outra espécie"><select required value={form.especie_id} onChange={(e) => setForm({ ...form, especie_id: e.target.value })}>
          <option value="">Selecione a espécie</option>{others.map((s) => <option key={s.id} value={s.id}>{s.nome}</option>)}
        </select></Field>}
        <Field label="Raça (opcional)"><input value={form.raca} onChange={(e) => setForm({ ...form, raca: e.target.value })} /></Field>
      </div>
      <FormActions editing={id} busy={busy} onClear={clear} />
    </form>
    <h3>Pets cadastrados</h3>
    <Table headers={['ID', 'Nome', 'Dono', 'Espécie', 'Raça', 'Ações']} empty={!data.pets.length}>
      {data.pets.map((p) => <tr key={p.id}>
        <td>{p.id}</td><td>{p.nome}</td><td>{data.donos.find((o) => o.id === p.dono_id)?.nome || `#${p.dono_id}`}</td>
        <td>{data.especies.find((s) => s.id === p.especie_id)?.nome || `#${p.especie_id}`}</td><td>{p.raca || 'Não informada'}</td>
        <td className="actions"><button disabled={busy} onClick={() => {
          setId(p.id); setForm({ nome: p.nome, dono_id: String(p.dono_id), especie_id: String(p.especie_id), raca: p.raca || '' });
          setOther(!common.some((s) => s.id === p.especie_id)); firstField.current.focus();
        }}>Editar</button>
          <ConfirmAction label="Excluir" description={`Excluir ${p.nome}? Pets com reservas não podem ser excluídos.`} busy={busy} onConfirm={async () => {
            const ok = await execute(`pets/${p.id}`, 'DELETE', null, 'Pet excluído.');
            if (ok && id === p.id) clear();
            return ok;
          }} /></td>
      </tr>)}
    </Table>
  </section>;
}
