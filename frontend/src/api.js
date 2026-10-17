export async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(`/api/${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers },
    });
  } catch {
    throw new Error('Não foi possível conectar à API. Confira se ela está em execução.');
  }
  if (response.status === 204) return null;
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    let message = body?.detail;
    if (Array.isArray(message)) {
      message = message.map((error) => {
        const field = error.loc.filter((item) => !['body', 'query'].includes(item)).join('.');
        return `${field || 'Dados'}: ${error.msg.replace(/^Value error, /, '')}`;
      }).join(' ');
    }
    throw new Error(typeof message === 'string' ? message : 'Não foi possível concluir a operação. Tente novamente.');
  }
  return body;
}
