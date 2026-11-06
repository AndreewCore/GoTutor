/** Estado de la interfaz y del borrador de Análisis libre. */
import * as local from './datos/local.js';
import {STARTER, findExample} from './datos/ejemplos.js';

const DRAFT_KEY = 'gotutor.draft';

/** Proyecto inicial de un solo archivo. */
export const starterFiles = () => [{name:'main.go', code:STARTER}];

/** Borrador vacío con la plantilla mínima de Go. */
const nuevoDraft = () => ({files:starterFiles(), active:0, exampleId:null, savedId:null, dirty:false});

/** Lee el borrador guardado; descarta los de versiones anteriores que no traían files. */
function leerDraft() {
  const d = local.get(DRAFT_KEY, null);
  if (!d || !Array.isArray(d.files) || !d.files.length) return nuevoDraft();
  // El prototipo guardaba el ejemplo por índice; ahora es por id.
  if (typeof d.exampleId !== 'string') d.exampleId = null;
  d.active = Math.min(d.active || 0, d.files.length - 1);
  return d;
}

/**
 * Estado mutable compartido. Se agrupa en un objeto porque `draft` se reemplaza
 * entero y los módulos importados no pueden reasignar un `let` exportado.
 *
 * resultado:  respuesta de /api/analizar para el archivo activo, junto con el
 *             código que se analizó (si el código cambió, ya no es válida).
 * nb:         lo mismo para el archivo abierto en el Cuaderno.
 */
export const st = {
  draft: leerDraft(),
  resultado: null,
  analizando: false,
  nb: null
};

// fsel: qué desplegable de archivos está abierto ('ed' en el editor, 'nb' en el Cuaderno o null).
export const ui = {view:'libre', param:null, step:'lex', menu:false, renaming:false, fsel:null, nbFile:0};

/** Persiste el borrador en este navegador (no va a la nube: es el área de trabajo). */
export const persistDraft = () => local.set(DRAFT_KEY, st.draft);

/** Reemplaza el borrador entero. */
export function setDraft(next) {
  st.draft = {dirty:false, exampleId:null, savedId:null, active:0, ...next};
  st.resultado = null;
  persistDraft();
}

export const activeFile = () => st.draft.files[st.draft.active];
export const isMulti = () => st.draft.files.length > 1;

/** El ejemplo cargado en el borrador, solo si es el único archivo y no se ha modificado. */
export function currentExample() {
  const ex = findExample(st.draft.exampleId);
  return ex && st.draft.files.length === 1 && st.draft.files[0].code === ex.code ? ex : null;
}

/** Resultado del análisis si corresponde al código actual del archivo activo. */
export function resultadoVigente() {
  const r = st.resultado, f = activeFile();
  return r && r.archivo === f.name && r.codigo === f.code ? r.data : null;
}
