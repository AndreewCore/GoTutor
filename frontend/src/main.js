/** Punto de entrada: carga estilos, guardados y arranca el router. */
import './estilos.css';
import './acciones.js';
import * as G from './datos/guardados.js';
import {route} from './router.js';

await G.cargar();
window.addEventListener('hashchange', route);
route();
