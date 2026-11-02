/** Vista Análisis libre: editor + salida de la fase + tutor. */
import * as api from '../api.js';
import * as G from '../datos/guardados.js';
import {PHASES} from '../datos/tutor.js';
import {errorsHTML, fileSelHTML, panel, salidaFase, statusText, stepClass, todosLosErrores, tutorHTML} from '../componentes.js';
import {activeFile, currentExample, isMulti, persistDraft, resultadoVigente, st, ui} from '../estado.js';
import {toast} from '../interfaz.js';
import {gutterHTML, highlight, linesHTML} from '../resaltado.js';
import {$, esc} from '../util.js';

/** Estado del pill junto a Guardar. */
function saveLabel() {
  if (st.draft.savedId && !st.draft.dirty) return ['ok', 'Guardado'];
  if (currentExample()) return ['info', 'Ejemplo sin cambios'];
  return ['warn', 'Sin guardar'];
}

function stepperHTML(data) {
  return PHASES.map((p, i) => `<li><button class="step ${stepClass(data, p.id)}" data-step="${p.id}" ${p.id === ui.step ? 'aria-current="step"' : ''}>
    <span class="num">${i + 1}</span><span class="sn">${p.name}</span><span class="ss">${statusText(data, p.id)}</span></button></li>`).join('');
}

/** Lo que se muestra en la salida cuando no hay un resultado vigente. */
function vacio() {
  if (st.analizando) return `<div class="empty"><span class="spin"></span><b>Analizando…</b>El servidor está ejecutando las fases.</div>`;
  if (st.resultado) return `<div class="empty ni"><b>Cambiaste el código</b>Pulsa <b>Analizar</b> otra vez para ver el resultado actualizado.</div>`;
  return `<div class="empty ni"><b>Aún no hay resultados</b>Pulsa <b>Analizar</b> para enviar ${esc(activeFile().name)} al analizador de Go (PLY).</div>`;
}

function outHTML(data) {
  const {title, body, sub} = salidaFase(data, ui.step, activeFile().code, vacio());
  return panel(title, body, sub || (data ? '' : 'tu código'));
}

function tutorPanelHTML(data) {
  const idx = PHASES.findIndex(p => p.id === ui.step);
  const prev = PHASES[idx - 1], next = PHASES[idx + 1];
  const errs = data ? errorsHTML(data, ui.step) : '';
  return `<div class="ph"><h2 class="pt">Qué pasa en esta fase</h2></div>
    <div class="pb">${tutorHTML(data, ui.step)}${errs ? `<h3 class="sec-title">Errores de la fase</h3>${errs}` : ''}</div>
    <div class="navrow">
      ${prev ? `<button class="btn sm" data-step="${prev.id}">Volver a ${prev.name.toLowerCase()}</button>` : '<span></span>'}
      ${next ? `<button class="btn sm" data-step="${next.id}">Seguir con ${next.name.toLowerCase()}</button>` : ''}
    </div>`;
}

// Si los paneles muestran un resultado; al editar se compara para redibujar solo cuando cambia.
let mostrandoResultado = false;

const analyzeBtn = () => st.analizando
  ? '<span class="spin"></span>Analizando…'
  : 'Analizar';

/** HTML de la vista. */
export function viewLibre() {
  const data = resultadoVigente();
  const e = currentExample();
  const s = st.draft.savedId && G.buscar(st.draft.savedId);
  const src = s ? s.name : e ? e.name : 'Borrador';
  return `<div class="libre">
    <ol class="stepper" id="stepper">${stepperHTML(data)}</ol>
    <div class="l2-body">
      <section class="panel ed-panel" id="edpanel">
        <div class="drop" aria-hidden="true">Suelta tus archivos .go aquí</div>
        <div class="ph">
          <div id="flabel">${fileSelHTML(st.draft.files, st.draft.active, 'ed')}</div><span class="sub" style="margin-left:0" id="srcname">${esc(src)}</span>
          <div class="ed-actions"><span class="pill" id="savepill"></span>
            <button class="btn sm" data-act="save">Guardar</button>
            <button class="btn primary sm" data-act="analyze" id="analyzebtn" ${st.analizando ? 'disabled' : ''}>${analyzeBtn()}</button></div>
        </div>
        <div class="ed-scroll ed" id="edscroll"><div class="ed-inner">
          <div class="gutter" id="gutter"></div>
          <div class="ed-code"><div class="hlayer" id="hlayer"></div>
            <textarea class="ta" id="ta" spellcheck="false" autocapitalize="off" autocomplete="off" wrap="off" aria-label="Código de ${esc(activeFile().name)}"></textarea></div>
        </div></div>
        <div class="sbar"><span id="caret">Ln 1, Col 1</span>${isMulti() ? `<span>${st.draft.files.length} archivos · se analiza el activo</span>` : ''}<span>Go</span><span>UTF-8</span><span>Analizador: PLY (Python)</span></div>
      </section>
      <div class="l2-out" id="out">${outHTML(data)}</div>
      <section class="panel" id="tutorp">${tutorPanelHTML(data)}</section>
    </div>
  </div>`;
}

/** Actualiza coloreado, números de línea e indicador sin tocar el textarea (conserva el foco). */
export function refreshEditor() {
  const {lines, errLines} = highlight(activeFile().code, todosLosErrores(resultadoVigente()));
  $('#hlayer').innerHTML = linesHTML(lines);
  $('#gutter').innerHTML = gutterHTML(lines.length, errLines);
  const [cls, txt] = saveLabel();
  const pill = $('#savepill');
  pill.className = `pill ${cls}`;
  pill.innerHTML = `<i></i>${txt}`;
}

/** Vuelve a dibujar stepper, salida, tutor y el botón Analizar. */
export function refreshResults() {
  const data = resultadoVigente();
  mostrandoResultado = !!data;
  $('#stepper').innerHTML = stepperHTML(data);
  $('#out').innerHTML = outHTML(data);
  $('#tutorp').innerHTML = tutorPanelHTML(data);
  const btn = $('#analyzebtn');
  btn.disabled = st.analizando;
  btn.innerHTML = analyzeBtn();
}

/** Conecta el textarea con el estado del borrador. */
export function bindEditor() {
  const ta = $('#ta');
  ta.value = activeFile().code;
  mostrandoResultado = !!resultadoVigente();
  const onChange = () => {
    activeFile().code = ta.value;
    st.draft.dirty = true;
    persistDraft();
    refreshEditor();
    // Solo redibuja los paneles cuando el resultado deja de corresponder al código
    // (o vuelve a corresponder tras deshacer), no en cada tecla.
    if (!!resultadoVigente() !== mostrandoResultado) refreshResults();
    updateCaret();
  };
  const updateCaret = () => {
    const before = ta.value.slice(0, ta.selectionStart);
    const ln = before.split('\n').length, col = before.length - before.lastIndexOf('\n');
    $('#caret').textContent = `Ln ${ln}, Col ${col}`;
  };
  ta.addEventListener('input', onChange);
  ta.addEventListener('keyup', updateCaret);
  ta.addEventListener('click', updateCaret);
  ta.addEventListener('keydown', ev => {
    if (ev.key === 'Tab' && !ev.shiftKey) {
      ev.preventDefault();
      ta.setRangeText('\t', ta.selectionStart, ta.selectionEnd, 'end');
      onChange();
    }
  });
  refreshEditor();
}

/** Envía el archivo activo al analizador y muestra el resultado. */
export async function ejecutarAnalisis() {
  if (st.analizando) return;
  const {name:archivo, code:codigo} = activeFile();
  st.analizando = true;
  if (ui.view === 'libre' && $('#stepper')) refreshResults();
  try {
    const data = await api.analizar(codigo, archivo);
    st.resultado = {archivo, codigo, data};
  } catch (err) {
    toast(err.message);
  } finally {
    st.analizando = false;
    if (ui.view === 'libre' && $('#stepper')) { refreshResults(); refreshEditor(); }
  }
}
