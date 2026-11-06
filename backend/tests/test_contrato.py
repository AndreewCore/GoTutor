"""Contrato JSON entre el backend y la interfaz, y cálculo de columnas.

Si una de estas pruebas falla, el frontend dejará de mostrar algo: revisen
frontend/src/componentes.js antes de cambiar un campo de modelos.py.
"""

import unittest
from unittest import mock

import servicio
from analizador.modelos import ErrorAnalisis, Nodo, Simbolo, Token, a_dict, columna

CAMPOS_TOKEN = {"tipo", "valor", "linea", "columna"}
CAMPOS_ERROR = {"fase", "linea", "columna", "mensaje", "sugerencia"}
CAMPOS_NODO = {"tipo", "dato", "linea", "hijos", "error"}
CAMPOS_SIMBOLO = {"nombre", "tipo", "categoria", "ambito", "linea", "usos", "error"}
CAMPOS_RESPUESTA = {"archivo", "fases", "tokens", "ast", "simbolos", "logs"}
ESTADOS = {"ok", "error", "pendiente", "no_impl", "fallo"}


def _arbol():
    """Árbol de dos niveles para revisar la serialización recursiva."""
    return Nodo("Program", "", 1, [Nodo("FuncDecl", "main", 3, [Nodo("Block", "", 3)])])


def _respuesta_completa(semantico):
    """Corre el servicio con léxico y sintáctico falsos y el semántico dado."""
    with mock.patch.object(servicio, "analizar_lexico",
                           return_value=([Token("PACKAGE", "package", 1, 1)], [])), \
         mock.patch.object(servicio, "analizar_sintactico", return_value=(_arbol(), [])), \
         mock.patch.object(servicio, "analizar_semantico", semantico):
        return servicio.analizar("package main\n", "main.go", escribir_logs=False)


class PruebasCampos(unittest.TestCase):
    def test_token(self):
        self.assertEqual(set(a_dict(Token("ID", "x", 1, 1))), CAMPOS_TOKEN)

    def test_error(self):
        self.assertEqual(set(a_dict(ErrorAnalisis("lex", 1, 1, "m"))), CAMPOS_ERROR)

    def test_simbolo(self):
        self.assertEqual(set(a_dict(Simbolo("x", "int", "Variable", "main", 1))), CAMPOS_SIMBOLO)

    def test_nodo_anidado(self):
        d = a_dict(_arbol())
        self.assertEqual(set(d), CAMPOS_NODO)
        nieto = d["hijos"][0]["hijos"][0]
        self.assertEqual(set(nieto), CAMPOS_NODO)
        self.assertEqual(nieto["hijos"], [])


class PruebasRespuesta(unittest.TestCase):
    def test_forma_de_la_respuesta(self):
        r = _respuesta_completa(lambda ast, codigo: ([Simbolo("main", "func()", "Función", "global", 3)], []))
        self.assertEqual(set(r), CAMPOS_RESPUESTA)
        self.assertEqual(list(r["fases"]), list(servicio.FASES))
        for fase in r["fases"].values():
            self.assertEqual(set(fase), {"estado", "errores"})
            self.assertIn(fase["estado"], ESTADOS)
        self.assertEqual(set(r["tokens"][0]), CAMPOS_TOKEN)
        self.assertEqual(set(r["simbolos"][0]), CAMPOS_SIMBOLO)

    def test_errores_serializados(self):
        r = _respuesta_completa(lambda ast, codigo: ([], [ErrorAnalisis("sem", 2, 3, "m", "s")]))
        self.assertEqual(r["fases"]["sem"]["estado"], "error")
        self.assertEqual(set(r["fases"]["sem"]["errores"][0]), CAMPOS_ERROR)

    def test_marcas_del_semantico_llegan_al_arbol(self):
        def semantico(ast, codigo):
            """Marca un nodo como lo haría el grupo al encontrar un error."""
            ast.hijos[0].error = "sem"
            return [], [ErrorAnalisis("sem", 3, 1, "m")]

        r = _respuesta_completa(semantico)
        self.assertEqual(r["ast"]["hijos"][0]["error"], "sem")
        self.assertIsNone(r["ast"]["error"])


class PruebasColumna(unittest.TestCase):
    def test_primera_linea(self):
        self.assertEqual(columna("abc", 0), 1)
        self.assertEqual(columna("abc", 2), 3)

    def test_despues_de_un_salto(self):
        self.assertEqual(columna("ab\ncd", 3), 1)
        self.assertEqual(columna("ab\ncd", 4), 2)

    def test_tabulador_cuenta_uno(self):
        # Igual que el compilador de Go y que el resaltador de la interfaz.
        self.assertEqual(columna("\tx := 1", 1), 2)

    def test_acentos_cuentan_uno(self):
        codigo = 'á := "ñ" @'
        self.assertEqual(columna(codigo, codigo.index("@")), 10)

    def test_emoji_cuenta_como_en_javascript(self):
        # "😀".length === 2 en JS, así que el editor ubica el '@' en la columna 11.
        codigo = 's := "😀" @'
        self.assertEqual(columna(codigo, codigo.index("@")), 11)


if __name__ == "__main__":
    unittest.main()
