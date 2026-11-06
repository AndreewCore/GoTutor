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

# Punto y coma automático (Delimitadores): en Go casi nadie escribe `;`; el
# escáner lo agrega al final de una línea si el último token puede cerrar una
# sentencia (un identificador, un literal, `)`, `]`, `}`, `return`, `++`...).
# Así la gramática puede exigir SEMICOLON entre sentencias sin reglas para los
# saltos de línea. Ver https://go.dev/ref/spec#Semicolons
#
# `fin_de_sentencia` son esos tipos de token. Vacío = no se inserta nada. Si se
# usa, `tokens` debe incluir "SEMICOLON", el tipo que recibe el ';' insertado.
# Va en un envoltorio del lexer (LexerConPuntoYComa) y no en t_newline porque
# las reglas de PLY no ven el token anterior.
fin_de_sentencia: set[str] = set()

# Go también usa "\n" como lexema del punto y coma implícito; sirve para que
# p_error diga "salto de línea inesperado" y no "';' inesperado", porque el
# alumno nunca escribió ese ';'.
VALOR_IMPLICITO = "\n"


class LexerConPuntoYComa:
    """Envuelve un lexer de PLY e inserta SEMICOLON donde Go lo haría.

    Se comporta como el lexer original (input, token, lineno, lexdata,
    errores...), así que yacc y analizar_lexico lo usan sin cambios.
    """

    def __init__(self, lexer, fin_de_sentencia: set[str]):
        """`fin_de_sentencia`: tipos de token tras los que un salto de línea es ';'."""
        self._lexer = lexer
        self._fin = frozenset(fin_de_sentencia)
        self._reiniciar()

    def _reiniciar(self):
        """Olvida el estado del texto anterior."""
        self._pendiente = None
        self._ultimo = None  # (tipo, línea donde termina, lexpos donde termina)
        self._terminado = False

    def __getattr__(self, nombre):
        """Delega todo lo demás (lineno, lexdata, errores, skip...) en el lexer de PLY."""
        return getattr(self._lexer, nombre)

    def __setattr__(self, nombre, valor):
        """Escribe en el lexer de PLY, salvo el estado propio (atributos con '_').

        t_error recibe el lexer de PLY en `t.lexer`, no este envoltorio; si
        `lexer.errores = []` quedara aquí, los errores irían a otra lista.
        """
        if nombre.startswith("_"):
            object.__setattr__(self, nombre, valor)
        else:
            setattr(self._lexer, nombre, valor)

    def input(self, codigo: str):
        """Carga un texto nuevo."""
        self._reiniciar()
        self._lexer.input(codigo)

    def token(self):
        """Devuelve el siguiente token, intercalando los ';' implícitos."""
        if self._pendiente is not None:
            tok, self._pendiente = self._pendiente, None
            return self._recordar(tok)
        if self._terminado:
            return None

        tok = self._lexer.token()
        if tok is None:
            # Go también cierra la última sentencia del archivo sin salto final.
            self._terminado = True
            return self._implicito() if self._cierra_sentencia() else None

        # PLY avanza lineno al consumir saltos (o un comentario o string de
        # varias líneas); si el token empieza en una línea posterior a donde
        # terminó el anterior, hubo un salto de línea entre ambos.
        if self._cierra_sentencia() and tok.lineno > self._ultimo[1]:
            self._pendiente = tok
            return self._implicito()
        return self._recordar(tok)

    def __iter__(self):
        """Permite `for tok in lexer`, como el lexer de PLY."""
        return iter(self.token, None)

    def _cierra_sentencia(self) -> bool:
        """Indica si el último token emitido puede terminar una sentencia."""
        return self._ultimo is not None and self._ultimo[0] in self._fin

    def _recordar(self, tok):
        """Guarda dónde terminó `tok`; lineno/lexpos del lexer apuntan justo después de él."""
        self._ultimo = (tok.type, self._lexer.lineno, self._lexer.lexpos)
        return tok

    def _implicito(self):
        """Crea el SEMICOLON implícito justo después del token anterior."""
        tok = lex.LexToken()
        tok.type = "SEMICOLON"
        tok.value = VALOR_IMPLICITO
        _, tok.lineno, tok.lexpos = self._ultimo
        tok.lexer = self
        self._ultimo = ("SEMICOLON", tok.lineno, tok.lexpos)
        return tok


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
