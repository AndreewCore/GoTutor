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
tokens_AndreewCore: list[str] = []
reservadas_AndreewCore: dict[str, str] = {}

# TODO(AndreewCore)

# ===== FIN aporte: Paúl Rodríguez (AndreewCore) =====


# ===== INICIO aporte: Danilo García (Danilogb18) =====
# Reglas asignadas: Variables (identificadores), Tipos de datos.
tokens_Danilogb18: list[str] = ["ID", "ENTERO", "DECIMAL", "CADENA"]
 
# Tipos primitivos y literales booleanos. En Go no son palabras reservadas sino identificadores predeclarados, pero se les da token propio para que el sintáctico distinga un tipo (`var x int`) de una variable. Se resuelven en t_ID igual que las reservadas.
reservadas_Danilogb18: dict[str, str] = {
    "int": "TIPO_INT",
    "float64": "TIPO_FLOAT",
    "string": "TIPO_STRING",
    "bool": "TIPO_BOOL",
    "true": "TRUE",
    "false": "FALSE",
}
 
 
def _error_lexico(t, mensaje: str, sugerencia: str) -> None:
    """Registra un error léxico de este bloque sin detener el análisis."""
    t.lexer.errores.append(ErrorAnalisis(
        fase="lex",
        linea=t.lexer.lineno,
        columna=columna(t.lexer.lexdata, t.lexpos),
        mensaje=mensaje,
        sugerencia=sugerencia,
    ))
 
 
# El orden de estas funciones importa porque PLY las prueba de arriba hacia abajo
# 1) número mal formado, antes que los números válidos, para que `12abc` no  salga como ENTERO(12) + ID(abc);
# 2) DECIMAL antes que ENTERO, para que `3.14` no salga como 3, '.', 14;
# 3) CADENA antes que la cadena sin cerrar.

 
def t_NUMERO_MAL_FORMADO(t):
    r"[0-9]+(\.[0-9]+)?[a-zA-Z_][a-zA-Z_0-9]*"
    resto = t.value.lstrip("0123456789")
    digitos = t.value[: len(t.value) - len(resto)]
    if resto[0].isalpha():
        # `2nota`: probablemente una variable con el número adelante.
        sugerencia = (f"Un identificador no puede empezar con un dígito. " f"Si es una variable, prueba con '{resto}{digitos}'.")
    else:
        # `12.5kg`, `12_000`: un número con algo pegado que GoTutor no admite.
        sugerencia = ("Un número no puede llevar letras ni guiones bajos pegados: ""deja solo el valor numérico.")
    _error_lexico(t, f"Número mal formado: '{t.value}'.", sugerencia)
 
 
def t_DECIMAL(t):
    r"[0-9]+\.[0-9]+"
    return t
 
 
def t_ENTERO(t):
    r"[0-9]+"
    return t
 
 
def t_CADENA(t):
    r'"([^"\\\n]|\\.)*"'
    # Admite secuencias de escape como \n o \" dentro de la cadena.
    return t
 
 
def t_CADENA_SIN_CERRAR(t):
    r'"([^"\\\n]|\\.)*\\?'
    # El \? final absorbe una barra suelta al final de la línea; sin él, `"fin\` daría además un segundo error por el carácter '\'.
    _error_lexico(t, "Cadena de texto sin cerrar.", 'Agrega una comilla doble (") al final del texto, en la misma línea.')
 
 
def t_ID(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    # Se captura la palabra completa y luego se consulta el diccionario unido. Así `format` es ID y no FOR seguido de `mat`.
    t.type = reservadas.get(t.value, "ID")
    return t
 

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
