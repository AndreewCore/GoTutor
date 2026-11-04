"""Inserción automática de punto y coma, como hace el escáner de Go.

En Go casi nadie escribe `;`: el escáner lo agrega al final de una línea si el
último token puede cerrar una sentencia (un identificador, un literal, `)`,
`]`, `}`, `return`, `++`...). Así la gramática puede exigir SEMICOLON entre
sentencias igual que la especificación, sin reglas especiales para los saltos
de línea. Ver https://go.dev/ref/spec#Semicolons

Este módulo es parte del esqueleto: el grupo solo decide qué tokens cierran
una sentencia (`fin_de_sentencia` en lexico.py).
"""

from __future__ import annotations

import ply.lex as lex

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
