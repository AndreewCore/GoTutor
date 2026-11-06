/**
 * localStorage con respaldo en memoria: en modo privado o con el almacenamiento
 * lleno, la app sigue funcionando durante la sesión aunque no persista.
 */
const mem = {};

/** Lee y parsea una clave; devuelve `fallback` si no existe. */
export function get(k, fallback) {
  try {
    const v = localStorage.getItem(k);
    return v ? JSON.parse(v) : (k in mem ? mem[k] : fallback);
  } catch { return k in mem ? mem[k] : fallback; }
}

/** Guarda un valor serializable. */
export function set(k, v) {
  mem[k] = v;
  try { localStorage.setItem(k, JSON.stringify(v)); } catch {}
}
