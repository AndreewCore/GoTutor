/** Utilidades sin estado compartidas por todas las vistas. */

/** querySelector corto. */
export const $ = (s, r = document) => r.querySelector(s);

/** Escapa texto para insertarlo en HTML. */
export const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

/** "1 línea" / "3 líneas". */
export const plural = (n, s, p) => `${n} ${n === 1 ? s : p}`;

/** Número de líneas visibles de un archivo (ignora el salto final). */
export const lineCount = code => code.replace(/\n$/, '').split('\n').length;

/** Fecha corta en español, p. ej. "2 nov, 14:05". */
export const fmtDate = ts => new Intl.DateTimeFormat('es', {day:'numeric', month:'short', hour:'2-digit', minute:'2-digit'}).format(ts);

/** Cuenta los nodos de un AST del analizador. */
export const countNodes = n => n ? 1 + n.hijos.reduce((a, c) => a + countNodes(c), 0) : 0;

/** Copia superficial de la lista de archivos de un proyecto. */
export const cloneFiles = files => files.map(f => ({...f}));

/** Archivo que representa a un proyecto: main.go si existe, si no el primero. */
export const mainFile = files => files.find(f => f.name === 'main.go') || files[0];
