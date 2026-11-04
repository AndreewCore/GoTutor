/**
 * Almacén de programas en Cloud Firestore, uno por usuario de Google.
 *
 * ESQUELETO: aún no está conectado. Misma interfaz que almacen-local.js.
 *
 * Estructura prevista:
 *   usuarios/{uid}/guardados/{id} = {name, files:[{name, code}], notes, created, updated}
 *
 * Reglas de seguridad previstas (Firestore → Reglas):
 *   match /usuarios/{uid}/guardados/{id} {
 *     allow read, write: if request.auth != null && request.auth.uid == uid;
 *   }
 *
 * Para implementarlo: `pnpm add firebase`, y usar getFirestore(app()) de
 * ../nube/firebase.js con collection/getDocs/setDoc/deleteDoc.
 */

const NO_IMPL = 'Firestore aún no está conectado (almacen-firestore.js)';

/** Devuelve los programas del usuario `uid`. */
export async function listar(uid) {
  throw new Error(NO_IMPL);
}

/** Crea o reemplaza un programa del usuario `uid`. */
export async function guardar(prog, uid) {
  throw new Error(NO_IMPL);
}

/** Elimina un programa del usuario `uid`. */
export async function eliminar(id, uid) {
  throw new Error(NO_IMPL);
}
