// Algoritmo con errores sintácticos 1 — Paúl Rodríguez (AndreewCore)
//
// Avance 2: errores a propósito en las declaraciones de AndreewCore
// (struct, variable con tipo, map y acceso por índice, fmt.Scan).
//   cd backend && python probar_sintactico.py ../algoritmos/algoritmo1_errorsyn1.go -u AndreewCore
//
// Errores esperados:
//   línea 18: ',' entre los campos del struct (en Go van en líneas separadas)
//   línea 23: var con tipo sin '=' antes del valor
//   línea 25: acceso por índice sin ']' de cierre
//   línea 26: fmt.Scan(&) sin la variable después de '&'

package main

import "fmt"

type Producto struct {
	nombre string,
	precio float64
}

func main() {
	var nombre string "Lapiz"
	var stock map[string]int = map[string]int{"lapiz": 40, "cuaderno": 3}
	fmt.Println(nombre, stock["lapiz")
	fmt.Scan(&)
}
