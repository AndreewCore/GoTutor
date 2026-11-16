// Algoritmo con errores sintácticos 2 — Paúl Rodríguez (AndreewCore)
//
// Avance 2: errores a propósito en funciones, métodos, fmt y for de
// AndreewCore.
//   cd backend && python probar_sintactico.py ../algoritmos/algoritmo1_errorsyn2.go -u AndreewCore
//
// Errores esperados:
//   línea 22: función con retorno sin ')' al cerrar los parámetros
//   línea 27: propiedad incompleta: 'e.' sin el nombre del campo
//   línea 32: fmt.Println sin ')' de cierre
//   línea 34: falta ',' entre los argumentos de fmt.Println
//   línea 39: for infinito sin '}': el archivo termina antes de cerrarlo

package main

import "fmt"

type Estudiante struct {
	nombre string
}

func doble(n int int {
	return n
}

func (e Estudiante) Mostrar() {
	fmt.Println(e.)
}

func main() {
	var activo bool = true
	fmt.Println("Inicio"
	for activo {
		fmt.Println("Activo" "si")
		break
	}
	for {
		break
}
