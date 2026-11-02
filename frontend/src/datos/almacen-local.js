/**
 * Almacén de programas guardados en este navegador (modo invitado).
 *
 * Implementa la misma interfaz que almacen-firestore.js; guardados.js elige uno.
 * Todas las funciones son async para que ambos almacenes sean intercambiables.
 */
import * as local from './local.js';
import {semilla} from './semilla.js';

const KEY = 'gotutor.saved';

/** Convierte datos del formato de un solo archivo ({code}) al de varios ({files}). */
const toFiles = o => o.files ? o : (({code, ...rest}) => ({...rest, files:[{name:'main.go', code}]}))(o);

/** Lee la lista completa; la primera vez la llena con los programas de muestra. */
function leer() {
  const v = local.get(KEY, null);
  return Array.isArray(v) ? v.map(toFiles) : semilla();
}

/** Devuelve todos los programas guardados. */
export async function listar() {
  const lista = leer();
  local.set(KEY, lista);
  return lista;
}

/** Crea o reemplaza un programa por su id. */
export async function guardar(prog) {
  const lista = leer();
  const i = lista.findIndex(s => s.id === prog.id);
  if (i >= 0) lista[i] = prog; else lista.push(prog);
  local.set(KEY, lista);
}

/** Elimina un programa por id. */
export async function eliminar(id) {
  local.set(KEY, leer().filter(s => s.id !== id));
}
