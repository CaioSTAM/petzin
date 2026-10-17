import React, { useId, useState } from 'react';

export function Field({ label, children }) {
  const id = useId();
  return <div className="field"><label htmlFor={id}>{label}</label>{React.cloneElement(children, { id })}</div>;
}

export function FormActions({ editing, busy, onClear }) {
  return <div className="actions">
    <button type="submit" disabled={busy}>{busy ? 'Salvando…' : editing ? 'Salvar alterações' : 'Cadastrar'}</button>
    <button type="button" disabled={busy} onClick={onClear}>{editing ? 'Cancelar edição' : 'Limpar'}</button>
  </div>;
}

export function ConfirmAction({ label, description, busy, onConfirm }) {
  const [confirming, setConfirming] = useState(false);
  if (!confirming) return <button type="button" disabled={busy} onClick={() => setConfirming(true)}>{label}</button>;
  return <span className="confirmation">
    <span>{description}</span>
    <button type="button" disabled={busy} onClick={async () => {
      if (await onConfirm()) setConfirming(false);
    }}>Confirmar {label.toLowerCase()}</button>
    <button type="button" disabled={busy} onClick={() => setConfirming(false)}>Voltar</button>
  </span>;
}

export function Table({ headers, children, empty }) {
  return <div className="table-scroll"><table>
    <thead><tr>{headers.map((header) => <th key={header} scope="col">{header}</th>)}</tr></thead>
    <tbody>{empty ? <tr><td colSpan={headers.length}>Nenhum registro cadastrado.</td></tr> : children}</tbody>
  </table></div>;
}

export const money = (value) => Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
export const date = (value) => value.split('-').reverse().join('/');
