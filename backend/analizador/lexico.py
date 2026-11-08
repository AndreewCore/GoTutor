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
tokens_AndreewCore: list[str] = [
    "LLAVE_IZQ", "LLAVE_DER",
    "PAREN_IZQ", "PAREN_DER",
    "CORCHETE_IZQ", "CORCHETE_DER"
    "COMA", "PUNTO_COMA", "DOS_PUNTOS", "PUNTO",
]

reservadas_AndreewCore: dict[str, str] = {}

# TODO(AndreewCore)

# DELIMITADORES

t_LLAVE_IZQ = r"\{"
t_LLAVE_DER = r"\}"
t_PAREN_IZQ = r"\("
t_PAREN_DER = r"\)"
t_CORCHETE_IZQ = r"\["
t_CORCHETE_DER = r"\]"
t_COMA = r","
t_PUNTO_COMA = r";"
t_DOS_PUNTOS = r":" # Tener en cuenta :=
t_PUNTO = r"\." # Tener en cuenta t_DECIMAL

t_ignore = " \t\r"

def t_NUEVA_LINEA(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

# Pendiente ; insertado al final

# COMENTARIOS

# Formato de COMENTARIO BLOQUE: /* COMENTARIO */

def t_COMENTARIO_BLOQUE(t):

    r"/\*[\s\S]*?\*/" #\s espacios en blanco y \S cualquier caractér *? n o más veces

    t.lexer.lineno += t.value.count("\n")

    # COMENTARIO BLOQUE SIN CERRAR

def t_COMENTARIO_SIN_CERRAR(t):
    r"/\*[\s\S]*"

    # Solo llega aquí si no hubo '*/': se come hasta el final del archivo.

    # Indicación de error via lexer
    t.lexer.errores.append(ErrorAnalisis(
        fase="lex",
        linea=t.lexer.lineno,
        columna=columna(t.lexer.lexdata, t.lexpos),
        mensaje="Comentario de varias líneas sin cerrar.",
        sugerencia="Cierra el comentario con */ o usa // si es de una sola línea.",
    ))

    t.lexer.lineno += t.value.count("\n")

# Formato de COMENTARIO LINEA: // COMENTARIO

def t_COMENTARIO_LINEA(t):
    r"//[^\n]*" # [^\n] cualquier caractér menos \n para que termine antes del espacio.

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
