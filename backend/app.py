"""Servidor Flask de GoTutor: expone el analizador y sirve el frontend compilado.

Desarrollo:  python app.py   (el frontend de Vite redirige /api a este puerto)
"""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

import servicio

DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
MAX_CODIGO = 200_000  # caracteres; un programa de práctica nunca se acerca a esto

app = Flask(__name__, static_folder=None)


@app.get("/api/salud")
def salud():
    """Confirma que la API está viva (la usa el frontend para avisar si no hay servidor)."""
    return jsonify(ok=True)


@app.post("/api/analizar")
def analizar():
    """Recibe {codigo, archivo} y devuelve el resultado de las tres fases."""
    datos = request.get_json(silent=True) or {}
    codigo = datos.get("codigo")
    archivo = str(datos.get("archivo") or "main.go")[:120]
    if not isinstance(codigo, str):
        return jsonify(error="Falta el campo 'codigo' (texto)."), 400
    if len(codigo) > MAX_CODIGO:
        return jsonify(error="El archivo es demasiado grande para analizarlo."), 413
    # Los editores de Windows guardan CRLF; PLY contaría mal las columnas.
    codigo = codigo.replace("\r\n", "\n").replace("\r", "\n")
    return jsonify(servicio.analizar(codigo, archivo))


@app.get("/", defaults={"ruta": ""})
@app.get("/<path:ruta>")
def frontend(ruta: str):
    """Sirve el build de Vite (pnpm build) para tener todo en un solo proceso."""
    if not DIST.exists():
        return "Frontend sin compilar. En desarrollo usa: cd frontend && pnpm dev", 404
    if ruta and (DIST / ruta).is_file():
        return send_from_directory(DIST, ruta)
    return send_from_directory(DIST, "index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 8000)), debug=True)
