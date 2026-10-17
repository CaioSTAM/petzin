import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { api } from "./api";
import Donos from "./Donos";
import Pets from "./Pets";
import Reservas from "./Reservas";
import Especies from "./Especies";
import "./styles.css";

const screens = { Donos, Pets, Reservas, Espécies: Especies };

function App() {
  const [tab, setTab] = useState("Donos");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(null);

  async function load(signal) {
    const keys = ["donos", "pets", "especies", "canis", "reservas"];
    const values = await Promise.all(keys.map((key) => api(key, { signal })));
    setData(Object.fromEntries(keys.map((key, index) => [key, values[index]])));
  }

  async function refresh(signal) {
    setLoading(true);
    setMessage(null);
    try {
      await load(signal);
    } catch (error) {
      if (!signal?.aborted) setMessage({ error: true, text: error.message });
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    refresh(controller.signal);
    return () => controller.abort();
  }, []);

  async function execute(path, method, body, success, onError) {
    setBusy(true);
    setMessage(null);
    try {
      await api(path, {
        method,
        ...(body !== null ? { body: JSON.stringify(body) } : {}),
      });
      setMessage({ error: false, text: success });
      try {
        await load();
      } catch {
        setMessage({
          error: true,
          text: `${success} A lista não pôde ser atualizada. Clique em Atualizar dados.`,
        });
      }
      return true;
    } catch (error) {
      if (onError) onError(error.message);
      else setMessage({ error: true, text: error.message });
      return false;
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <header>
        <h1>PetzIn</h1>
        <p>Cadastro de donos, pets e reservas de canis.</p>
      </header>
      <nav aria-label="Seções">
        {Object.keys(screens).map((name) => (
          <button
            key={name}
            aria-current={tab === name ? "page" : undefined}
            disabled={busy || loading}
            onClick={() => {
              setTab(name);
              setMessage(null);
            }}
          >
            {name}
          </button>
        ))}
      </nav>
      {message && (
        <p
          className={message.error ? "error" : "success"}
          role={message.error ? "alert" : "status"}
        >
          {message.text}
        </p>
      )}
      <div className="refresh">
        <button disabled={busy || loading} onClick={() => refresh()}>
          {loading ? "Carregando…" : "Atualizar dados"}
        </button>
      </div>
      {data &&
        Object.entries(screens).map(([name, Screen]) => (
          <div key={name} hidden={tab !== name}>
            <Screen data={data} execute={execute} busy={busy || loading} />
          </div>
        ))}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
