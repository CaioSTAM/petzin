import React, { useRef, useState } from "react";
import { ConfirmAction, Field, FormActions, Table } from "./components";

const empty = { nome: "", dono_id: "", especie_id: "", raca: "" };

export default function Pets({ data, execute, busy }) {
  const [form, setForm] = useState(empty);
  const [id, setId] = useState(null);
  const [other, setOther] = useState(false);
  const firstField = useRef(null);
  const especiesPrincipais = data.especies.filter((especie) =>
    ["cachorro", "gato"].includes(especie.codigo),
  );
  const outrasEspecies = data.especies.filter(
    (especie) => !["cachorro", "gato"].includes(especie.codigo),
  );
  function limparFormulario() {
    setForm(empty);
    setId(null);
    setOther(false);
  }
  async function salvarPet(event) {
    event.preventDefault();
    const dadosPet = {
      ...form,
      dono_id: Number(form.dono_id),
      especie_id: Number(form.especie_id),
      raca: form.raca.trim() || null,
    };
    if (
      await execute(
        `pets${id ? `/${id}` : ""}`,
        id ? "PUT" : "POST",
        dadosPet,
        "Pet salvo.",
      )
    )
      limparFormulario();
  }
  function iniciarEdicao(pet) {
    setId(pet.id);
    setForm({
      nome: pet.nome,
      dono_id: String(pet.dono_id),
      especie_id: String(pet.especie_id),
      raca: pet.raca || "",
    });
    setOther(
      !especiesPrincipais.some((especie) => especie.id === pet.especie_id),
    );
    firstField.current.focus();
  }
  function selecionarEspecie(event) {
    const valor = event.target.value;
    setOther(valor === "outros");
    setForm({ ...form, especie_id: valor === "outros" ? "" : valor });
  }
  async function excluirPet(pet) {
    const excluido = await execute(
      `pets/${pet.id}`,
      "DELETE",
      null,
      "Pet excluído.",
    );
    if (excluido && id === pet.id) limparFormulario();
    return excluido;
  }
  return (
    <section>
      <h2>Pets</h2>
      <h3>{id ? `Editar pet #${id}` : "Cadastrar pet"}</h3>
      {!data.donos.length && (
        <p>Cadastre um dono antes de cadastrar seu pet.</p>
      )}
      <form onSubmit={salvarPet}>
        <div className="fields">
          <Field label="Nome do pet">
            <input
              ref={firstField}
              required
              value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })}
            />
          </Field>
          <Field label="Dono">
            <select
              required
              value={form.dono_id}
              onChange={(e) => setForm({ ...form, dono_id: e.target.value })}
            >
              <option value="">Selecione</option>
              {data.donos.map((dono) => (
                <option key={dono.id} value={dono.id}>
                  {dono.nome} (#{dono.id})
                </option>
              ))}
            </select>
          </Field>
          <Field label="Espécie">
            <select
              required
              value={other ? "outros" : form.especie_id}
              onChange={selecionarEspecie}
            >
              <option value="">Selecione</option>
              {especiesPrincipais.map((especie) => (
                <option key={especie.id} value={especie.id}>
                  {especie.nome}
                </option>
              ))}
              <option value="outros">Outros</option>
            </select>
          </Field>
          {other && (
            <Field label="Outra espécie">
              <select
                required
                value={form.especie_id}
                onChange={(e) =>
                  setForm({ ...form, especie_id: e.target.value })
                }
              >
                <option value="">Selecione a espécie</option>
                {outrasEspecies.map((especie) => (
                  <option key={especie.id} value={especie.id}>
                    {especie.nome}
                  </option>
                ))}
              </select>
            </Field>
          )}
          <Field label="Raça (opcional)">
            <input
              value={form.raca}
              onChange={(e) => setForm({ ...form, raca: e.target.value })}
            />
          </Field>
        </div>
        <FormActions editing={id} busy={busy} onClear={limparFormulario} />
      </form>
      <h3>Pets cadastrados</h3>
      <Table
        headers={["ID", "Nome", "Dono", "Espécie", "Raça", "Ações"]}
        empty={!data.pets.length}
      >
        {data.pets.map((pet) => (
          <tr key={pet.id}>
            <td>{pet.id}</td>
            <td>{pet.nome}</td>
            <td>
              {data.donos.find((dono) => dono.id === pet.dono_id)?.nome ||
                `#${pet.dono_id}`}
            </td>
            <td>
              {data.especies.find((especie) => especie.id === pet.especie_id)
                ?.nome || `#${pet.especie_id}`}
            </td>
            <td>{pet.raca || "Não informada"}</td>
            <td className="actions">
              <button disabled={busy} onClick={() => iniciarEdicao(pet)}>
                Editar
              </button>
              <ConfirmAction
                label="Excluir"
                description={`Excluir ${pet.nome}? Pets com reservas não podem ser excluídos.`}
                busy={busy}
                onConfirm={() => excluirPet(pet)}
              />
            </td>
          </tr>
        ))}
      </Table>
    </section>
  );
}
