/** Router por hash: #ejemplos, #libre, #guardados, #guardado/<id>. */
import {renderBar} from './barra.js';
import {ui} from './estado.js';
import {$} from './util.js';
import {viewEjemplos} from './vistas/ejemplos.js';
import {analizarNb, bindNotes, viewCuaderno} from './vistas/cuaderno.js';
import {viewGuardados} from './vistas/guardados.js';
import {bindEditor, viewLibre} from './vistas/libre.js';

const TITULOS = {ejemplos:'Ejemplos', libre:'Análisis libre', guardados:'Guardados', guardado:'Cuaderno'};

/** Dibuja la vista que indica el hash actual. */
export function route() {
  const [view, param] = location.hash.slice(1).split('/');
  const next = view in TITULOS ? view : 'libre';
  if (next !== ui.view || (param || null) !== ui.param) { ui.renaming = false; ui.nbFile = 0; }
  ui.view = next; ui.param = param || null; ui.menu = false; ui.fsel = null;
  const html = {ejemplos:viewEjemplos, libre:viewLibre, guardados:viewGuardados, guardado:() => viewCuaderno(ui.param)}[ui.view]();
  $('#view').innerHTML = html;
  $('#view').scrollTop = 0;
  renderBar();
  if (ui.view === 'libre') bindEditor();
  if (ui.view === 'guardado') { bindNotes(); analizarNb(); }
  document.title = `${TITULOS[ui.view]} — GoTutor`;
}
