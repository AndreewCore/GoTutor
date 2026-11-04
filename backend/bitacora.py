"""Escribe un log por fase en backend/logs/ cada vez que se analiza código.

Nombre: <fase>-<usuarioGit>-<dd-mm-aaaa>-<HHhMM>.txt
  p. ej. lexico-AndreewCore-02-11-2026-14h05.txt

Si hay varios análisis en el mismo minuto, quedan todos en ese archivo,
uno tras otro y separados por una línea de '='.
"""

from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime
from functools import cache
from pathlib import Path

CARPETA = Path(__file__).parent / "logs"
NOMBRE = {"lex": "lexico", "syn": "sintactico", "sem": "semantico"}
SEPARADOR = "=" * 72


@cache
def usuario_git() -> str:
    """Usuario de Git para el nombre del log; GOTUTOR_USUARIO_GIT tiene prioridad."""
    if usuario := os.environ.get("GOTUTOR_USUARIO_GIT"):
        return _limpiar(usuario)
    try:
        salida = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True, timeout=3,
            cwd=Path(__file__).parent,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        salida = ""
    return _limpiar(salida) or "desconocido"


def _limpiar(texto: str) -> str:
    """Deja solo caracteres seguros para un nombre de archivo."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "", texto.replace(" ", ""))


def _errores(errores) -> list[str]:
    """Formatea los errores de una fase."""
    if not errores:
        return ["Sin errores."]
    return [f"[{e.linea}:{e.columna}] {e.mensaje}" + (f"  — {e.sugerencia}" if e.sugerencia else "")
            for e in errores]


def _arbol(nodo, nivel: int = 0) -> list[str]:
    """Dibuja el AST indentado, una línea por nodo."""
    marca = f"  <-- error {nodo.error}" if nodo.error else ""
    lineas = [f"{'  ' * nivel}{nodo.tipo} {nodo.dato}".rstrip() + f"  (L{nodo.linea}){marca}"]
    for hijo in nodo.hijos:
        lineas += _arbol(hijo, nivel + 1)
    return lineas


def escribir(archivo: str, fases: dict, tokens, ast, simbolos) -> list[str]:
    """Escribe los logs de las fases que se ejecutaron y devuelve sus rutas relativas."""
    CARPETA.mkdir(exist_ok=True)
    ahora = datetime.now()
    sello = ahora.strftime("%d-%m-%Y-%Hh%M")
    cabecera = [f"GoTutor — {archivo}", f"Fecha: {ahora:%d/%m/%Y %H:%M:%S}", f"Usuario Git: {usuario_git()}", ""]

    contenido = {}
    if fases["lex"]["estado"] in ("ok", "error", "fallo"):
        contenido["lex"] = ["TOKENS"] + [
            f"{t.linea}:{t.columna}\t{t.tipo}\t{t.valor!r}" for t in (tokens or [])
        ]
    if fases["syn"]["estado"] in ("ok", "error", "fallo"):
        contenido["syn"] = ["ÁRBOL SINTÁCTICO"] + (_arbol(ast) if ast else ["(no se construyó)"])
    if fases["sem"]["estado"] in ("ok", "error", "fallo"):
        contenido["sem"] = ["TABLA DE SÍMBOLOS"] + [
            f"{s.nombre}\t{s.tipo}\t{s.categoria}\t{s.ambito}\tL{s.linea}\tusos={s.usos}" for s in (simbolos or [])
        ]

    rutas = []
    for fase, cuerpo in contenido.items():
        ruta = CARPETA / f"{NOMBRE[fase]}-{usuario_git()}-{sello}.txt"
        texto = "\n".join(cabecera + cuerpo + ["", "ERRORES"] + _errores(fases[fase]["errores"])) + "\n"
        # El nombre solo tiene precisión de minutos (formato pedido para la
        # entrega): un segundo análisis en el mismo minuto se agrega al final
        # en vez de borrar el anterior.
        if ruta.exists():
            texto = f"\n{SEPARADOR}\n\n" + texto
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(texto)
        rutas.append(f"logs/{ruta.name}")
    return rutas
