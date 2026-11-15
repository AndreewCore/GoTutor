"""Corre el análisis sintáctico sobre un archivo .go y deja su log en logs/.

Uso (desde backend/):
    python probar_sintactico.py ../algoritmos/algoritmo1.go
    python probar_sintactico.py ../algoritmos/algoritmo2.go --usuario Danilogb18

Genera logs/sintactico-<usuarioGit>-<dd-mm-aaaa>-<HHhMM>.txt con el árbol
sintáctico y los errores, el log que pide la entrega del avance 2.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    """Parsea el archivo indicado, muestra el árbol y los errores y escribe el log sintáctico.

    Devuelve 0 si el parser corrió (con o sin errores del código Go) y 1 si
    el léxico encontró errores, sintactico.py no está implementado o lanzó
    una excepción.
    """
    parser = argparse.ArgumentParser(description="Prueba el analizador sintáctico con un archivo .go.")
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
    from analizador.sintactico import analizar_sintactico

    codigo = args.archivo.read_text(encoding="utf-8")

    # Igual que la API: el parser solo corre si el léxico terminó sin errores,
    # porque los caracteres que el lexer descarta dejarían errores sintácticos
    # que no son del alumno.
    estado_lex, _, errores_lex = servicio._ejecutar("lex", analizar_lexico, codigo)
    if estado_lex != "ok":
        print(f"El léxico terminó en estado '{estado_lex}': corrige estos errores primero "
              f"(prueba con probar_lexico.py).")
        _mostrar_errores(errores_lex)
        return 1

    estado, ast, errores = servicio._ejecutar("syn", analizar_sintactico, codigo)
    if estado == "no_impl":
        print("sintactico.py aún no define reglas: no hay nada que probar.")
        return 1

    print("\n".join(bitacora._arbol(ast)) if ast else "(no se construyó el árbol)")
    print(f"\nEstado: {estado}, {len(errores)} errores")
    _mostrar_errores(errores)

    # Léxico y semántico quedan "pendiente" para que bitacora escriba solo el log sintáctico.
    fases = {"lex": {"estado": "pendiente", "errores": []},
             "syn": {"estado": estado, "errores": errores},
             "sem": {"estado": "pendiente", "errores": []}}
    for ruta in bitacora.escribir(args.archivo.name, fases, None, ast, None):
        print(f"Log: backend/{ruta}")
    return 1 if estado == "fallo" else 0


def _mostrar_errores(errores) -> None:
    """Imprime cada error con su posición y sugerencia."""
    for e in errores:
        print(f"  [{e.linea}:{e.columna}] {e.mensaje}" + (f"  — {e.sugerencia}" if e.sugerencia else ""))


if __name__ == "__main__":
    # Para que los imports funcionen aunque se ejecute desde otra carpeta.
    sys.path.insert(0, str(Path(__file__).parent))
    sys.exit(main())
