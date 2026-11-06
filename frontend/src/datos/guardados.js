/**
 * Programas guardados del usuario.
 *
 * Las vistas leen una copia en memoria de forma síncrona (como el prototipo) y
 * cada cambio se escribe en el almacén en segundo plano. Así, conectar
 * Firestore solo requiere cambiar `almacen` en usarAlmacen(), no las vistas.
 */
import * as almacenLocal from './almacen-local.js';
import {toast} from '../interfaz.js';

let almacen = almacenLocal;
let uid = null;
let lista = [];

/** Cambia el almacén (local o Firestore) y recarga la lista. */
export async function usarAlmacen(nuevo, nuevoUid = null) {
  almacen = nuevo;
  uid = nuevoUid;
  await cargar();
}

/** Carga los programas desde el almacén actual. */
export async function cargar() {
  try {
    lista = await almacen.listar(uid);
  } catch (err) {
    lista = [];
    avisar(err);
  }
}

/** Muestra en un toast el fallo de escritura sin bloquear la interfaz. */
const avisar = err => { console.error(err); toast(`No se pudo sincronizar: ${err.message}`); };

/** Todos los programas (copia en memoria). */
export const todos = () => lista;

/** Busca un programa por id. */
export const buscar = id => lista.find(s => s.id === id);

/** Agrega un programa nuevo. */
export function crear(prog) {
  lista.push(prog);
  almacen.guardar(prog, uid).catch(avisar);
}

/** Aplica `cambios` a un programa existente y lo persiste. */
export function actualizar(id, cambios) {
  const prog = buscar(id);
  if (!prog) return;
  Object.assign(prog, cambios);
  almacen.guardar(prog, uid).catch(avisar);
}

/** Elimina un programa. */
export function eliminar(id) {
  lista = lista.filter(s => s.id !== id);
  almacen.eliminar(id, uid).catch(avisar);
}
