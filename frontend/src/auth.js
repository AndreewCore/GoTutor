/**
 * Sesión del usuario. Sin Firebase conectado, todos usan el perfil invitado
 * y sus programas viven solo en este navegador.
 */
import {cerrarSesionGoogle, firebaseConfigurado, iniciarSesionGoogle} from './nube/firebase.js';

export const INVITADO = {
  uid:null, name:'Invitado', initials:'IN', email:'', course:'Lenguajes de Programación', group:'', invitado:true
};

let usuario = INVITADO;

/** Perfil actual (invitado o cuenta de Google). */
export const usuarioActual = () => usuario;

/** Iniciales para el avatar a partir del nombre completo. */
const iniciales = nombre => nombre.split(/\s+/).filter(Boolean).slice(0, 2).map(p => p[0].toUpperCase()).join('') || '?';

/** Convierte el usuario de Firebase al perfil que muestra la barra superior. */
export function perfilDesdeFirebase(u) {
  return {
    uid:u.uid, name:u.displayName || u.email, initials:iniciales(u.displayName || u.email || ''),
    email:u.email || '', course:'Lenguajes de Programación', group:'', invitado:false
  };
}

/** Inicia sesión con Google. Lanza un error si Firebase no está configurado o conectado. */
export async function iniciarSesion() {
  if (!firebaseConfigurado()) throw new Error('Falta configurar Firebase en .env.local');
  usuario = perfilDesdeFirebase(await iniciarSesionGoogle());
  return usuario;
}

/** Cierra la sesión y vuelve al perfil invitado. */
export async function cerrarSesion() {
  await cerrarSesionGoogle();
  usuario = INVITADO;
}
