/** Modal y avisos flotantes (toast), compartidos por todas las vistas. */
import {$, esc} from './util.js';

let modalActions = {};

/** Acción del botón `i` del modal abierto (la usa el manejador global de clics). */
export const modalAction = i => modalActions[i];

/** Abre un modal con botones; `actions` = [{label, cls, submit, run}]. */
export function openModal({title, body, actions}) {
  modalActions = {};
  const btns = actions.map((a, i) => { modalActions[i] = a.run; return `<button class="btn ${a.cls || ''}" data-modal="${i}" ${a.submit ? 'type="submit"' : 'type="button"'}>${a.label}</button>`; }).join('');
  $('#overlay').innerHTML = `<div class="scrim" data-act="modal-close"><form class="modal" role="dialog" aria-modal="true" aria-label="${esc(title)}" data-form="modal">
    <h2>${esc(title)}</h2>${body}<div class="acts">${btns}</div></form></div>`;
  const f = $('#overlay input') || $('#overlay .btn:last-child');
  f.focus();
  if (f.select) f.select();
}

/** Cierra el modal abierto. */
export const closeModal = () => { $('#overlay').innerHTML = ''; };

let toastTimer;

/** Muestra un aviso breve; `tag` es una etiqueta opcional a la izquierda. */
export function toast(msg, tag) {
  const el = document.createElement('div');
  el.className = 'toast';
  el.setAttribute('role', 'status');
  el.innerHTML = `${tag ? `<span class="tag">${tag}</span>` : ''}${esc(msg)}`;
  document.querySelectorAll('.toast').forEach(n => n.remove());
  document.body.appendChild(el);
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.remove(), 2800);
}

/** Aviso estándar para lo que todavía no está conectado. */
export const notImplToast = () => toast('Función no implementada', 'Pendiente');
