/** Vista Cuaderno: un programa guardado, fase por fase, con notas del alumno. */
import * as api from '../api.js';
import * as G from '../datos/guardados.js';
import {errorsHTML, fileSelHTML, panel, salidaFase, todosLosErrores, tutorCompact} from '../componentes.js';
import {st, ui} from '../estado.js';
import {codeView} from '../resaltado.js';
import {$, esc, fmtDate, lineCount, plural} from '../util.js';

const TITULO_NB = {lex:'Tokens', syn:'Árbol sintáctico', sem:'Tabla de símbolos y errores'};

/** Archivo del guardado que se está mostrando. */
const archivoNb = s => s.files[ui.nbFile];

/** Clave que identifica qué se analizó; si el archivo cambia, el resultado ya no sirve. */
const claveNb = s => `${s.id}\u0000${archivoNb(s).name}\u0000${archivoNb(s).code}`;

/** Resultado vigente del Cuaderno para el guardado `s`, o null. */
const nbVigente = s => st.nb && st.nb.clave === claveNb(s) ? st.nb : null;

/** Panel de una fase en el Cuaderno: salida + errores de esa fase. */
function celdaFase(s, ph) {
  const nb = nbVigente(s);
  const code = archivoNb(s).code;
  let vacio = `<div class="empty"><span class="spin"></span><b>Analizando…</b></div>`;
  if (nb && nb.error) vacio = `<div class="empty ni fail"><b>No se pudo analizar</b>${esc(nb.error)}</div>`;
  const data = nb && nb.data;
  const {body, sub} = salidaFase(data, ph, code, vacio);
  const errs = data ? errorsHTML(data, ph) : '';
  return panel(TITULO_NB[ph], body + (errs && data.fases[ph].estado !== 'pendiente' ? `<h3 class="sec-title">Errores</h3>${errs}` : ''), sub);
}

/** HTML de la vista. */
export function viewCuaderno(id) {
  const s = G.buscar(id);
  if (!s) {
    return `<div class="page"><div class="card blank"><h2>Este guardado ya no existe</h2><p>Puede que lo hayas eliminado.</p><a class="btn sm" href="#guardados">Volver a Guardados</a></div></div>`;
  }
  ui.nbFile = Math.min(ui.nbFile, s.files.length - 1);
  const file = archivoNb(s);
  const nb = nbVigente(s);
  const cell = (n, label, main, note, cls = '') => `<div class="cell ${cls}"><div class="cn">[${n}]<small>${label}</small></div>${main}<aside class="note">${note}</aside></div>`;
  const title = ui.renaming
    ? `<form class="rename" data-form="rename"><input name="name" value="${esc(s.name)}" aria-label="Nuevo nombre" required maxlength="80"><button class="btn primary sm">Guardar nombre</button><button type="button" class="btn ghost sm" data-act="rename-cancel">Cancelar</button></form>`
    : `<h1>${esc(s.name)}</h1>`;
  return `<div class="page">
    <div class="crumb"><a href="#guardados">Guardados</a> / ${esc(s.name)}</div>
    <div class="nb-head">
      <div>${title}<div class="meta">Creado ${fmtDate(s.created)}, actualizado ${fmtDate(s.updated)}</div></div>
      <div class="acts">
        <button class="btn primary sm" data-act="open-saved" data-id="${s.id}">Abrir en Análisis libre</button>
        ${ui.renaming ? '' : '<button class="btn sm" data-act="rename">Renombrar</button>'}
        <button class="btn sm" data-act="delete" data-id="${s.id}">Eliminar</button>
      </div>
    </div>
    <div class="cells">
      ${cell(1, 'código', `<section class="panel ed-panel nb-code"><div class="ph"><div id="nblabel">${fileSelHTML(s.files, ui.nbFile, 'nb')}</div><span class="sub">Solo lectura, ${plural(lineCount(file.code), 'línea', 'líneas')}${s.files.length > 1 ? `, ${s.files.length} archivos` : ''}</span></div>${codeView(file.code, {errors:todosLosErrores(nb && nb.data)})}</section>`,
        `<div class="tutor compact"><h3>Tu programa</h3><p>${s.files.length > 1 ? `Este proyecto tiene ${s.files.length} archivos; elige cuál ver en la lista del nombre.` : 'Este es el código tal como lo guardaste.'} Para cambiarlo, ábrelo en Análisis libre.</p></div>`, 'code-cell')}
      ${cell(2, 'léxico', `<div id="nb-lex">${celdaFase(s, 'lex')}</div>`, tutorCompact('lex'))}
      ${cell(3, 'sintáctico', `<div id="nb-syn">${celdaFase(s, 'syn')}</div>`, tutorCompact('syn'))}
      ${cell(4, 'semántico', `<div id="nb-sem">${celdaFase(s, 'sem')}</div>`, tutorCompact('sem'))}
      ${cell(5, 'notas', `<section class="panel"><div class="ph"><h2 class="pt">Mis notas</h2><span class="sub" id="notestate">${s.notes ? 'Guardadas' : ''}</span></div>
          <textarea class="notes" id="notes" data-id="${s.id}" placeholder="Escribe lo que aprendiste o lo que quieres preguntar en clase…">${esc(s.notes || '')}</textarea></section>`,
        `<div class="tutor compact"><h3>Notas del alumno</h3><p>Se guardan solas mientras escribes y solo las ves tú.</p></div>`)}
    </div>
  </div>`;
}

/** Redibuja el código y las tres celdas de fases sin tocar las notas ni el scroll. */
export function rerenderNb() {
  const s = G.buscar(ui.param);
  if (!s || ui.view !== 'guardado') return;
  const file = archivoNb(s);
  const nb = nbVigente(s);
  const code = $('.nb-code');
  code.querySelector('#nblabel').innerHTML = fileSelHTML(s.files, ui.nbFile, 'nb');
  code.querySelector('.sub').textContent = `Solo lectura, ${plural(lineCount(file.code), 'línea', 'líneas')}${s.files.length > 1 ? `, ${s.files.length} archivos` : ''}`;
  code.querySelector('.ed-scroll').outerHTML = codeView(file.code, {errors:todosLosErrores(nb && nb.data)});
  for (const ph of ['lex', 'syn', 'sem']) $(`#nb-${ph}`).innerHTML = celdaFase(s, ph);
}

/** Analiza el archivo mostrado en el Cuaderno (si no está ya analizado). */
export async function analizarNb() {
  const s = G.buscar(ui.param);
  if (!s || nbVigente(s)) return;
  const clave = claveNb(s);
  const {name, code} = archivoNb(s);
  st.nb = {clave, cargando:true};
  try {
    st.nb = {clave, data:await api.analizar(code, name)};
  } catch (err) {
    st.nb = {clave, error:err.message};
  }
  // Si el alumno cambió de archivo o de vista mientras tanto, no pisamos lo nuevo.
  const actual = G.buscar(ui.param);
  if (ui.view === 'guardado' && actual && claveNb(actual) === clave) rerenderNb();
}

/** Guarda las notas medio segundo después de dejar de escribir. */
export function bindNotes() {
  const ta = $('#notes');
  if (!ta) return;
  let t;
  ta.addEventListener('input', () => {
    $('#notestate').textContent = 'Guardando…';
    clearTimeout(t);
    t = setTimeout(() => {
      if (!G.buscar(ta.dataset.id)) return;
      G.actualizar(ta.dataset.id, {notes:ta.value});
      $('#notestate').textContent = 'Guardadas';
    }, 500);
  });
}
