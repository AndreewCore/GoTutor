"""Corre solo el análisis léxico sobre un archivo .go y deja su log en logs/.

Uso (desde backend/):
    python probar_lexico.py ../algoritmos/algoritmo1.go
    python probar_lexico.py ../algoritmos/algoritmo2.go --usuario Danilogb18

Genera logs/lexico-<usuarioGit>-<dd-mm-aaaa>-<HHhMM>.txt con todos los tokens
reconocidos y los errores, el log que pide la entrega del avance 1.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    """Tokeniza el archivo indicado, muestra el resultado y escribe el log léxico.

    Devuelve 0 si el lexer corrió (con o sin errores del código Go) y 1 si
    lexico.py aún no está implementado o lanzó una excepción.
    """
    parser = argparse.ArgumentParser(description="Prueba el analizador léxico con un archivo .go.")
    parser.add_argument("archivo", type=Path, help="programa Go a analizar")
    parser.add_argument("-u", "--usuario", help="usuario de GitHub para el nombre del log "
                        "(por defecto, git config user.name)")
    args = parser.parse_args(argv)

    # Se fija antes de importar bitacora porque usuario_git() guarda en caché
    # el primer valor que calcula.
    if args.usuario:
        os.environ["GOTUTOR_USUARIO_GIT"] = args.usuario

    import bitacora
    import servicio
    from analizador.lexico import analizar_lexico

    codigo = args.archivo.read_text(encoding="utf-8")
    estado, tokens, errores = servicio._ejecutar("lex", analizar_lexico, codigo)

    if estado == "no_impl":
        print("lexico.py aún no define tokens: no hay nada que probar.")
        return 1

    for t in tokens or []:
        print(f"{t.linea}:{t.columna}\t{t.tipo}\t{t.valor!r}")
    print(f"\n{len(tokens or [])} tokens, {len(errores)} errores")
    for e in errores:
        print(f"  [{e.linea}:{e.columna}] {e.mensaje}" + (f"  — {e.sugerencia}" if e.sugerencia else ""))

    # Las fases siguientes quedan "pendiente" para que bitacora escriba solo el log léxico.
    fases = {"lex": {"estado": estado, "errores": errores},
             "syn": {"estado": "pendiente", "errores": []},
             "sem": {"estado": "pendiente", "errores": []}}
    for ruta in bitacora.escribir(args.archivo.name, fases, tokens, None, None):
        print(f"Log: backend/{ruta}")
    return 1 if estado == "fallo" else 0


if __name__ == "__main__":
    sys.exit(main())
