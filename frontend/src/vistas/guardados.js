/** Vista Guardados: lista de programas del usuario. */
import * as G from '../datos/guardados.js';
import {usuarioActual} from '../auth.js';
import {codeView} from '../resaltado.js';
import {esc, fmtDate, lineCount, mainFile, plural} from '../util.js';

/** Fragmento de 5 líneas desde la primera func, para no repetir la cabecera package/import. */
function snipRange(code) {
  const i = code.split('\n').findIndex(l => l.startsWith('func'));
  const from = i >= 0 ? i + 1 : 1;
  return {from, to:from + 4};
}

/** HTML de la vista. */
export function viewGuardados() {
  const list = [...G.todos()].sort((a, b) => b.updated - a.updated);
  const rows = list.map(s => {
    const f = mainFile(s.files);
    const size = s.files.length > 1 ? plural(s.files.length, 'archivo', 'archivos') : plural(lineCount(f.code), 'línea', 'líneas');
    return `<article class="srow">
      <div><h2>${esc(s.name)}</h2><div class="meta"><span>Actualizado ${fmtDate(s.updated)}</span><span>${size}</span>${s.notes ? '<span class="pill warn"><i></i>Con notas</span>' : ''}</div></div>
      <div class="snip">${codeView(f.code, snipRange(f.code))}</div>
      <div class="acts"><a class="btn primary sm" href="#guardado/${s.id}">Abrir</a></div>
    </article>`;
  }).join('');
  const donde = usuarioActual().invitado ? 'en este navegador' : 'en tu cuenta';
  return `<div class="page">
    <div class="intro"><div><h1>Guardados</h1><p>Tus programas guardados ${donde} desde Análisis libre. Ábrelos para verlos fase por fase y tomar notas.</p></div></div>
    ${list.length ? `<div class="saved-list">${rows}</div>`
      : `<div class="card blank"><h2>Aún no tienes programas guardados</h2><p>Escribe tu código en Análisis libre y pulsa Guardar.</p><a class="btn primary sm" href="#libre">Ir a Análisis libre</a></div>`}
  </div>`;
}
