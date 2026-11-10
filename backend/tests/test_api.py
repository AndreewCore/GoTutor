"""Pruebas de la integración (API + orquestación), independientes del analizador del grupo.

Ejecutar desde backend/:  python -m unittest
"""

import unittest
from unittest import mock

import servicio
from analizador.modelos import ErrorAnalisis, Nodo, Simbolo, Token
from app import MAX_CODIGO, app

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

    def test_lexico_real_reconoce_el_programa(self):
        """El léxico del grupo (avance 1) tokeniza un programa válido sin errores."""
        r = self.analizar()
        self.assertEqual(r["fases"]["lex"]["estado"], "ok")
        self.assertEqual(r["tokens"][0]["tipo"], "PACKAGE")

    def test_fase_sin_implementar_detiene_las_demas(self):
        """Una fase que lanza NotImplementedError sale como no_impl y deja pendientes las siguientes."""
        # Se simula con mock porque el léxico real ya está implementado y
        # el mecanismo debe seguir probado aunque las fases avancen.
        with mock.patch.object(servicio, "analizar_lexico", side_effect=NotImplementedError):
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

    def test_retorno_de_carro_suelto(self):
        # Los editores del Mac clásico guardan solo \r; también rompería las líneas de PLY.
        with mock.patch.object(servicio, "analizar", return_value={}) as m:
            self.cliente.post("/api/analizar", json={"codigo": "a\rb\r\nc"})
        m.assert_called_once_with("a\nb\nc", "main.go")

    def test_cuerpo_que_no_es_json(self):
        r = self.cliente.post("/api/analizar", data="codigo=x", content_type="text/plain")
        self.assertEqual(r.status_code, 400)

    def test_codigo_que_no_es_texto(self):
        self.assertEqual(self.cliente.post("/api/analizar", json={"codigo": 5}).status_code, 400)

    def test_codigo_demasiado_grande(self):
        with mock.patch.object(servicio, "analizar") as m:
            r = self.cliente.post("/api/analizar", json={"codigo": "x" * (MAX_CODIGO + 1)})
        self.assertEqual(r.status_code, 413)
        m.assert_not_called()

    def test_codigo_en_el_limite(self):
        with mock.patch.object(servicio, "analizar", return_value={}):
            r = self.cliente.post("/api/analizar", json={"codigo": "x" * MAX_CODIGO})
        self.assertEqual(r.status_code, 200)

    def test_nombre_de_archivo_recortado(self):
        with mock.patch.object(servicio, "analizar", return_value={}) as m:
            self.cliente.post("/api/analizar", json={"codigo": "", "archivo": "a" * 500})
        self.assertEqual(len(m.call_args.args[1]), 120)


if __name__ == "__main__":
    unittest.main()
