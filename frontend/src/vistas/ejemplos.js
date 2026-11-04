/** Vista Ejemplos: programas cortos agrupados por dificultad. */
import {EXAMPLES, LEVELS} from '../datos/ejemplos.js';
import {MASCOT} from '../componentes.js';
import {codeView} from '../resaltado.js';
import {esc, lineCount, plural} from '../util.js';

const LABEL = {lex:'Errores léxicos', syn:'Errores sintácticos', sem:'Errores semánticos'};

/** Tarjeta con un fragmento alrededor de la línea que el ejemplo enseña. */
function card(ex) {
  const from = Math.max(1, ex.linea - 3), to = Math.min(lineCount(ex.code), ex.linea + 1);
  return `<article class="card">
    <div class="card-h"><span class="pill err"><i></i>${LABEL[ex.fase]}</span><h2>${esc(ex.name)}</h2><p>${esc(ex.challenge)}</p></div>
    <div class="snip">${codeView(ex.code, {from, to})}</div>
    <div class="card-f"><span class="meta">${plural(lineCount(ex.code), 'línea', 'líneas')}</span><button class="btn primary sm" data-act="open-ex" data-id="${ex.id}">Abrir en Análisis libre</button></div>
  </article>`;
}

/** HTML de la vista. */
export function viewEjemplos() {
  const sections = LEVELS.map((lv, n) => {
    const items = EXAMPLES.filter(ex => ex.level === lv.id);
    return `<section class="level">
      <div class="level-h"><span class="lvl lvl-${n + 1}" aria-hidden="true"><i></i><i></i><i></i></span><h2>${lv.name}</h2><p>${lv.desc}</p><span class="count">${items.length}</span></div>
      <div class="grid">${items.map(card).join('')}</div>
    </section>`;
  }).join('');
  return `<div class="page">
    <div class="intro">${MASCOT}<div><h1>Ejemplos</h1><p>Programas cortos ordenados por dificultad. Ábrelos en Análisis libre para recorrer las fases, modificarlos y guardar tu versión.</p></div>
      <aside class="card blank start"><h2>Empezar desde cero</h2><p>Abre un main.go con la estructura mínima de un programa Go.</p><button class="btn primary sm" data-act="open-blank">Nuevo main.go</button></aside>
    </div>
    ${sections}
  </div>`;
}
