// Algoritmo de prueba 1 — Paúl Rodríguez (AndreewCore)
//
// Avance 2: prueba solo las reglas sintácticas de AndreewCore.
//   - Variable con tipo (var x T y var x T = valor)
//   - for condicional y for infinito
//   - map (literal, tipo de parámetro y acceso por clave)
//   - Función con un retorno
//   - fmt: impresión y lectura (fmt.Scan(&x))
//   - Acceso por índice
//   - Struct (propiedades) y métodos con receptor
// `func main()` es la única regla ajena (función sin retorno, SamuelEcheverria).
//   cd backend && python probar_sintactico.py ../algoritmos/algoritmo1.go -u AndreewCore

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
