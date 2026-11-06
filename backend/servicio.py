"""Ejecuta las tres fases en orden y arma la respuesta JSON para el frontend.

Estados de cada fase:
  ok         terminó sin errores
  error      encontró errores del código Go del alumno
  pendiente  no se ejecutó porque una fase anterior no quedó en "ok"
  no_impl    el archivo del grupo todavía lanza NotImplementedError
  fallo      el analizador del grupo lanzó una excepción (bug en Python)
"""

from __future__ import annotations

import threading
import traceback

import bitacora
from analizador.lexico import analizar_lexico
from analizador.modelos import ErrorAnalisis, a_dict
from analizador.semantico import analizar_semantico
from analizador.sintactico import analizar_sintactico

FASES = ("lex", "syn", "sem")
ARCHIVO_DE_FASE = {"lex": "lexico.py", "syn": "sintactico.py", "sem": "semantico.py"}

# Flask atiende cada petición en un hilo, pero los analizadores guardan estado
# a nivel de módulo (`_errores` en sintactico.py, el parser de PLY, lo que el
# grupo agregue en semantico.py). Sin este candado, dos análisis simultáneos
# —p. ej. dos pestañas en la presentación— mezclarían sus errores. Un análisis
# dura milisegundos, así que atenderlos en fila no se nota.
_candado = threading.Lock()


def _ejecutar(fase: str, funcion, *args):
    """Llama a la función del grupo y traduce excepciones a un estado de fase.

    Devuelve (estado, resultado, errores). `resultado` es None si no hubo salida.
    """
    try:
        resultado, errores = funcion(*args)
    except NotImplementedError:
        return "no_impl", None, []
    except Exception as exc:  # noqa: BLE001
        # Un bug en el analizador no debe tumbar la API: se muestra como un
        # error más para que el grupo lo vea en la interfaz y en la consola.
        traceback.print_exc()
        aviso = ErrorAnalisis(
            fase=fase,
            linea=1,
            columna=1,
            mensaje=f"Error interno en {ARCHIVO_DE_FASE[fase]}: {type(exc).__name__}: {exc}",
            sugerencia="Revisa la consola del servidor Flask para ver el traceback completo.",
        )
        return "fallo", None, [aviso]
    return ("error" if errores else "ok"), resultado, list(errores)


def analizar(codigo: str, archivo: str = "main.go", escribir_logs: bool = True) -> dict:
    """Corre léxico → sintáctico → semántico sobre `codigo` y devuelve el JSON de respuesta.

    Atiende un análisis a la vez (ver `_candado`).
    """
    with _candado:
        return _analizar(codigo, archivo, escribir_logs)


def _analizar(codigo: str, archivo: str, escribir_logs: bool) -> dict:
    """Implementación de `analizar`; supone que ya se tiene `_candado`."""
    fases = {f: {"estado": "pendiente", "errores": []} for f in FASES}
    tokens = ast = simbolos = None

    estado, tokens, errores = _ejecutar("lex", analizar_lexico, codigo)
    fases["lex"] = {"estado": estado, "errores": errores}

    if estado == "ok":
        estado, ast, errores = _ejecutar("syn", analizar_sintactico, codigo)
        fases["syn"] = {"estado": estado, "errores": errores}

        # El semántico necesita un árbol completo; con errores sintácticos el AST es parcial.
        if estado == "ok" and ast is not None:
            estado, simbolos, errores = _ejecutar("sem", analizar_semantico, ast, codigo)
            fases["sem"] = {"estado": estado, "errores": errores}

    logs = bitacora.escribir(archivo, fases, tokens, ast, simbolos) if escribir_logs else []

    return {
        "archivo": archivo,
        "fases": {
            f: {"estado": d["estado"], "errores": [a_dict(e) for e in d["errores"]]}
            for f, d in fases.items()
        },
        "tokens": [a_dict(t) for t in tokens] if tokens is not None else None,
        "ast": a_dict(ast) if ast is not None else None,
        "simbolos": [a_dict(s) for s in simbolos] if simbolos is not None else None,
        "logs": logs,
    }
