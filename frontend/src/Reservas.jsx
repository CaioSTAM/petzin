import React, { useRef, useState } from 'react';
import { api } from './api';
import { ConfirmAction, Field, FormActions, Table, date, money } from './components';

const empty = { dono_id: '', canil_id: '', data_entrada: '', data_saida: '', pet_ids: [] };

export default function Reservas({ data, execute, busy }) {
  const [form, setForm] = useState(empty);
  const [id, setId] = useState(null);
  const [availability, setAvailability] = useState(null);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState('');
  const requestVersion = useRef(0);
  const firstField = useRef(null);
  const pets = data.pets.filter((p) => p.dono_id === Number(form.dono_id));
  function change(values) {
    requestVersion.current += 1;
    setForm((current) => ({ ...current, ...values }));
    setAvailability(null); setError(''); setChecking(false);
  }
  function clear() { change(empty); setId(null); }
  function validDates() {
    if (!form.data_entrada || !form.data_saida || form.data_saida < form.data_entrada) {
      setError('Informe a entrada e uma saída igual ou posterior à entrada.');
      return false;
    }
    return true;
  }
  async function checkAvailability() {
    if (!validDates()) return;
    const version = ++requestVersion.current;
    setChecking(true); setError(''); setAvailability(null);
    try {
      const result = await api(`canis/disponiveis?${new URLSearchParams({ data_entrada: form.data_entrada, data_saida: form.data_saida })}`);
      if (version === requestVersion.current) setAvailability(result);
    } catch (err) {
      if (version === requestVersion.current) setError(err.message);
    } finally {
      if (version === requestVersion.current) setChecking(false);
    }
  }
  return <section>
    <h2>Reservas</h2>
    <p>Uma reserva por canil. Até dois cachorros do mesmo dono podem compartilhar; outros animais ficam sozinhos.</p>
    <p>Entrada e saída contam como diárias. Exemplo: dias 20 a 22 = 3 diárias. A tarifa aplicada aparece na reserva.</p>
    <h3>{id ? `Editar reserva #${id}` : 'Cadastrar reserva'}</h3>
    <form onSubmit={async (event) => {
      event.preventDefault();
      setError('');
      if (!validDates()) return;
      if (!form.pet_ids.length) { setError('Selecione pelo menos um pet.'); return; }
      const { dono_id, ...body } = form;
      if (await execute(`reservas${id ? `/${id}` : ''}`, id ? 'PUT' : 'POST', { ...body, canil_id: Number(body.canil_id) }, 'Reserva salva.', setError)) clear();
    }}>
      <div className="fields">
        <Field label="Dono dos pets"><select ref={firstField} required value={form.dono_id} onChange={(e) => change({ dono_id: e.target.value, pet_ids: [] })}>
          <option value="">Selecione</option>{data.donos.map((o) => <option key={o.id} value={o.id}>{o.nome} (#{o.id})</option>)}
        </select></Field>
        <Field label="Entrada"><input type="date" required value={form.data_entrada} onChange={(e) => change({ data_entrada: e.target.value })} /></Field>
        <Field label="Saída"><input type="date" required min={form.data_entrada || undefined} value={form.data_saida} onChange={(e) => change({ data_saida: e.target.value })} /></Field>
        <Field label="Canil"><select required value={form.canil_id} onChange={(e) => change({ canil_id: e.target.value })}>
          <option value="">Selecione</option>{data.canis.map((c) => <option key={c.id} value={c.id}>Canil {c.id}</option>)}
        </select></Field>
      </div>
      <fieldset><legend>Pets da reserva (até dois)</legend>
        {!form.dono_id ? <p>Selecione um dono.</p> : !pets.length ? <p>Esse dono ainda não tem pets cadastrados.</p> : pets.map((p) => <label className="checkbox" key={p.id}>
          <input type="checkbox" checked={form.pet_ids.includes(p.id)} disabled={!form.pet_ids.includes(p.id) && form.pet_ids.length === 2} onChange={(e) => change({ pet_ids: e.target.checked ? [...form.pet_ids, p.id] : form.pet_ids.filter((value) => value !== p.id) })} />
          {p.nome} (#{p.id}) — {data.especies.find((s) => s.id === p.especie_id)?.nome}
        </label>)}
      </fieldset>
      <button type="button" disabled={busy || checking} onClick={checkAvailability}>{checking ? 'Consultando…' : 'Consultar disponibilidade'}</button>
      {availability !== null && <p role="status">{availability.length ? `Canis livres: ${availability.map((c) => c.id).join(', ')}.` : 'Nenhum canil livre nesse período.'} A vaga será validada ao salvar.{id ? ' A reserva atual também ocupa seu canil nesta consulta.' : ''}</p>}
      {error && <p role="alert" className="error">{error}</p>}
      <FormActions editing={id} busy={busy} onClear={clear} />
    </form>
    <h3>Reservas cadastradas</h3>
    <Table headers={['ID', 'Canil', 'Pets', 'Entrada', 'Saída', 'Diárias', 'Tarifa', 'Total', 'Situação', 'Ações']} empty={!data.reservas.length}>
      {data.reservas.map((r) => <tr key={r.id}>
        <td>{r.id}</td><td>{r.canil_id}</td><td>{r.pet_ids.map((pid) => data.pets.find((p) => p.id === pid)?.nome || `#${pid}`).join(', ')}</td>
        <td>{date(r.data_entrada)}</td><td>{date(r.data_saida)}</td><td>{r.diarias}</td><td>{money(r.tarifa_diaria)}</td><td>{money(r.valor_total)}</td><td>{r.status === 'ativa' ? 'Ativa' : 'Cancelada'}</td>
        <td>{r.status === 'ativa' && <div className="actions"><button disabled={busy} onClick={() => {
          setId(r.id); change({ dono_id: String(data.pets.find((p) => p.id === r.pet_ids[0])?.dono_id || ''), canil_id: String(r.canil_id), data_entrada: r.data_entrada, data_saida: r.data_saida, pet_ids: [...r.pet_ids] }); firstField.current.focus();
        }}>Editar</button>
          <ConfirmAction label="Cancelar reserva" description={`Cancelar a reserva #${r.id}? O canil será liberado e o histórico será mantido.`} busy={busy} onConfirm={async () => {
            const ok = await execute(`reservas/${r.id}`, 'DELETE', null, 'Reserva cancelada.');
            if (ok && id === r.id) clear();
            return ok;
          }} /></div>}</td>
      </tr>)}
    </Table>
  </section>;
}
