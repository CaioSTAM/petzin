import React, { useRef, useState } from "react";
import { ConfirmAction, Field, FormActions, Table } from "./components";

const empty = { nome: "", telefone: "" };

export default function Donos({ data, execute, busy }) {
  const [form, setForm] = useState(empty);
  const [id, setId] = useState(null);
  const firstField = useRef(null);
  function limparFormulario() {
    setForm(empty);
    setId(null);
  }
  async function salvarDono(event) {
    event.preventDefault();
    if (
      await execute(
        `donos${id ? `/${id}` : ""}`,
        id ? "PUT" : "POST",
        form,
        "Dono salvo.",
      )
    )
      limparFormulario();
  }
  function iniciarEdicao(dono) {
    setId(dono.id);
    setForm({ nome: dono.nome, telefone: dono.telefone });
    firstField.current.focus();
  }
  async function excluirDono(dono) {
    const excluido = await execute(
      `donos/${dono.id}`,
      "DELETE",
      null,
      "Dono excluído.",
    );
    if (excluido && id === dono.id) limparFormulario();
    return excluido;
  }
  return (
    <section>
      <h2>Donos</h2>
      <h3>{id ? `Editar dono #${id}` : "Cadastrar dono"}</h3>
      <form onSubmit={salvarDono}>
        <div className="fields">
          <Field label="Nome">
            <input
              ref={firstField}
              required
              value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })}
            />
          </Field>
          <Field label="Telefone com país e DDD">
            <input
              type="tel"
              required
              placeholder="+55 (92) 99999-9999"
              value={form.telefone}
              onChange={(e) => setForm({ ...form, telefone: e.target.value })}
            />
          </Field>
        </div>
        <FormActions editing={id} busy={busy} onClear={limparFormulario} />
      </form>
      <h3>Donos cadastrados</h3>
      <Table
        headers={["ID", "Nome", "Telefone", "Ações"]}
        empty={!data.donos.length}
      >
        {data.donos.map((dono) => (
          <tr key={dono.id}>
            <td>{dono.id}</td>
            <td>{dono.nome}</td>
            <td>{dono.telefone}</td>
            <td className="actions">
              <button disabled={busy} onClick={() => iniciarEdicao(dono)}>
                Editar
              </button>
              <ConfirmAction
                label="Excluir"
                description={`Excluir ${dono.nome}? Donos com pets não podem ser excluídos.`}
                busy={busy}
                onConfirm={() => excluirDono(dono)}
              />
            </td>
          </tr>
        ))}
      </Table>
    </section>
  );
}
