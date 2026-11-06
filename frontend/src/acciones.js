/** Manejadores globales: clics, formularios, teclado, subida de archivos y resaltado al pasar el cursor. */
import * as G from './datos/guardados.js';
import * as almacenFirestore from './datos/almacen-firestore.js';
import * as almacenLocal from './datos/almacen-local.js';
import {cerrarSesion, iniciarSesion} from './auth.js';
import {renderBar} from './barra.js';
import {findExample} from './datos/ejemplos.js';
import {activeFile, isMulti, persistDraft, setDraft, starterFiles, st, ui} from './estado.js';
import {closeModal, modalAction, notImplToast, openModal, toast} from './interfaz.js';
import {route} from './router.js';
import {fileSelHTML} from './componentes.js';
import {analizarNb, rerenderNb} from './vistas/cuaderno.js';
import {ejecutarAnalisis, refreshEditor, refreshResults} from './vistas/libre.js';
import {$, cloneFiles, esc, fmtDate, lineCount, plural} from './util.js';

const goLibre = () => { if (location.hash === '#libre') route(); else location.hash = '#libre'; };

/** Vuelve a dibujar solo los desplegables de archivos visibles. */
function rerenderFsel() {
  const ed = $('#flabel'), nb = $('#nblabel');
  if (ed) ed.innerHTML = fileSelHTML(st.draft.files, st.draft.active, 'ed');
  if (nb) { const s = G.buscar(ui.param); nb.innerHTML = fileSelHTML(s.files, ui.nbFile, 'nb'); }
}

/**
 * Carga archivos en Análisis libre; pide confirmación si hay cambios sin guardar.
 * Con `analizar`, lanza el análisis apenas se abre (lo usan los ejemplos).
 */
function loadIntoLibre(next, {analizar = false} = {}) {
  const go = () => {
    setDraft(next);
    ui.step = 'lex';
    goLibre();
    if (analizar) ejecutarAnalisis();
  };
  const unsaved = st.draft.dirty && JSON.stringify(st.draft.files) !== JSON.stringify(next.files);
  if (!unsaved) return go();
  openModal({
    title: isMulti() ? 'Reemplazar archivos' : `Reemplazar ${activeFile().name}`,
    body:'<p>Tienes cambios sin guardar en Análisis libre. Si continúas, se reemplazarán por el código nuevo.</p>',
    actions:[
      {label:'Cancelar', cls:'ghost', run:closeModal},
      {label:'Guardar primero', run:() => { closeModal(); openSaveModal(); }},
      {label:'Reemplazar', cls:'danger', run:() => { closeModal(); go(); }}
    ]
  });
}

/** Guarda el proyecto completo. `after` se ejecuta tras guardar (p. ej. continuar un reemplazo). */
function openSaveModal(after) {
  const d = st.draft;
  const existing = d.savedId && G.buscar(d.savedId);
  const ex = findExample(d.exampleId);
  const n = d.files.length;
  const def = existing ? existing.name : ex && !isMulti() ? `${ex.name} (mi versión)` : `${isMulti() ? 'Proyecto' : activeFile().name}, ${fmtDate(Date.now())}`;
  const doSave = asCopy => {
    const name = ($('#save-name').value.trim() || def).slice(0, 80);
    const now = Date.now();
    if (existing && !asCopy) {
      G.actualizar(existing.id, {name, files:cloneFiles(d.files), updated:now});
    } else {
      const s = {id:'s-' + now.toString(36), name, files:cloneFiles(d.files), notes:'', created:now, updated:now};
      G.crear(s);
      d.savedId = s.id;
    }
    d.dirty = false;
    persistDraft();
    closeModal();
    renderBar();
    toast(`Guardado: ${name}`);
    if (after) return after();
    if (ui.view === 'libre') { refreshEditor(); $('#srcname').textContent = name; }
  };
  const what = n > 1 ? `los ${n} archivos del proyecto` : 'el código actual';
  openModal({
    title: existing ? 'Guardar cambios' : n > 1 ? `Guardar proyecto (${n} archivos)` : `Guardar ${activeFile().name}`,
    body:`<p>${existing ? `Se actualizará el programa guardado con ${what}.` : `Se guardará ${what}. Podrás abrirlo luego desde Guardados en formato Cuaderno.`}</p>
      <label for="save-name">Nombre</label><input id="save-name" value="${esc(def)}" maxlength="80">`,
    actions:[
      {label:'Cancelar', cls:'ghost', run:closeModal},
      ...(existing ? [{label:'Guardar como copia', run:() => doSave(true)}] : []),
      {label: existing ? 'Actualizar' : 'Guardar', cls:'primary', submit:true, run:() => doSave(false)}
    ]
  });
}

/* ---------- Subida de archivos ---------- */

/** Punto de entrada común del botón del header y de arrastrar y soltar. */
async function handleUpload(list) {
  const all = [...list];
  const ok = all.filter(f => /\.go$/i.test(f.name));
  const bad = all.filter(f => !ok.includes(f));
  if (bad.length) toast(`No se subió: ${bad.map(f => f.name).join(', ')} (solo archivos .go)`);
  if (!ok.length) return;
  // Si se repite un nombre dentro de la misma subida, gana el último.
  const byName = new Map();
  for (const f of ok) byName.set(f.name, {name:f.name, code:(await f.text()).replace(/\r\n?/g, '\n')});
  const files = [...byName.values()];
  const clashes = files.filter(f => st.draft.files.some(d => d.name === f.name)).map(f => f.name);
  const current = isMulti() ? `los ${st.draft.files.length} archivos actuales` : `el archivo actual (${activeFile().name})`;
  openModal({
    title:`Subir ${plural(files.length, 'archivo', 'archivos')}`,
    body:`<ul class="flist">${files.map(f => `<li><span class="file">${esc(f.name)}</span><span>${plural(lineCount(f.code), 'línea', 'líneas')}</span></li>`).join('')}</ul>
      <p>¿Quieres mantener ${current} y agregar estos, o reemplazarlos?</p>
      ${clashes.length ? `<p class="warnp">${clashes.map(esc).join(', ')} ya ${clashes.length > 1 ? 'existen' : 'existe'}: si mantienes los actuales, se ${clashes.length > 1 ? 'sobrescribirán' : 'sobrescribirá'} con la versión subida.</p>` : ''}`,
    actions:[
      {label:'Cancelar', cls:'ghost', run:closeModal},
      {label:'Reemplazar todo', run:() => { closeModal(); confirmReplace(files); }},
      {label:'Mantener y agregar', cls:'primary', submit:true, run:() => { closeModal(); applyUpload(files, false); }}
    ]
  });
}

/** Antes de reemplazar, ofrece guardar los archivos actuales si tienen cambios. */
function confirmReplace(files) {
  if (!st.draft.dirty) return applyUpload(files, true);
  openModal({
    title:'¿Guardar los archivos actuales?',
    body:`<p>Tienes cambios sin guardar en ${isMulti() ? `${st.draft.files.length} archivos` : activeFile().name}. Si reemplazas sin guardar, se perderán.</p>`,
    actions:[
      {label:'Cancelar', cls:'ghost', run:closeModal},
      {label:'Reemplazar sin guardar', cls:'danger', run:() => { closeModal(); applyUpload(files, true); }},
      {label:'Guardar y reemplazar', cls:'primary', submit:true, run:() => { closeModal(); openSaveModal(() => applyUpload(files, true)); }}
    ]
  });
}

function applyUpload(files, replace) {
  if (replace) {
    setDraft({files, dirty:true});
  } else {
    const d = st.draft;
    files.forEach(f => {
      const i = d.files.findIndex(x => x.name === f.name);
      if (i >= 0) d.files[i] = f; else d.files.push(f);
    });
    d.active = d.files.findIndex(x => x.name === files[0].name);
    d.dirty = true;
    persistDraft();
  }
  ui.fsel = null;
  ui.step = 'lex';
  toast(plural(files.length, 'archivo subido', 'archivos subidos'));
  goLibre();
}

function confirmRemoveFile(i) {
  const f = st.draft.files[i];
  openModal({
    title:'Quitar archivo',
    body:`<p>Se quitará «${esc(f.name)}» de Análisis libre. Si el proyecto está guardado, seguirá ahí hasta que vuelvas a guardar.</p>`,
    actions:[
      {label:'Cancelar', cls:'ghost', run:closeModal},
      {label:'Quitar', cls:'danger', submit:true, run:() => {
        const d = st.draft;
        d.files.splice(i, 1);
        if (d.active > i || d.active >= d.files.length) d.active = Math.max(0, d.active - 1);
        d.dirty = true;
        persistDraft();
        closeModal();
        ui.fsel = null;
        route();
        toast(`Quitado: ${f.name}`);
      }}
    ]
  });
}

function confirmDelete(id) {
  const s = G.buscar(id);
  openModal({
    title:'Eliminar programa',
    body:`<p>Se eliminará «${esc(s.name)}» junto con sus notas. Esta acción no se puede deshacer.</p>`,
    actions:[
      {label:'Cancelar', cls:'ghost', run:closeModal},
      {label:'Eliminar', cls:'danger', submit:true, run:() => {
        G.eliminar(id);
        if (st.draft.savedId === id) { st.draft.savedId = null; st.draft.dirty = true; persistDraft(); }
        closeModal();
        location.hash = '#guardados';
        toast('Eliminado');
      }}
    ]
  });
}

/* ---------- Sesión ---------- */

/** Inicia sesión con Google y pasa a los guardados de la nube. */
async function login() {
  try {
    const u = await iniciarSesion();
    await G.usarAlmacen(almacenFirestore, u.uid);
    toast(`Hola, ${u.name}`);
  } catch (err) {
    toast(err.message, 'Pendiente');
  }
  route();
}

/** Cierra la sesión y vuelve a los guardados locales. */
async function logout() {
  try {
    await cerrarSesion();
    await G.usarAlmacen(almacenLocal);
  } catch (err) {
    toast(err.message, 'Pendiente');
  }
  route();
}

/* ---------- Listeners ---------- */

document.addEventListener('click', ev => {
  const t = ev.target;
  if (ui.menu && !t.closest('.profile')) { ui.menu = false; renderBar(); }
  if (ui.fsel && !t.closest('.fsel')) { ui.fsel = null; rerenderFsel(); }

  const step = t.closest('[data-step]');
  if (step) { ui.step = step.dataset.step; refreshResults(); return; }

  const m = t.closest('[data-modal]');
  if (m && m.type !== 'submit') { modalAction(m.dataset.modal)(); return; }

  const a = t.closest('[data-act]');
  if (!a) return;
  switch (a.dataset.act) {
    case 'menu': ui.menu = !ui.menu; renderBar(); break;
    case 'ni': ui.menu = false; renderBar(); notImplToast(); break;
    case 'login': ui.menu = false; renderBar(); login(); break;
    case 'logout': ui.menu = false; renderBar(); logout(); break;
    case 'analyze': ejecutarAnalisis(); break;
    case 'save': openSaveModal(); break;
    case 'open-ex': { const ex = findExample(a.dataset.id); loadIntoLibre({files:[{name:'main.go', code:ex.code}], exampleId:ex.id}, {analizar:true}); break; }
    case 'open-blank': loadIntoLibre({files:starterFiles()}); break;
    case 'open-saved': { const s = G.buscar(a.dataset.id); loadIntoLibre({files:cloneFiles(s.files), active:ui.nbFile, savedId:s.id}); break; }
    case 'upload': $('#upfile').click(); break;
    case 'ed-menu': case 'nb-menu': {
      const scope = a.dataset.act.slice(0, 2);
      ui.fsel = ui.fsel === scope ? null : scope;
      rerenderFsel();
      const cur = $('.fmenu [aria-selected="true"]');
      if (cur) cur.focus();
      break;
    }
    case 'ed-pick': ui.fsel = null; st.draft.active = +a.dataset.i; persistDraft(); route(); $('#ta').focus(); break;
    case 'nb-pick': ui.fsel = null; ui.nbFile = +a.dataset.i; rerenderNb(); analizarNb(); break;
    case 'ed-remove': confirmRemoveFile(+a.dataset.i); break;
    case 'rename': ui.renaming = true; route(); $('.rename input').select(); break;
    case 'rename-cancel': ui.renaming = false; route(); break;
    case 'delete': confirmDelete(a.dataset.id); break;
    case 'modal-close': if (t === a) closeModal(); break;
  }
});

document.addEventListener('submit', ev => {
  ev.preventDefault();
  const f = ev.target;
  if (f.dataset.form === 'rename') {
    const s = G.buscar(ui.param);
    const name = f.elements.name.value.trim();
    if (s && name) { G.actualizar(s.id, {name:name.slice(0, 80), updated:Date.now()}); toast('Nombre actualizado'); }
    ui.renaming = false;
    route();
  }
  if (f.dataset.form === 'modal') {
    const sub = f.querySelector('[type="submit"]');
    if (sub) modalAction(sub.dataset.modal)();
  }
});

document.addEventListener('keydown', ev => {
  if (ev.key === 'Escape') {
    if ($('#overlay').innerHTML) closeModal();
    else if (ui.fsel) { const scope = ui.fsel; ui.fsel = null; rerenderFsel(); $(`[data-act="${scope}-menu"]`).focus(); }
    else if (ui.menu) { ui.menu = false; renderBar(); }
    else if (ui.renaming) { ui.renaming = false; route(); }
  }
  if ((ev.ctrlKey || ev.metaKey) && ui.view === 'libre') {
    const k = ev.key.toLowerCase();
    if (k === 's') { ev.preventDefault(); openSaveModal(); }
    if (k === 'enter') { ev.preventDefault(); ejecutarAnalisis(); }
  }
});

$('#upfile').addEventListener('change', ev => {
  handleUpload(ev.target.files);
  ev.target.value = '';
});

// Arrastrar y soltar: solo el panel del editor acepta archivos; en el resto se evita
// que el navegador abra el archivo y se indica dónde soltarlo.
const hasFiles = ev => ev.dataTransfer && [...ev.dataTransfer.types].includes('Files');
document.addEventListener('dragover', ev => {
  if (!hasFiles(ev)) return;
  ev.preventDefault();
  const p = ev.target.closest && ev.target.closest('#edpanel');
  ev.dataTransfer.dropEffect = p ? 'copy' : 'none';
  if (p) p.classList.add('dragging');
});
document.addEventListener('dragleave', ev => {
  const p = $('#edpanel');
  if (p && !p.contains(ev.relatedTarget)) p.classList.remove('dragging');
});
document.addEventListener('drop', ev => {
  if (!hasFiles(ev)) return;
  ev.preventDefault();
  const p = ev.target.closest && ev.target.closest('#edpanel');
  if (p) { p.classList.remove('dragging'); handleUpload(ev.dataTransfer.files); }
  else toast(ui.view === 'libre' ? 'Suelta los archivos sobre el editor' : 'Usa el botón Subir archivos o suéltalos en el editor de Análisis libre');
});

// Resalta en el editor el token o la línea del elemento bajo el cursor.
document.addEventListener('mouseover', ev => {
  document.querySelectorAll('.ed .hl, .ed .hl-line').forEach(n => n.classList.remove('hl', 'hl-line'));
  if (ev.target.closest('.ed')) return;
  const tk = ev.target.closest('[data-pos]');
  const ln = !tk && ev.target.closest('[data-line]');
  const el = tk ? $(`#hlayer .tk[data-pos="${tk.dataset.pos}"]`) : ln ? $(`#hlayer .ln[data-ln="${ln.dataset.line}"]`) : null;
  if (!el) return;
  el.classList.add(tk ? 'hl' : 'hl-line');
  revealInEditor(el.closest('.ln'));
});

// Desplaza solo el contenedor del editor; scrollIntoView movería también la página.
function revealInEditor(row) {
  const box = $('#edscroll');
  const top = row.offsetTop;
  if (top < box.scrollTop || top + row.offsetHeight > box.scrollTop + box.clientHeight) {
    box.scrollTop = top - box.clientHeight / 2;
  }
}
