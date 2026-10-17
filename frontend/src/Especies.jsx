import React, { useState } from "react";
import { Field, Table } from "./components";

export default function Especies({ data, execute, busy }) {
  const [nome, setNome] = useState("");
  const [error, setError] = useState("");
  async function salvarEspecie(event) {
    event.preventDefault();
    setError("");
    if (
      await execute(
        "especies",
        "POST",
        { nome },
        "Espécie cadastrada.",
        setError,
      )
    )
      setNome("");
  }
  return (
    <section>
      <h2>Espécies</h2>
      <p>
        Confira a lista antes de cadastrar para evitar nomes diferentes para a
        mesma espécie.
      </p>
      <form onSubmit={salvarEspecie}>
        <Field label="Nome da espécie">
          <input
            required
            value={nome}
            onChange={(e) => setNome(e.target.value)}
          />
        </Field>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        <button disabled={busy}>
          {busy ? "Salvando…" : "Cadastrar espécie"}
        </button>
      </form>
      <h3>Espécies cadastradas</h3>
      <Table headers={["ID", "Nome"]} empty={!data.especies.length}>
        {data.especies.map((especie) => (
          <tr key={especie.id}>
            <td>{especie.id}</td>
            <td>{especie.nome}</td>
          </tr>
        ))}
      </Table>
    </section>
  );
}
