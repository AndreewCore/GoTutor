"""Fase 1 — Análisis léxico de Go con PLY (ply.lex).

>>> A CARGO DEL GRUPO <<<

La API solo llama a `analizar_lexico(codigo)`. Mientras la lista `tokens`
esté vacía, la interfaz muestra "Función no implementada" en esta fase.

Contrato (ver modelos.py):
    analizar_lexico(codigo: str) -> tuple[list[Token], list[ErrorAnalisis]]
"""

import sys

import ply.lex as lex

from .modelos import ErrorAnalisis, Token, columna  # noqa: F401 (ErrorAnalisis se usa en t_error)

# ---------------------------------------------------------------------------
# Palabras reservadas
# ---------------------------------------------------------------------------
# TODO(grupo): completar. Ejemplo:
#   reservadas = {"func": "FUNC", "var": "VAR", "for": "FOR", ...}
reservadas: dict[str, str] = {}

# ---------------------------------------------------------------------------
# Lista de tokens (sintactico.py la importa)
# ---------------------------------------------------------------------------
# TODO(grupo): completar. Ejemplo:
#   tokens = ["ID", "INT_LIT", "STRING_LIT", "DEFINE", "PLUS", ...] + list(reservadas.values())
tokens: list[str] = []

# ---------------------------------------------------------------------------
# Reglas
# ---------------------------------------------------------------------------
# TODO(grupo): operadores simples (t_DEFINE = r':=') y funciones t_XXX(t).
# El orden importa: los casos específicos van antes que los generales.
#
#   def t_ID(t):
#       r'[A-Za-z_]\w*'
#       t.type = reservadas.get(t.value, "ID")
#       return t


# ---------------------------------------------------------------------------
# Errores léxicos
# ---------------------------------------------------------------------------
# TODO(grupo): definir t_error. Para que el error salga en la interfaz,
# agrégalo a `t.lexer.errores` en lugar de imprimirlo:
#
#   def t_error(t):
#       t.lexer.errores.append(ErrorAnalisis(
#           fase="lex",
#           linea=t.lineno,
#           columna=columna(t.lexer.lexdata, t.lexpos),
#           mensaje=f"Carácter no reconocido: '{t.value[0]}'.",
#           sugerencia="",
#       ))
#       t.lexer.skip(1)
#
# Recuerda contar las líneas (t.lexer.lineno) en tu regla de saltos de línea,
# si no, todos los errores aparecerán en la línea 1.


def construir_lexer():
    """Crea un lexer de PLY nuevo con la lista de errores vacía.

    sintactico.py también lo usa, así ambas fases tokenizan igual.
    """
    lexer = lex.lex(module=sys.modules[__name__])
    lexer.errores = []
    return lexer


def analizar_lexico(codigo: str) -> tuple[list[Token], list[ErrorAnalisis]]:
    """Tokeniza `codigo` y devuelve los tokens y los errores léxicos."""
    if not tokens:
        raise NotImplementedError("lexico.py aún no define tokens")

    lexer = construir_lexer()
    lexer.input(codigo)
    salida = [
        Token(tipo=t.type, valor=str(t.value), linea=t.lineno, columna=columna(codigo, t.lexpos))
        for t in iter(lexer.token, None)
    ]
    return salida, lexer.errores
