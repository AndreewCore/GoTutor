"""Fase 2 — Análisis sintáctico de Go con PLY (ply.yacc).

>>> A CARGO DEL GRUPO <<<

La API solo llama a `analizar_sintactico(codigo)`. Mientras no exista
ninguna regla p_xxx, la interfaz muestra "Función no implementada".

Contrato (ver modelos.py):
    analizar_sintactico(codigo: str) -> tuple[Nodo | None, list[ErrorAnalisis]]

El árbol que devuelvas es el que se dibuja en la interfaz y el que recibe
semantico.py. Construye objetos `Nodo`, no tuplas:

    def p_for_stmt(p):
        'for_stmt : FOR simple_stmt SEMICOLON expr SEMICOLON simple_stmt block'
        p[0] = Nodo("ForStmt", "", p.lineno(1), [p[2], p[4], p[6], p[7]])

Para que p.lineno(n) funcione, el lexer debe actualizar t.lexer.lineno.
"""

import sys

import ply.yacc as yacc

from .lexico import construir_lexer, tokens  # noqa: F401 (yacc lee `tokens` de este módulo)
from .modelos import ErrorAnalisis, Nodo, columna

# Los errores de la ejecución actual. analizar_sintactico los reinicia.
_errores: list[ErrorAnalisis] = []

# ---------------------------------------------------------------------------
# Precedencia de operadores
# ---------------------------------------------------------------------------
# TODO(grupo): ejemplo
#   precedence = (
#       ("left", "OR"), ("left", "AND"),
#       ("left", "EQ", "NEQ", "LT", "LE", "GT", "GE"),
#       ("left", "PLUS", "MINUS"), ("left", "TIMES", "DIVIDE", "MOD"),
#   )

# ---------------------------------------------------------------------------
# Gramática
# ---------------------------------------------------------------------------
# TODO(grupo): la primera regla define el símbolo inicial.
#
#   def p_programa(p):
#       'programa : package_clause import_list decl_list'
#       p[0] = Nodo("Program", "", 1, [p[1], *p[2], *p[3]])


# ---------------------------------------------------------------------------
# Errores sintácticos
# ---------------------------------------------------------------------------
# TODO(grupo): definir p_error. Para que el error salga en la interfaz,
# agrégalo a `_errores`:
#
#   def p_error(p):
#       if p is None:
#           _errores.append(ErrorAnalisis("syn", <última línea>, 1,
#                                         "Fin de archivo inesperado.", ""))
#           return
#       _errores.append(ErrorAnalisis(
#           fase="syn",
#           linea=p.lineno,
#           columna=columna(p.lexer.lexdata, p.lexpos),
#           mensaje=f"Token inesperado: '{p.value}'.",
#           sugerencia="",
#       ))
#
# Ojo: los ';' que agrega el lexer al final de línea llegan con p.value == "\n"
# (ver puntoycoma.py). Para esos conviene decir "salto de línea inesperado",
# como hace Go, porque el alumno no escribió ningún ';'.


def _tiene_reglas() -> bool:
    """Indica si el grupo ya escribió alguna regla de gramática."""
    modulo = sys.modules[__name__]
    return any(nombre.startswith("p_") and nombre != "p_error" for nombre in vars(modulo))


def analizar_sintactico(codigo: str) -> tuple[Nodo | None, list[ErrorAnalisis]]:
    """Parsea `codigo` y devuelve el AST (o None si no se pudo) y los errores."""
    if not _tiene_reglas():
        raise NotImplementedError("sintactico.py aún no define reglas")

    _errores.clear()
    # write_tables/debug en False: no queremos parsetab.py ni parser.out
    # regenerándose en el repo cada vez que la API recibe una petición.
    parser = yacc.yacc(module=sys.modules[__name__], write_tables=False, debug=False)
    ast = parser.parse(codigo, lexer=construir_lexer(), tracking=True)
    return ast, list(_errores)
