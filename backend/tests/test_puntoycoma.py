"""Inserción automática de ';' (analizador/puntoycoma.py) con un lexer PLY mínimo."""

import unittest
from unittest import mock

import ply.lex as lex
import ply.yacc as yacc

from analizador import lexico
from analizador.modelos import columna
from analizador.puntoycoma import VALOR_IMPLICITO, LexerConPuntoYComa

FIN = {"ID", "INT", "RPAREN", "RBRACE", "RAW", "RETURN", "INCREMENT"}


class _Mini:
    """Lexer de prueba con lo justo para los casos de Go que importan."""

    tokens = ["ID", "INT", "RAW", "RETURN", "INCREMENT", "PLUS", "LPAREN", "RPAREN",
              "LBRACE", "RBRACE", "SEMICOLON"]
    t_INCREMENT = r"\+\+"
    t_PLUS = r"\+"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_SEMICOLON = r";"
    t_INT = r"\d+"
    t_ignore = " \t"

    def t_RAW(self, t):
        r"`[^`]*`"
        t.lexer.lineno += t.value.count("\n")
        return t

    def t_COMENTARIO(self, t):
        r"/\*(.|\n)*?\*/"
        t.lexer.lineno += t.value.count("\n")

    def t_ID(self, t):
        r"[A-Za-z_]\w*"
        t.type = "RETURN" if t.value == "return" else "ID"
        return t

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        t.lexer.skip(1)


def _lexer(fin=FIN):
    """Lexer mínimo envuelto con la inserción de ';'."""
    return LexerConPuntoYComa(lex.lex(object=_Mini()), fin)


def _tipos(codigo, fin=FIN):
    """Tipos de token que produce `codigo`, ';' implícitos marcados con '⏎'."""
    lexer = _lexer(fin)
    lexer.input(codigo)
    return ["⏎" if t.type == "SEMICOLON" and t.value == VALOR_IMPLICITO else t.type for t in lexer]


class PruebasInsercion(unittest.TestCase):
    def test_tras_identificador(self):
        self.assertEqual(_tipos("x\ny\n"), ["ID", "⏎", "ID", "⏎"])

    def test_no_tras_operador(self):
        # `x +` sigue en la línea siguiente: no hay fin de sentencia.
        self.assertEqual(_tipos("x +\ny"), ["ID", "PLUS", "ID", "⏎"])

    def test_no_tras_llave_abierta(self):
        self.assertEqual(_tipos("f() {\n}\n"), ["ID", "LPAREN", "RPAREN", "LBRACE", "RBRACE", "⏎"])

    def test_tras_return_e_incremento(self):
        self.assertEqual(_tipos("return\ni++\n"), ["RETURN", "⏎", "ID", "INCREMENT", "⏎"])

    def test_fin_de_archivo_sin_salto(self):
        self.assertEqual(_tipos("x"), ["ID", "⏎"])

    def test_fin_de_archivo_tras_operador(self):
        self.assertEqual(_tipos("x +"), ["ID", "PLUS"])

    def test_lineas_en_blanco_no_duplican(self):
        self.assertEqual(_tipos("x\n\n\ny"), ["ID", "⏎", "ID", "⏎"])

    def test_punto_y_coma_escrito_no_se_duplica(self):
        self.assertEqual(_tipos("x;\ny"), ["ID", "SEMICOLON", "ID", "⏎"])

    def test_string_crudo_de_varias_lineas(self):
        # El '+' está en la misma línea en que termina el string: no es fin de sentencia.
        self.assertEqual(_tipos("`a\nb` + c"), ["RAW", "PLUS", "ID", "⏎"])

    def test_comentario_de_varias_lineas_cuenta_como_salto(self):
        self.assertEqual(_tipos("x /* a\nb */ y"), ["ID", "⏎", "ID", "⏎"])

    def test_sin_tokens_de_fin_no_inserta(self):
        self.assertEqual(_tipos("x\ny\n", fin=set()), ["ID", "ID"])

    def test_posicion_justo_despues_del_token(self):
        codigo = "a\n\tfoo(1)\nb"
        lexer = _lexer()
        lexer.input(codigo)
        implicitos = [t for t in lexer if t.value == VALOR_IMPLICITO]
        self.assertEqual([(t.lineno, columna(codigo, t.lexpos)) for t in implicitos],
                         [(1, 2), (2, 8), (3, 2)])

    def test_reinicia_entre_textos(self):
        lexer = _lexer()
        lexer.input("x")
        list(lexer)
        lexer.input("y")
        self.assertEqual([t.type for t in lexer], ["ID", "SEMICOLON"])

    def test_delega_atributos(self):
        lexer = _lexer()
        lexer.input("x")
        self.assertEqual(lexer.lexdata, "x")
        lexer.errores = []
        self.assertEqual(lexer._lexer.errores, [])


class PruebasConYacc(unittest.TestCase):
    """La gramática ve SEMICOLON entre sentencias aunque el código no lo tenga."""

    tokens = _Mini.tokens

    def p_sentencias(self, p):
        """sentencias : sentencias sentencia
                      | sentencia"""
        p[0] = (p[1] if len(p) == 3 else []) + [p[len(p) - 1]]

    def p_sentencia(self, p):
        "sentencia : ID SEMICOLON"
        p[0] = (p[1], p.lineno(2))

    def p_error(self, p):
        self.errores.append(p)

    def test_parser_recibe_los_implicitos(self):
        self.errores = []
        parser = yacc.yacc(module=self, write_tables=False, debug=False, errorlog=yacc.NullLogger())
        resultado = parser.parse("a\nb; c\n", lexer=_lexer(), tracking=True)
        self.assertEqual(self.errores, [])
        self.assertEqual(resultado, [("a", 1), ("b", 2), ("c", 2)])

    def test_error_por_salto_de_linea(self):
        self.errores = []
        parser = yacc.yacc(module=self, write_tables=False, debug=False, errorlog=yacc.NullLogger())
        parser.parse("a +\n", lexer=_lexer(), tracking=True)
        self.assertEqual(self.errores[0].type, "PLUS")


class PruebasConstruirLexer(unittest.TestCase):
    def test_exige_semicolon_en_tokens(self):
        with mock.patch.object(lexico, "tokens", ["ID"]), \
             mock.patch.object(lexico, "fin_de_sentencia", {"ID"}):
            with self.assertRaisesRegex(ValueError, "SEMICOLON"):
                lexico.construir_lexer()


if __name__ == "__main__":
    unittest.main()
