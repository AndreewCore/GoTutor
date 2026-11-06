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
from .puntoycoma import LexerConPuntoYComa

# ===========================================================================
# Cómo se reparte este archivo
# ===========================================================================
# Cada integrante escribe SOLO dentro de su bloque INICIO/FIN y agrega sus
# tokens a su propia lista (`tokens_<usuario>`) y sus palabras reservadas a su
# propio diccionario (`reservadas_<usuario>`). Al final del archivo se juntan
# en `tokens` y `reservadas`; así nadie edita las mismas líneas y los merges no
# chocan.
#
# Orden en PLY: las reglas con función (def t_X) se prueban en el orden en que
# aparecen en el archivo; las de string (t_X = r'...') se ordenan solas de la
# más larga a la más corta. Las palabras reservadas no llevan regla propia:
# se resuelven dentro de t_ID con el diccionario `reservadas`.


# ===== INICIO aporte: Paúl Rodríguez (AndreewCore) =====
# Reglas asignadas: Delimitadores, Comentarios.
# También aquí: t_ignore, saltos de línea (t.lexer.lineno) y t_error.
tokens_AndreewCore: list[str] = []
reservadas_AndreewCore: dict[str, str] = {}

# Punto y coma automático (Delimitadores, ver puntoycoma.py): Go agrega un ';'
# al final de la línea si el último token es uno de estos tipos. Vacío = no se
# inserta nada. Si se usa, `tokens` debe incluir "SEMICOLON", que es el tipo
# que puntoycoma.py le da al ';' insertado.
fin_de_sentencia: set[str] = set()

# TODO(AndreewCore)

# ===== FIN aporte: Paúl Rodríguez (AndreewCore) =====


# ===== INICIO aporte: Danilo García (Danilogb18) =====
# Reglas asignadas: Variables (identificadores), Tipos de datos.
tokens_Danilogb18: list[str] = []
reservadas_Danilogb18: dict[str, str] = {}

# TODO(Danilogb18)

# ===== FIN aporte: Danilo García (Danilogb18) =====


# ===== INICIO aporte: Samuel Echeverría (SamuelEcheverria) =====
# Reglas asignadas: Operadores, Palabras reservadas.
tokens_SamuelEcheverria: list[str] = []
reservadas_SamuelEcheverria: dict[str, str] = {}

# TODO(SamuelEcheverria)

# ===== FIN aporte: Samuel Echeverría (SamuelEcheverria) =====


# ---------------------------------------------------------------------------
# Unión de los aportes (sintactico.py importa `tokens`)
# ---------------------------------------------------------------------------
reservadas: dict[str, str] = {
    **reservadas_AndreewCore,
    **reservadas_Danilogb18,
    **reservadas_SamuelEcheverria,
}
# dict.fromkeys quita repetidos sin perder el orden: PLY falla si un token se
# declara dos veces, y es fácil que dos aportes nombren el mismo.
tokens: list[str] = list(dict.fromkeys(
    tokens_AndreewCore + tokens_Danilogb18 + tokens_SamuelEcheverria + list(reservadas.values())
))

# ---------------------------------------------------------------------------
# Errores léxicos (referencia para quien escriba t_error)
# ---------------------------------------------------------------------------
# Para que el error salga en la interfaz y en el log, agrégalo a
# `t.lexer.errores` en lugar de imprimirlo:
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
# Recuerda contar las líneas (t.lexer.lineno) en la regla de saltos de línea;
# si no, todos los errores aparecerán en la línea 1.


def construir_lexer():
    """Crea un lexer de PLY nuevo con la lista de errores vacía.

    sintactico.py también lo usa, así ambas fases tokenizan igual (con los
    ';' implícitos incluidos).
    """
    if fin_de_sentencia and "SEMICOLON" not in tokens:
        raise ValueError("fin_de_sentencia necesita que 'SEMICOLON' esté en tokens")
    lexer = lex.lex(module=sys.modules[__name__])
    lexer.errores = []
    return LexerConPuntoYComa(lexer, fin_de_sentencia)


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
