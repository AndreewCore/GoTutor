"""Estructuras que comparten las tres fases y que el servidor envía al frontend.

Este archivo es el CONTRATO entre el analizador (grupo) y la interfaz.
No cambies los nombres de los campos: el frontend los lee tal cual.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Fase = Literal["lex", "syn", "sem"]


@dataclass
class Token:
    """Un token reconocido por el lexer. `linea` y `columna` empiezan en 1."""

    tipo: str  # p. ej. "FUNC", "ID", "INT_LIT", "DEFINE"
    valor: str  # el lexema tal como aparece en el código
    linea: int
    columna: int


@dataclass
class ErrorAnalisis:
    """Un error de cualquier fase, con un mensaje para el alumno."""

    fase: Fase
    linea: int
    columna: int
    mensaje: str  # qué está mal, p. ej. "Carácter no reconocido: '@'."
    sugerencia: str = ""  # cómo arreglarlo, p. ej. "Para multiplicar usa *."


@dataclass
class Nodo:
    """Nodo del árbol sintáctico que dibuja la interfaz.

    `error` marca el nodo en rojo: pon la fase ("syn" o "sem") que lo encontró.
    """

    tipo: str  # p. ej. "FuncDecl", "IfStmt", "BinaryExpr", "Ident"
    dato: str = ""  # texto corto junto al tipo, p. ej. "main", "+", '"fmt"'
    linea: int = 0
    hijos: list[Nodo] = field(default_factory=list)
    error: Fase | None = None


@dataclass
class Simbolo:
    """Una fila de la tabla de símbolos."""

    nombre: str
    tipo: str  # p. ej. "int", "func(int, int) int", "desconocido"
    categoria: str  # "Variable", "Función", "Parámetro", "Importación", "Sin declarar"...
    ambito: str  # "global", "main", "main › for"...
    linea: int  # línea de la declaración (o del primer uso si no está declarado)
    usos: int = 0
    error: bool = False


def columna(codigo: str, lexpos: int) -> int:
    """Convierte la posición absoluta de PLY (`t.lexpos`) en columna 1-based."""
    inicio_linea = codigo.rfind("\n", 0, lexpos) + 1
    return lexpos - inicio_linea + 1


def a_dict(obj) -> dict:
    """Serializa cualquiera de las dataclasses de arriba (incluye hijos anidados)."""
    return asdict(obj)
