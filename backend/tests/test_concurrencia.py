"""Dos análisis a la vez no deben mezclar el estado global de los analizadores."""

import threading
import time
import unittest
from unittest import mock

import servicio
from analizador.modelos import ErrorAnalisis, Token

# Imita a un analizador del grupo que, como sintactico.py, junta sus errores en
# una lista del módulo y la reinicia al empezar.
_errores_globales = []


def _lexico_con_estado_global(codigo):
    """Lexer falso que reporta un error con su propio código y tarda un poco."""
    _errores_globales.clear()
    _errores_globales.append(ErrorAnalisis("lex", 1, 1, codigo))
    time.sleep(0.05)  # deja que el otro hilo entre si no hubiera candado
    return [Token("ID", codigo, 1, 1)], list(_errores_globales)


class PruebasConcurrencia(unittest.TestCase):
    def test_peticiones_simultaneas_no_se_mezclan(self):
        resultados = {}

        def trabajo(codigo):
            """Analiza `codigo` y guarda los mensajes de error que recibió."""
            r = servicio.analizar(codigo, escribir_logs=False)
            resultados[codigo] = [e["mensaje"] for e in r["fases"]["lex"]["errores"]]

        with mock.patch.object(servicio, "analizar_lexico", _lexico_con_estado_global):
            hilos = [threading.Thread(target=trabajo, args=(c,)) for c in ("A", "B", "C", "D")]
            for h in hilos:
                h.start()
            for h in hilos:
                h.join(timeout=5)

        self.assertEqual(resultados, {c: [c] for c in ("A", "B", "C", "D")})

    def test_una_excepcion_libera_el_candado(self):
        with mock.patch.object(servicio, "analizar_lexico", side_effect=RuntimeError("x")), \
             mock.patch("traceback.print_exc"):
            servicio.analizar("x", escribir_logs=False)
        self.assertFalse(servicio._candado.locked())


if __name__ == "__main__":
    unittest.main()
