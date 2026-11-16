// Algoritmo con errores léxicos 2 — Paúl Rodríguez (AndreewCore)
//
// Prueba los delimitadores del léxico de AndreewCore: símbolos que se
// confunden con delimitadores y que Go no acepta.
//   cd backend && python probar_lexico.py ../algoritmos/algoritmo1_error2.go -u AndreewCore
//
// Errores esperados:
//   línea 18: comillas simples en 'Ana' (dos errores)
//   línea 19: '@' en lugar de '['
//   línea 20: cadena con acento grave `Fin` (dos errores)

package main

import "fmt"

func main() {
	var notas map[string]int = map[string]int{"Ana": 9, "Luis": 8}
	fmt.Println(notas['Ana'])
	fmt.Println(notas@"Luis"])
	fmt.Println(`Fin`)
}
