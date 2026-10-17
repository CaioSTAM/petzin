import React, { useRef, useState } from "react";
import { api } from "./api";
import {
  ConfirmAction,
  Field,
  FormActions,
  Table,
  date,
  money,
} from "./components";

const empty = {
  dono_id: "",
  canil_id: "",
  data_entrada: "",
  data_saida: "",
  pet_ids: [],
};

export default function Reservas({ data, execute, busy }) {
  const [form, setForm] = useState(empty);
  const [id, setId] = useState(null);
  const [availability, setAvailability] = useState(null);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState("");
  const requestVersion = useRef(0);
  const firstField = useRef(null);
  const pets = data.pets.filter((pet) => pet.dono_id === Number(form.dono_id));
  function alterarFormulario(values) {
    requestVersion.current += 1;
    setForm((formularioAtual) => ({ ...formularioAtual, ...values }));
    setAvailability(null);
    setError("");
    setChecking(false);
  }
  function limparFormulario() {
    alterarFormulario(empty);
    setId(null);
  }
  function validarDatas() {
    if (
      !form.data_entrada ||
      !form.data_saida ||
      form.data_saida < form.data_entrada
    ) {
      setError("Informe a entrada e uma saída igual ou posterior à entrada.");
      return false;
    }
    return true;
  }
  async function consultarDisponibilidade() {
    if (!validarDatas()) return;
    const version = ++requestVersion.current;
    setChecking(true);
    setError("");
    setAvailability(null);
    try {
      const canisDisponiveis = await api(
        `canis/disponiveis?${new URLSearchParams({ data_entrada: form.data_entrada, data_saida: form.data_saida })}`,
      );
      if (version === requestVersion.current) setAvailability(canisDisponiveis);
    } catch (err) {
      if (version === requestVersion.current) setError(err.message);
    } finally {
      if (version === requestVersion.current) setChecking(false);
    }
  }
  async function salvarReserva(event) {
    event.preventDefault();
    setError("");
    if (!validarDatas()) return;
    if (!form.pet_ids.length) {
      setError("Selecione pelo menos um pet.");
      return;
    }
    const dadosReserva = {
      canil_id: Number(form.canil_id),
      data_entrada: form.data_entrada,
      data_saida: form.data_saida,
      pet_ids: form.pet_ids,
    };
    if (
      await execute(
        `reservas${id ? `/${id}` : ""}`,
        id ? "PUT" : "POST",
        dadosReserva,
        "Reserva salva.",
        setError,
      )
    )
      limparFormulario();
  }
  function iniciarEdicao(reserva) {
    const primeiroPet = data.pets.find((pet) => pet.id === reserva.pet_ids[0]);
    setId(reserva.id);
    alterarFormulario({
      dono_id: String(primeiroPet?.dono_id || ""),
      canil_id: String(reserva.canil_id),
      data_entrada: reserva.data_entrada,
      data_saida: reserva.data_saida,
      pet_ids: [...reserva.pet_ids],
    });
    firstField.current.focus();
  }
  function selecionarPet(petId, selecionado) {
    const petIds = selecionado
      ? [...form.pet_ids, petId]
      : form.pet_ids.filter((idSelecionado) => idSelecionado !== petId);
    alterarFormulario({ pet_ids: petIds });
  }
  async function cancelarReserva(reserva) {
    const cancelada = await execute(
      `reservas/${reserva.id}`,
      "DELETE",
      null,
      "Reserva cancelada.",
    );
    if (cancelada && id === reserva.id) limparFormulario();
    return cancelada;
  }
  return (
    <section>
      <h2>Reservas</h2>
      <p>
        Uma reserva por canil. Até dois cachorros do mesmo dono podem
        compartilhar; outros animais ficam sozinhos.
      </p>
      <p>
        Entrada e saída contam como diárias. Exemplo: dias 20 a 22 = 3 diárias.
        A tarifa aplicada aparece na reserva.
      </p>
      <h3>{id ? `Editar reserva #${id}` : "Cadastrar reserva"}</h3>
      <form onSubmit={salvarReserva}>
        <div className="fields">
          <Field label="Dono dos pets">
            <select
              ref={firstField}
              required
              value={form.dono_id}
              onChange={(e) =>
                alterarFormulario({ dono_id: e.target.value, pet_ids: [] })
              }
            >
              <option value="">Selecione</option>
              {data.donos.map((dono) => (
                <option key={dono.id} value={dono.id}>
                  {dono.nome} (#{dono.id})
                </option>
              ))}
            </select>
          </Field>
          <Field label="Entrada">
            <input
              type="date"
              required
              value={form.data_entrada}
              onChange={(e) =>
                alterarFormulario({ data_entrada: e.target.value })
              }
            />
          </Field>
          <Field label="Saída">
            <input
              type="date"
              required
              min={form.data_entrada || undefined}
              value={form.data_saida}
              onChange={(e) =>
                alterarFormulario({ data_saida: e.target.value })
              }
            />
          </Field>
          <Field label="Canil">
            <select
              required
              value={form.canil_id}
              onChange={(e) => alterarFormulario({ canil_id: e.target.value })}
            >
              <option value="">Selecione</option>
              {data.canis.map((canil) => (
                <option key={canil.id} value={canil.id}>
                  Canil {canil.id}
                </option>
              ))}
            </select>
          </Field>
        </div>
        <fieldset>
          <legend>Pets da reserva (até dois)</legend>
          {!form.dono_id ? (
            <p>Selecione um dono.</p>
          ) : !pets.length ? (
            <p>Esse dono ainda não tem pets cadastrados.</p>
          ) : (
            pets.map((pet) => (
              <label className="checkbox" key={pet.id}>
                <input
                  type="checkbox"
                  checked={form.pet_ids.includes(pet.id)}
                  disabled={
                    !form.pet_ids.includes(pet.id) && form.pet_ids.length === 2
                  }
                  onChange={(e) => selecionarPet(pet.id, e.target.checked)}
                />
                {pet.nome} (#{pet.id}) —{" "}
                {
                  data.especies.find((especie) => especie.id === pet.especie_id)
                    ?.nome
                }
              </label>
            ))
          )}
        </fieldset>
        <button
          type="button"
          disabled={busy || checking}
          onClick={consultarDisponibilidade}
        >
          {checking ? "Consultando…" : "Consultar disponibilidade"}
        </button>
        {availability !== null && (
          <p role="status">
            {availability.length
              ? `Canis livres: ${availability.map((canil) => canil.id).join(", ")}.`
              : "Nenhum canil livre nesse período."}{" "}
            A vaga será validada ao salvar.
            {id
              ? " A reserva atual também ocupa seu canil nesta consulta."
              : ""}
          </p>
        )}
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        <FormActions editing={id} busy={busy} onClear={limparFormulario} />
      </form>
      <h3>Reservas cadastradas</h3>
      <Table
        headers={[
          "ID",
          "Canil",
          "Pets",
          "Entrada",
          "Saída",
          "Diárias",
          "Tarifa",
          "Total",
          "Situação",
          "Ações",
        ]}
        empty={!data.reservas.length}
      >
        {data.reservas.map((reserva) => (
          <tr key={reserva.id}>
            <td>{reserva.id}</td>
            <td>{reserva.canil_id}</td>
            <td>
              {reserva.pet_ids
                .map(
                  (petId) =>
                    data.pets.find((pet) => pet.id === petId)?.nome ||
                    `#${petId}`,
                )
                .join(", ")}
            </td>
            <td>{date(reserva.data_entrada)}</td>
            <td>{date(reserva.data_saida)}</td>
            <td>{reserva.diarias}</td>
            <td>{money(reserva.tarifa_diaria)}</td>
            <td>{money(reserva.valor_total)}</td>
            <td>{reserva.status === "ativa" ? "Ativa" : "Cancelada"}</td>
            <td>
              {reserva.status === "ativa" && (
                <div className="actions">
                  <button
                    disabled={busy}
                    onClick={() => iniciarEdicao(reserva)}
                  >
                    Editar
                  </button>
                  <ConfirmAction
                    label="Cancelar reserva"
                    description={`Cancelar a reserva #${reserva.id}? O canil será liberado e o histórico será mantido.`}
                    busy={busy}
                    onConfirm={() => cancelarReserva(reserva)}
                  />
                </div>
              )}
            </td>
          </tr>
        ))}
      </Table>
    </section>
  );
}
