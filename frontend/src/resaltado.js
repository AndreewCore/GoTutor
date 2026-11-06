/**
 * Coloreado de sintaxis del editor.
 *
 * Este tokenizador es SOLO visual: corre en cada tecla y no reemplaza al
 * analizador léxico del grupo (que es el que llena la tabla de tokens).
 */
import {esc} from './util.js';

const KW = new Set(['package','import','func','var','const','return','if','else','for','range','type','struct','break','continue']);
const TYPES = new Set(['int','string','bool','float64','byte','rune']);
const RULES = [
  ['NL', /^\n/], ['WS', /^[ \t]+/], ['COMMENT', /^\/\/[^\n]*/],
  ['STRING_LIT', /^"[^"\n]*"/], ['BAD_STR', /^"[^"\n]*/],
  ['FLOAT_LIT', /^\d+\.\d+/], ['INT_LIT', /^\d+/], ['ID', /^[A-Za-z_]\w*/],
  ['OP', /^(:=|\+\+|--|==|!=|<=|>=|&&|\|\||[+\-*\/%<>=!.,;:(){}\[\]])/], ['ILLEGAL', /^[^\n]/]
];

/** Divide el código en piezas con línea y columna (1-based). */
export function lex(src) {
  const out = [];
  let i = 0, line = 1, col = 1;
  while (i < src.length) {
    const rest = src.slice(i);
    let type, m;
    for (const [t, re] of RULES) { m = rest.match(re); if (m) { type = t; break; } }
    const v = m[0];
    if (type === 'ID') {
      if (KW.has(v)) type = 'KW';
      else if (TYPES.has(v)) type = 'TYPE';
      else if (v === 'true' || v === 'false') type = 'BOOL_LIT';
    } else if (type === 'BAD_STR') type = 'ILLEGAL';
    out.push({type, v, line, col});
    if (v === '\n') { line++; col = 1; } else col += v.length;
    i += v.length;
  }
  // Un identificador seguido de '(' se colorea como llamada a función.
  out.forEach((t, k) => {
    if (t.type !== 'ID') return;
    let j = k + 1;
    while (out[j] && out[j].type === 'WS') j++;
    if (out[j] && out[j].v === '(') t.fn = true;
  });
  return out;
}

/** Categoría visual de una pieza (para color y etiqueta). */
export function cat(t) {
  if (t.type === 'ILLEGAL') return 'err';
  if (t.type === 'COMMENT') return 'cm';
  if (t.type === 'TYPE') return 'type';
  if (t.type === 'STRING_LIT') return 'str';
  if (/_LIT$/.test(t.type)) return 'num';
  if (t.type === 'ID') return t.fn ? 'fn' : 'id';
  if (t.type === 'KW') return 'kw';
  return 'op';
}

/**
 * Mapa "línea:columna" → categoría visual. Sirve para colorear la tabla de
 * tokens del analizador real con los mismos colores que el editor, sin
 * depender de cómo el grupo llame a sus tipos de token.
 */
export function categoriasPorPosicion(code) {
  const m = new Map();
  lex(code).forEach(t => m.set(`${t.line}:${t.col}`, cat(t)));
  return m;
}

/** Colorea código y devuelve líneas HTML más los números de línea con error. */
export function highlight(code, errors = []) {
  const toks = lex(code);
  const bad = new Set();
  // El error se marca en la pieza que contiene la columna, no solo en la que empieza ahí,
  // porque el analizador puede reportar la posición en medio de un lexema.
  errors.forEach(er => {
    const i = toks.findIndex(t => t.line === er.linea && t.col <= er.columna && er.columna < t.col + Math.max(1, t.v.length) && t.type !== 'NL');
    if (i >= 0) bad.add(i);
  });
  const lines = [[]];
  toks.forEach((t, i) => {
    if (t.type === 'NL') { lines.push([]); return; }
    if (t.type === 'WS') { lines[lines.length - 1].push(esc(t.v)); return; }
    lines[lines.length - 1].push(`<span class="tk k-${cat(t)}${bad.has(i) ? ' squig' : ''}" data-pos="${t.line}:${t.col}">${esc(t.v)}</span>`);
  });
  return {lines:lines.map(l => l.join('')), errLines:new Set(errors.map(e => e.linea))};
}

/** Números de línea; los que tienen error llevan un punto rojo. */
export function gutterHTML(n, errLines, from = 1) {
  let g = '';
  for (let i = from; i < from + n; i++) g += `<div class="${errLines.has(i) ? 'is-err' : ''}">${i}</div>`;
  return g;
}

/** Envuelve cada línea coloreada en su fila. */
export function linesHTML(lines, from = 1) {
  return lines.map((l, i) => `<div class="ln" data-ln="${from + i}">${l || ' '}</div>`).join('');
}

/** Vista de código de solo lectura; `from`/`to` recortan un fragmento. */
export function codeView(code, {errors = [], from = 1, to} = {}) {
  const {lines, errLines} = highlight(code.replace(/\n$/, ''), errors);
  const part = lines.slice(from - 1, to);
  return `<div class="ed-scroll ed"><div class="ed-inner">
    <div class="gutter">${gutterHTML(part.length, errLines, from)}</div>
    <div class="ed-code"><div class="hlayer">${linesHTML(part, from)}</div></div>
  </div></div>`;
}
