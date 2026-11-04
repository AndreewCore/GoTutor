/**
 * Programas de ejemplo de la vista Ejemplos.
 *
 * Los errores, el AST y la tabla de símbolos NO se guardan aquí: los calcula el
 * analizador real al abrir el ejemplo. `fase` y `linea` solo describen el error
 * que el ejemplo enseña, para la etiqueta y el fragmento de la tarjeta.
 */

export const STARTER = `package main

import "fmt"

func main() {
	// Escribe tu código aquí
	fmt.Println("Hola, GoTutor")
}
`;

export const LEVELS = [
  {id:'basico',     name:'Básico',     desc:'Errores que el lexer o el parser detectan a simple vista.'},
  {id:'intermedio', name:'Intermedio', desc:'Reglas de gramática y de tipos dentro de sentencias de control.'},
  {id:'avanzado',   name:'Avanzado',   desc:'Varios errores semánticos a la vez: tipos, ámbitos y funciones.'}
];

export const EXAMPLES = [
  {
    id:"suma", name:"Suma con errores de tipo", level:"avanzado", fase:"sem", linea:19,
    challenge:"Pasa las fases léxica y sintáctica, pero tiene 2 errores de significado en las líneas 19 y 20.",
    code:
`package main

import "fmt"

// sumar devuelve la suma de dos enteros
func sumar(a int, b int) int {
	return a + b
}

func main() {
	var total int = 0
	nombre := "Gopher"
	for i := 0; i < 5; i++ {
		total = sumar(total, i)
	}
	if total > 10 {
		fmt.Println(nombre, total)
	}
	total = "diez"
	fmt.Println(resultado)
}`
  },
  {
    id:"lexico", name:"Caracteres no válidos", level:"basico", fase:"lex", linea:7,
    challenge:"Dos fragmentos no se pueden convertir en tokens. El análisis se detiene en la primera fase.",
    code:
`package main

import "fmt"

func main() {
	precio := 25
	descuento := 5 @ 2
	mensaje := "Total:
	fmt.Println(precio - descuento)
}`
  },
  {
    id:"sintaxis", name:"Paréntesis y punto y coma", level:"intermedio", fase:"syn", linea:9,
    challenge:"Todos los tokens son válidos, pero su orden no sigue la gramática de Go en las líneas 8 y 10.",
    code:
`package main

import "fmt"

func main() {
	edad := 20
	if edad >= 18 {
		fmt.Println("Mayor de edad"
	}
	for i := 0; i < 3 i++ {
		fmt.Println(i)
	}
}`
  },
  {
    id:"llave", name:"Llave sin cerrar", level:"basico", fase:"syn", linea:7,
    challenge:"Un programa de 7 líneas al que le falta un solo carácter. El parser llega al final del archivo sin encontrarlo.",
    code:
`package main

import "fmt"

func main() {
	nombre := "Ana"
	fmt.Println("Hola,", nombre)
`
  },
  {
    id:"paridad", name:"Condición que no es bool", level:"intermedio", fase:"sem", linea:16,
    challenge:"El programa es válido hasta el análisis semántico. Una condición usa un tipo que Go no acepta en un if.",
    code:
`package main

import "fmt"

func esPar(n int) bool {
	return n % 2 == 0
}

func main() {
	contador := 0
	for i := 1; i <= 10; i++ {
		if esPar(i) {
			contador++
		}
	}
	if contador {
		fmt.Println("Hay pares")
	}
}`
  },
  {
    id:"ambitos", name:"Ámbitos y múltiples retornos", level:"avanzado", fase:"sem", linea:15,
    challenge:"Tres errores semánticos distintos: una variable sin usar, una variable fuera de su ámbito y una asignación con el número equivocado de valores.",
    code:
`package main

import "fmt"

func dividir(a float64, b float64) (float64, bool) {
	if b == 0 {
		return 0, false
	}
	return a / b, true
}

func main() {
	resultado, ok := dividir(10, 4)
	if ok {
		mensaje := "Resultado:"
	}
	fmt.Println(mensaje, resultado)
	var total float64 = dividir(8, 2)
	fmt.Println(total)
}`
  }
];


/** Busca un ejemplo por id. */
export const findExample = id => EXAMPLES.find(e => e.id === id);
