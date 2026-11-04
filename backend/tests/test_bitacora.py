"""Logs por fase en backend/logs (bitacora.py)."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

import bitacora
from analizador.modelos import ErrorAnalisis, Token

AHORA = datetime(2026, 11, 2, 14, 5, 30)


def _fases(lex="ok", syn="pendiente", sem="pendiente", errores_lex=()):
    """Estados de fase con la forma que arma servicio.analizar."""
    return {"lex": {"estado": lex, "errores": list(errores_lex)},
            "syn": {"estado": syn, "errores": []},
            "sem": {"estado": sem, "errores": []}}


class PruebasBitacora(unittest.TestCase):
    def setUp(self):
        """Redirige los logs a una carpeta temporal con fecha y usuario fijos."""
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        self.carpeta = Path(carpeta.name)
        reloj = mock.Mock(wraps=datetime)
        reloj.now.return_value = AHORA
        for objetivo, valor in [("CARPETA", self.carpeta), ("datetime", reloj)]:
            parche = mock.patch.object(bitacora, objetivo, valor)
            parche.start()
            self.addCleanup(parche.stop)
        parche = mock.patch.object(bitacora, "usuario_git", return_value="prueba")
        parche.start()
        self.addCleanup(parche.stop)

    def leer(self, ruta):
        """Contenido de un log a partir de la ruta que devuelve escribir()."""
        return (self.carpeta / Path(ruta).name).read_text(encoding="utf-8")

    def test_nombre_del_archivo(self):
        rutas = bitacora.escribir("main.go", _fases(), [Token("ID", "x", 1, 1)], None, None)
        self.assertEqual(rutas, ["logs/lexico-prueba-02-11-2026-14h05.txt"])

    def test_solo_fases_ejecutadas(self):
        rutas = bitacora.escribir("main.go", _fases(lex="no_impl"), None, None, None)
        self.assertEqual(rutas, [])

    def test_mismo_minuto_no_sobrescribe(self):
        error = ErrorAnalisis("lex", 2, 3, "Carácter no reconocido: '@'.")
        primera = bitacora.escribir("a.go", _fases(), [Token("ID", "x", 1, 1)], None, None)
        segunda = bitacora.escribir("b.go", _fases(lex="error", errores_lex=[error]), [], None, None)
        self.assertEqual(primera, segunda)
        texto = self.leer(primera[0])
        self.assertIn("GoTutor — a.go", texto)
        self.assertIn("GoTutor — b.go", texto)
        self.assertLess(texto.index("a.go"), texto.index(bitacora.SEPARADOR), "el orden es cronológico")
        self.assertLess(texto.index(bitacora.SEPARADOR), texto.index("b.go"))
        self.assertIn("[2:3] Carácter no reconocido: '@'.", texto)

    def test_primer_analisis_sin_separador(self):
        rutas = bitacora.escribir("main.go", _fases(), [], None, None)
        self.assertNotIn(bitacora.SEPARADOR, self.leer(rutas[0]))


if __name__ == "__main__":
    unittest.main()
