/** Piezas de HTML que comparten Análisis libre y el Cuaderno. */
import {PHASES, TUTOR} from './datos/tutor.js';
import {categoriasPorPosicion} from './resaltado.js';
import {ui} from './estado.js';
import {countNodes, esc, lineCount, plural} from './util.js';

export const MASCOT = `<svg class="mascot" viewBox="0 0 80 90" aria-hidden="true">
  <ellipse cx="40" cy="52" rx="30" ry="34" fill="#7fd3ec"/>
  <ellipse cx="13" cy="24" rx="7" ry="8" fill="#7fd3ec"/><ellipse cx="67" cy="24" rx="7" ry="8" fill="#7fd3ec"/>
  <circle cx="28" cy="38" r="11" fill="#fff" stroke="#1d3a4d" stroke-width="2"/><circle cx="52" cy="38" r="11" fill="#fff" stroke="#1d3a4d" stroke-width="2"/>
  <circle cx="31" cy="39" r="4.5" fill="#1d3a4d"/><circle cx="49" cy="39" r="4.5" fill="#1d3a4d"/>
  <ellipse cx="40" cy="53" rx="6" ry="4" fill="#f2c6a0"/><rect x="36.5" y="56" width="7" height="7" rx="1" fill="#fff" stroke="#1d3a4d" stroke-width="1.2"/>
  <ellipse cx="22" cy="84" rx="7" ry="4" fill="#f2c6a0"/><ellipse cx="58" cy="84" rx="7" ry="4" fill="#f2c6a0"/>
</svg>`;

const ARCHIVO = {lex:'lexico.py', syn:'sintactico.py', sem:'semantico.py'};
const faseNombre = ph => PHASES.find(p => p.id === ph).name.toLowerCase();

/* ---------- Estado de cada fase ---------- */

/** Estado de una fase según la API: ok, error, pendiente, no_impl o fallo. */
export const estadoFase = (data, ph) => data.fases[ph].estado;

/** Errores de una fase. */
export const errsOf = (data, ph) => data.fases[ph].errores;

/** Todos los errores, para marcar el código. */
export const todosLosErrores = data => data ? PHASES.flatMap(p => errsOf(data, p.id)) : [];

/** Clase del paso en el stepper. */
export function stepClass(data, ph) {
  if (!data) return '';
  const e = estadoFase(data, ph);
  return e === 'ok' ? 'ok' : (e === 'error' || e === 'fallo') ? 'error' : '';
}

/** Texto corto bajo el nombre de la fase. */
export function statusText(data, ph) {
  if (!data) return 'Sin analizar';
  const e = estadoFase(data, ph);
  if (e === 'ok') return 'Sin errores';
  if (e === 'pendiente') return 'Pendiente';
  if (e === 'no_impl') return 'No implementado';
  if (e === 'fallo') return 'Fallo del analizador';
  return plural(errsOf(data, ph).length, 'error', 'errores');
}

/* ---------- Salidas de cada fase ---------- */

/** Panel con título, subtítulo opcional y cuerpo desplazable. */
export function panel(title, inner, sub = '') {
  return `<section class="panel"><div class="ph"><h2 class="pt">${title}</h2>${sub ? `<span class="sub">${sub}</span>` : ''}</div><div class="pb">${inner}</div></section>`;
}

/** Estado vacío para la fase cuyo archivo de Python aún no está hecho. */
export function notImpl(ph) {
  return `<div class="empty ni"><span class="pill warn"><i></i>Pendiente</span><b>Función no implementada</b><span>Aquí aparecerá el resultado del análisis ${faseNombre(ph)} cuando se complete <code>backend/analizador/${ARCHIVO[ph]}</code>.</span></div>`;
}

/** El analizador del grupo lanzó una excepción: se muestra para que la depuren. */
function fallo(data, ph) {
  const e = errsOf(data, ph)[0];
  return `<div class="empty ni fail"><span class="pill err"><i></i>Fallo</span><b>El analizador falló</b><span>${esc(e ? e.mensaje : '')}</span><span>${esc(e ? e.sugerencia : '')}</span></div>`;
}

const pendiente = `<div class="empty"><b>Fase pendiente</b>Esta fase se ejecuta cuando las anteriores terminan sin errores.</div>`;

/** Tabla de tokens del analizador; el color sale del resaltado del editor en esa posición. */
function tokensTable(tokens, code) {
  if (!tokens.length) return `<div class="empty"><b>Sin tokens</b>El archivo está vacío o solo tiene comentarios.</div>`;
  const cats = categoriasPorPosicion(code);
  return `<table class="tbl"><thead><tr><th>#</th><th>Token</th><th>Lexema</th><th>Lín.</th><th>Col.</th></tr></thead><tbody>
    ${tokens.map((t, k) => `<tr data-pos="${t.linea}:${t.columna}" data-line="${t.linea}">
      <td class="n">${k + 1}</td><td><span class="ttype c-${cats.get(`${t.linea}:${t.columna}`) || 'op'}">${esc(t.tipo)}</span></td><td class="m">${esc(t.valor)}</td><td class="n">${t.linea}</td><td class="n">${t.columna}</td></tr>`).join('')}
  </tbody></table>`;
}

/** Un nodo del AST: hoja o <details> desplegable. */
function astNode(n) {
  const bad = n.error ? ' bad' : '';
  const head = `<span class="nt">${esc(n.tipo)}</span>${n.dato ? `<span class="nd">${esc(n.dato)}</span>` : ''}<span class="nl">L${n.linea}</span>`;
  if (!n.hijos.length) return `<div class="leaf${bad}" data-line="${n.linea}">${head}</div>`;
  return `<details open class="${bad}"><summary data-line="${n.linea}">${head}</summary>${n.hijos.map(astNode).join('')}</details>`;
}

function astHTML(data) {
  if (!data.ast) return `<div class="empty"><b>El árbol no se pudo construir</b>Corrige los errores sintácticos para que el parser pueda armarlo.</div>`;
  return `<div class="ast">${astNode(data.ast)}</div>`;
}

function symbolsHTML(simbolos) {
  if (!simbolos.length) return `<div class="empty"><b>Tabla de símbolos vacía</b>El programa no declara nombres.</div>`;
  return `<table class="tbl"><thead><tr><th>Nombre</th><th>Tipo</th><th>Categoría</th><th>Ámbito</th><th>Lín.</th><th>Usos</th></tr></thead><tbody>
    ${simbolos.map(s => `<tr data-line="${s.linea}" class="${s.error ? 'bad' : ''}"><td class="m">${esc(s.nombre)}</td><td class="m">${esc(s.tipo)}</td><td>${esc(s.categoria)}</td><td>${esc(s.ambito)}</td><td class="n">${s.linea}</td><td class="n">${s.usos}</td></tr>`).join('')}
  </tbody></table>`;
}

export const TITULO = {lex:'Tokens', syn:'Árbol sintáctico', sem:'Tabla de símbolos'};

/**
 * Título, cuerpo y subtítulo del panel de salida de una fase.
 * `vacio` es lo que se muestra cuando todavía no hay resultado.
 */
export function salidaFase(data, ph, code, vacio) {
  const title = TITULO[ph];
  if (!data) return {title, body:vacio, sub:''};
  const e = estadoFase(data, ph);
  if (e === 'no_impl') return {title, body:notImpl(ph), sub:''};
  if (e === 'pendiente') return {title, body:pendiente, sub:''};
  if (e === 'fallo') return {title, body:fallo(data, ph), sub:''};
  if (ph === 'lex') return {title, body:tokensTable(data.tokens || [], code), sub:plural((data.tokens || []).length, 'token', 'tokens')};
  if (ph === 'syn') return {title, body:astHTML(data), sub:data.ast ? plural(countNodes(data.ast), 'nodo', 'nodos') : ''};
  const sims = data.simbolos || [];
  return {title, body:symbolsHTML(sims), sub:plural(sims.length, 'símbolo', 'símbolos')};
}

/** Lista de errores de una fase (vacía si la fase no aplica). */
export function errorsHTML(data, ph) {
  const e = estadoFase(data, ph);
  if (e === 'no_impl' || e === 'fallo') return '';
  if (e === 'pendiente') return pendiente;
  const list = errsOf(data, ph);
  if (!list.length) return `<div class="empty good"><b>Sin errores en esta fase</b>Todo lo que se revisó aquí es válido.</div>`;
  return `<ul class="errs">${list.map(x => `<li class="err" data-line="${x.linea}">
      <span class="pos">${x.linea}:${x.columna}</span><span class="msg">${esc(x.mensaje)}</span>${x.sugerencia ? `<span class="hint">${esc(x.sugerencia)}</span>` : ''}</li>`).join('')}</ul>`;
}

/* ---------- Tutor ---------- */

/** Explicación de la fase más un comentario sobre lo que pasó en el código analizado. */
export function tutorHTML(data, ph) {
  const T = TUTOR[ph];
  let ctx;
  if (!data) ctx = 'Pulsa Analizar y aquí verás qué encontró esta fase en tu código.';
  else {
    const e = estadoFase(data, ph), errs = errsOf(data, ph);
    ctx = {
      error: () => `En tu código, esta fase encontró ${plural(errs.length, 'error', 'errores')}. El primero está en la línea ${errs[0].linea}.`,
      pendiente: () => 'En tu código, esta fase no se ejecutó porque una fase anterior no terminó bien.',
      no_impl: () => `Esta fase todavía no está implementada en ${ARCHIVO[ph]}.`,
      fallo: () => `El analizador lanzó un error de Python en ${ARCHIVO[ph]}; no es un problema de tu código.`,
      ok: () => 'En tu código, esta fase terminó sin errores.'
    }[e]();
  }
  return `<div class="tutor"><div class="tutor-row">${MASCOT}<div>
    <h3>${T.title}</h3><p>${T.body}</p><p class="ctx">${ctx}</p>
    <p class="cap">${T.cap}</p><pre>${esc(T.ply)}</pre>
  </div></div></div>`;
}

/** Versión corta del tutor para la columna lateral del Cuaderno. */
export const tutorCompact = ph => `<div class="tutor compact"><h3>${TUTOR[ph].title}</h3><p>${TUTOR[ph].short}</p></div>`;

/* ---------- Selector de archivos ---------- */

/**
 * Nombre del archivo: etiqueta simple si hay uno, desplegable si hay varios.
 * scope 'ed' (editor, permite quitar) o 'nb' (Cuaderno, solo lectura).
 */
export function fileSelHTML(files, active, scope) {
  const f = files[active];
  if (files.length < 2) return `<span class="file">${esc(f.name)}</span>`;
  const open = ui.fsel === scope;
  const items = files.map((x, i) => `<li>
      <button type="button" class="fpick" role="option" aria-selected="${i === active}" data-act="${scope}-pick" data-i="${i}">
        <span class="ck">${i === active ? '✓' : ''}</span><span class="nm">${esc(x.name)}</span><span class="lc">${plural(lineCount(x.code), 'línea', 'líneas')}</span></button>
      ${scope === 'ed' ? `<button type="button" class="frm" data-act="ed-remove" data-i="${i}" aria-label="Quitar ${esc(x.name)}" title="Quitar archivo">×</button>` : ''}
    </li>`).join('');
  return `<div class="fsel">
    <button type="button" class="file fbtn" data-act="${scope}-menu" aria-haspopup="listbox" aria-expanded="${open}">${esc(f.name)}<span class="car">▾</span></button>
    ${open ? `<ul class="fmenu" role="listbox" aria-label="Archivos">${items}
      ${scope === 'ed' ? '<li class="hint">Arrastra archivos .go al editor para agregar más.</li>' : ''}</ul>` : ''}
  </div>`;
}
