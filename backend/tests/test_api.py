"""Pruebas de la integración (API + orquestación), independientes del analizador del grupo.

Ejecutar desde backend/:  python -m unittest
"""

import unittest
from unittest import mock

import servicio
from analizador.modelos import ErrorAnalisis, Nodo, Simbolo, Token
from app import app

CODIGO = 'package main\n\nfunc main() {\n}\n'


def _lex_ok(codigo):
    """Lexer falso que siempre reconoce un token."""
    return [Token("PACKAGE", "package", 1, 1)], []


def _syn_ok(codigo):
    """Parser falso que devuelve un árbol mínimo."""
    return Nodo("Program", "", 1, [Nodo("PackageClause", "main", 1)]), []


class PruebasServicio(unittest.TestCase):
    def analizar(self):
        """Analiza sin escribir logs para no ensuciar backend/logs."""
        return servicio.analizar(CODIGO, "main.go", escribir_logs=False)

    def test_plantillas_sin_implementar(self):
        r = self.analizar()
        self.assertEqual(r["fases"]["lex"]["estado"], "no_impl")
        self.assertEqual(r["fases"]["syn"]["estado"], "pendiente")
        self.assertIsNone(r["tokens"])

    def test_error_lexico_detiene_las_demas_fases(self):
        err = ErrorAnalisis("lex", 1, 5, "Carácter no reconocido: '@'.")
        with mock.patch.object(servicio, "analizar_lexico", return_value=([], [err])):
            r = self.analizar()
        self.assertEqual(r["fases"]["lex"]["estado"], "error")
        self.assertEqual(r["fases"]["lex"]["errores"][0]["columna"], 5)
        self.assertEqual(r["fases"]["syn"]["estado"], "pendiente")

    def test_tres_fases_ok(self):
        simbolos = [Simbolo("main", "func()", "Función", "global", 3)]
        with mock.patch.object(servicio, "analizar_lexico", _lex_ok), \
             mock.patch.object(servicio, "analizar_sintactico", _syn_ok), \
             mock.patch.object(servicio, "analizar_semantico", return_value=(simbolos, [])):
            r = self.analizar()
        self.assertEqual([r["fases"][f]["estado"] for f in servicio.FASES], ["ok", "ok", "ok"])
        self.assertEqual(r["ast"]["hijos"][0]["dato"], "main")
        self.assertEqual(r["simbolos"][0]["nombre"], "main")

    def test_excepcion_del_grupo_se_reporta_como_fallo(self):
        with mock.patch.object(servicio, "analizar_lexico", _lex_ok), \
             mock.patch.object(servicio, "analizar_sintactico", side_effect=KeyError("x")), \
             mock.patch("traceback.print_exc"):
            r = self.analizar()
        self.assertEqual(r["fases"]["syn"]["estado"], "fallo")
        self.assertIn("sintactico.py", r["fases"]["syn"]["errores"][0]["mensaje"])


class PruebasApi(unittest.TestCase):
    def setUp(self):
        self.cliente = app.test_client()

    def test_salud(self):
        self.assertTrue(self.cliente.get("/api/salud").json["ok"])

    def test_falta_codigo(self):
        self.assertEqual(self.cliente.post("/api/analizar", json={}).status_code, 400)

    def test_analizar(self):
        with mock.patch.object(servicio, "analizar", return_value={"ok": 1}) as m:
            r = self.cliente.post("/api/analizar", json={"codigo": "a\r\nb", "archivo": "x.go"})
        self.assertEqual(r.status_code, 200)
        m.assert_called_once_with("a\nb", "x.go")


if __name__ == "__main__":
    unittest.main()
