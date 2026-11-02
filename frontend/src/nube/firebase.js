/**
 * Conexión con Firebase (Auth con Google + Firestore).
 *
 * ESQUELETO: lee la config de .env.local pero todavía no inicializa nada.
 * Para conectarlo:
 *   1. pnpm add firebase
 *   2. Crear el proyecto en la consola de Firebase, activar Authentication →
 *      Google y Cloud Firestore (plan Spark, gratis).
 *   3. Copiar .env.example a .env.local y completar las variables.
 *   4. Implementar las funciones de abajo con initializeApp, getAuth,
 *      GoogleAuthProvider, signInWithPopup, signOut y onAuthStateChanged.
 */

const config = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

/** Indica si hay credenciales en el entorno (si no, se usa el modo invitado). */
export const firebaseConfigurado = () => Object.values(config).every(Boolean);

/** Abre el popup de Google y devuelve el usuario de Firebase. */
export async function iniciarSesionGoogle() {
  throw new Error('Inicio de sesión con Google aún no implementado (nube/firebase.js)');
}

/** Cierra la sesión de Firebase. */
export async function cerrarSesionGoogle() {
  throw new Error('Cierre de sesión aún no implementado (nube/firebase.js)');
}

/**
 * Llama a `cb(usuario | null)` cada vez que cambia la sesión.
 * Devuelve una función para dejar de escuchar.
 */
export function observarSesion(cb) {
  cb(null);
  return () => {};
}
