// Algoritmo de prueba 1 — Paúl Rodríguez (AndreewCore)
//
// Avance 3: errores semánticos de la regla Retorno de funciones.
//   - notaDe devuelve un string (nombre) donde la firma pide float64.
//   - Mostrar no tiene tipo de retorno y su return lleva un valor (1).
//   cd backend && python probar_semantico.py ../algoritmos/algoritmo1_errorsem1.go -u AndreewCore

package main

import "fmt"

type Estudiante struct {
	nombre string
	edad   int
}

func (e Estudiante) Mostrar() {
	fmt.Println("Nombre:", e.nombre, "Edad:", e.edad)
	return 1
}

func (e Estudiante) Nombre() string {
	return e.nombre
}

func notaDe(notas map[string]float64, nombre string) float64 {
	return nombre
}

func main() {
	var curso string = "Lenguajes de Programacion"
	var edad int
	var activo bool = true
	var notas map[string]float64 = map[string]float64{"Ana": 9.5, "Luis": 8.0}
	var ana Estudiante = Estudiante{nombre: "Ana", edad: 20}

	fmt.Println("Curso:", curso)
	fmt.Print("Ingresa tu edad: ")
	fmt.Scan(&edad)

	ana.Mostrar()
	fmt.Println("Nota de", ana.Nombre(), ":", notaDe(notas, "Ana"))
	fmt.Println("Nota de Luis:", notas["Luis"])

	for activo {
		fmt.Println("for condicional: se repite mientras activo sea true")
		break
	}

	for {
		fmt.Println("for infinito: termina con break")
		break
	}
}
