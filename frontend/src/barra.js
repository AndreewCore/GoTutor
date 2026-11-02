/** Barra superior: navegación, subida de archivos y menú de perfil. */
import * as G from './datos/guardados.js';
import {usuarioActual} from './auth.js';
import {ui} from './estado.js';
import {$, esc, plural} from './util.js';

const GOOGLE = `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#4285F4" d="M22.6 12.3c0-.8-.1-1.5-.2-2.3H12v4.3h6a5.1 5.1 0 0 1-2.2 3.4v2.8h3.6c2.1-2 3.2-4.8 3.2-8.2z"/><path fill="#34A853" d="M12 23c3 0 5.5-1 7.4-2.7l-3.6-2.8c-1 .7-2.3 1.1-3.8 1.1-2.9 0-5.4-2-6.3-4.6H2v2.9A11 11 0 0 0 12 23z"/><path fill="#FBBC05" d="M5.7 14c-.2-.7-.4-1.3-.4-2s.1-1.4.4-2V7.1H2a11 11 0 0 0 0 9.8L5.7 14z"/><path fill="#EA4335" d="M12 5.4c1.6 0 3.1.6 4.2 1.7l3.2-3.2A11 11 0 0 0 2 7.1L5.7 10C6.6 7.4 9.1 5.4 12 5.4z"/></svg>`;

/** Contenido del menú de perfil según haya sesión de Google o no. */
function menuPerfil(u) {
  const n = G.todos().length;
  const who = `<div class="who"><span class="avatar">${esc(u.initials)}</span><div><b>${esc(u.name)}</b>${u.email ? `<small>${esc(u.email)}</small>` : ''}<small>${esc(u.course)}${u.group ? `, ${esc(u.group)}` : ''}</small></div></div>`;
  if (u.invitado) {
    return `${who}
      <div class="stat"><b>${plural(n, 'programa guardado', 'programas guardados')}</b></div>
      <p class="note">Sin sesión, tus programas se guardan solo en este navegador.</p>
      <button role="menuitem" class="gbtn" data-act="login">${GOOGLE}Iniciar sesión con Google</button>`;
  }
  return `${who}
    <div class="stat"><b>${plural(n, 'programa guardado', 'programas guardados')}</b> en tu cuenta</div>
    <button role="menuitem" data-act="ni">Mi progreso</button>
    <button role="menuitem" data-act="ni">Ajustes</button>
    <div class="sep"></div>
    <button role="menuitem" data-act="logout">Cerrar sesión</button>`;
}

/** Dibuja la barra superior completa. */
export function renderBar() {
  const u = usuarioActual();
  const navView = ui.view === 'guardado' ? 'guardados' : ui.view;
  const link = (id, label, extra = '') => `<a href="#${id}" ${navView === id ? 'aria-current="page"' : ''}>${label}${extra}</a>`;
  $('#appbar').innerHTML = `
    <a class="brand" href="#libre"><span class="logo" aria-hidden="true">Go</span><span class="bn">GoTutor</span></a>
    <nav class="nav" aria-label="Secciones">
      ${link('ejemplos', 'Ejemplos')}
      ${link('libre', 'Análisis libre')}
      ${link('guardados', 'Guardados', `<span class="count">${G.todos().length}</span>`)}
    </nav>
    <div class="bar-end">
    <button class="btn upbtn" data-act="upload" title="Subir archivos .go">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 16V4"/><path d="m6 10 6-6 6 6"/><path d="M4 20h16"/></svg><span class="ul">Subir archivos</span></button>
    <div class="profile">
      <button class="pbtn" data-act="menu" aria-expanded="${ui.menu}" aria-haspopup="menu"><span class="avatar">${esc(u.initials)}</span><span class="pn">${esc(u.name)}</span><span class="car">▾</span></button>
      ${ui.menu ? `<div class="pmenu" role="menu">${menuPerfil(u)}</div>` : ''}
    </div>
    </div>`;
}
