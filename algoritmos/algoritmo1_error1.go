// Algoritmo con errores léxicos 1 — Paúl Rodríguez (AndreewCore)
//
// Prueba los comentarios del léxico de AndreewCore: los válidos se ignoran
// y los mal escritos se reportan.
//   cd backend && python probar_lexico.py ../algoritmos/algoritmo1_error1.go -u AndreewCore
//
// Errores esperados:
//   línea 18: '#' usado como comentario (y sus palabras salen como ID)
//   línea 20: comentario /* sin cerrar (se come hasta el final del archivo)

package main

import "fmt"

/* Comentario de bloque válido */
func main() {
	fmt.Println("Hola") // comentario de línea válido
	# comentario con numeral
	fmt.Println("Mundo") /* bloque válido en la misma línea */
	/* comentario de bloque sin cerrar
	fmt.Println("Fin")
}
