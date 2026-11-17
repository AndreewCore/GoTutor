// Algoritmo de prueba 1 — Paúl Rodríguez (AndreewCore)
//
// Avance 3: errores semánticos de la regla Asignación de tipo.
//   - curso es string y se le asigna un int.
//   - edad es int y se le asigna un string.
//   cd backend && python probar_semantico.py ../algoritmos/algoritmo1_errorsem2.go -u AndreewCore

package main

import "fmt"

type Estudiante struct {
	nombre string
	edad   int
}

func (e Estudiante) Mostrar() {
	fmt.Println("Nombre:", e.nombre, "Edad:", e.edad)
}

func (e Estudiante) Nombre() string {
	return e.nombre
}

func notaDe(notas map[string]float64, nombre string) float64 {
	return notas[nombre]
}

func main() {
	var curso string = 2026
	var edad int
	var activo bool = true
	var notas map[string]float64 = map[string]float64{"Ana": 9.5, "Luis": 8.0}
	var ana Estudiante = Estudiante{nombre: "Ana", edad: 20}

	fmt.Println("Curso:", curso)
	fmt.Print("Ingresa tu edad: ")
	fmt.Scan(&edad)
	edad = "veinte"

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
