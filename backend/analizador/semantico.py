"""Fase 3 — Análisis semántico: recorre el AST y llena la tabla de símbolos.

>>> A CARGO DEL GRUPO <<<

La API llama a `analizar_semantico(ast, codigo)` solo si las fases léxica y
sintáctica terminaron sin errores. Mientras lance NotImplementedError, la
interfaz muestra "Función no implementada" en esta fase.

Contrato (ver modelos.py):
    analizar_semantico(ast: Nodo, codigo: str)
        -> tuple[list[Simbolo], list[ErrorAnalisis]]

Si un nodo tiene un error semántico, ponle `nodo.error = "sem"`: como el árbol
se envía a la interfaz después de esta fase, se verá marcado en rojo.

Reglas que conviene revisar (las mismas de los ejemplos de la interfaz):
  - variable usada sin declarar, o fuera de su ámbito
  - variable local declarada y nunca usada
  - asignación con tipos incompatibles (int = string)
  - condición de if/for que no es bool
  - número de valores en la asignación distinto a los que devuelve la función
"""

from .modelos import ErrorAnalisis, Nodo, Simbolo


def analizar_semantico(ast: Nodo, codigo: str) -> tuple[list[Simbolo], list[ErrorAnalisis]]:
    """Revisa el significado del programa y devuelve la tabla de símbolos y los errores."""
    # TODO(grupo): implementar. Ejemplo de error:
    #   ErrorAnalisis("sem", 20, 14, "'resultado' no está declarado en este ámbito.",
    #                 "Declara la variable antes de usarla.")
    raise NotImplementedError("semantico.py aún no está implementado")
