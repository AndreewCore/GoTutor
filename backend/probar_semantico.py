"""Corre el análisis semántico sobre un archivo .go y deja su log en logs/.

Uso (desde backend/):
    python probar_semantico.py ../algoritmos/algoritmo1.go
    python probar_semantico.py ../algoritmos/algoritmo2.go --usuario Danilogb18

Genera logs/semantico-<usuarioGit>-<dd-mm-aaaa>-<HHhMM>.txt con la tabla de
símbolos y los errores semánticos, el log que pide la entrega del avance 3.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    """Analiza el archivo, muestra la tabla de símbolos y los errores y escribe el log semántico.

    Devuelve 0 si el semántico corrió (con o sin errores del código Go) y 1 si
    el léxico o el sintáctico encontraron errores o semantico.py lanzó una excepción.
    """
    parser = argparse.ArgumentParser(description="Prueba el analizador semántico con un archivo .go.")
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
    from analizador.semantico import analizar_semantico
    from analizador.sintactico import analizar_sintactico

    codigo = args.archivo.read_text(encoding="utf-8")

    # Igual que la API: el semántico solo corre si las fases anteriores terminaron sin errores.
    for fase, funcion, script in (("lex", analizar_lexico, "probar_lexico.py"),
                                  ("syn", analizar_sintactico, "probar_sintactico.py")):
        estado, ast, errores = servicio._ejecutar(fase, funcion, codigo)
        if estado != "ok":
            print(f"La fase '{fase}' terminó en estado '{estado}': corrige estos errores primero "
                  f"(prueba con {script}).")
            _mostrar_errores(errores)
            return 1

    estado, simbolos, errores = servicio._ejecutar("sem", analizar_semantico, ast, codigo)
    if estado == "no_impl":
        print("semantico.py aún no está implementado: no hay nada que probar.")
        return 1

    for s in simbolos or []:
        print(f"{s.nombre}\t{s.tipo}\t{s.categoria}\t{s.ambito}\tL{s.linea}\tusos={s.usos}")
    print(f"\nEstado: {estado}, {len(errores)} errores")
    _mostrar_errores(errores)

    # Léxico y sintáctico quedan "pendiente" para que bitacora escriba solo el log semántico.
    fases = {"lex": {"estado": "pendiente", "errores": []},
             "syn": {"estado": "pendiente", "errores": []},
             "sem": {"estado": estado, "errores": errores}}
    for ruta in bitacora.escribir(args.archivo.name, fases, None, ast, simbolos):
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
