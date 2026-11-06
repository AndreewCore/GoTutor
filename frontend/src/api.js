/** Cliente de la API Flask (backend/app.py). */

/**
 * Envía un archivo al analizador y devuelve el resultado de las tres fases.
 * Forma de la respuesta: ver "Contrato de la API" en el README.
 */
export async function analizar(codigo, archivo) {
  let res;
  try {
    res = await fetch('/api/analizar', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({codigo, archivo})
    });
  } catch {
    throw new Error('No se pudo conectar con el analizador. ¿Está corriendo el servidor Flask?');
  }
  // Un 502/504 del proxy de Vite llega sin JSON cuando Flask está apagado.
  const data = await res.json().catch(() => null);
  if (!res.ok || !data) {
    throw new Error(data?.error || 'No se pudo conectar con el analizador. ¿Está corriendo el servidor Flask?');
  }
  return data;
}
