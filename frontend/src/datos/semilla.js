/** Programas de muestra para el primer uso en modo invitado (localStorage vacío). */
const DAY = 864e5;

export const semilla = () => [
  {
    id:'s-fibo', name:'Tarea 1: Fibonacci', created:Date.now() - 5 * DAY, updated:Date.now() - 2 * DAY,
    notes:'El árbol de la llamada recursiva debería tener dos CallExpr dentro del BinaryExpr. Preguntar en clase si el parser de PLY los evalúa de izquierda a derecha.',
    files:[{name:'main.go', code:
`package main

import "fmt"

func fibonacci(n int) int {
	if n < 2 {
		return n
	}
	return fibonacci(n-1) + fibonacci(n-2)
}

func main() {
	for i := 0; i < 10; i++ {
		fmt.Println(fibonacci(i))
	}
}
`}]
  },
  {
    id:'s-prom', name:'Práctica: promedio de notas', created:Date.now() - DAY, updated:Date.now() - 3 * 36e5, notes:'',
    files:[{name:'main.go', code:
`package main

import "fmt"

func main() {
	notas := []float64{8.5, 9.0, 7.25}
	suma := 0.0
	for _, n := range notas {
		suma += n
	}
	promedio := suma / float64(len(notas))
	fmt.Println("Promedio:", promedio)
}
`}]
  }
];
