// Algoritmo de prueba 3 — Samuel Echeverría (SamuelEcheverria)
//
// Programa Go con la mayoría de tokens del subconjunto de GoTutor, usado
// como entrada para validar el analizador. Para generar el log léxico:
//   cd backend && python probar_lexico.py ../algoritmos/algoritmo3.go -u SamuelEcheverria
//
// TODO(SamuelEcheverria): escribir el algoritmo.

package main

import "fmt"

/* calcularBalance procesa los precios de una lista de ventas,
   calcula el ingreso bruto, el promedio y verifica si se superó la meta. */
func calcularBalance(ventas []float64, meta float64) (float64,float64,bool){
	var bruto float64 = 0.0
	metaAlcanzada := false

	for _, monto := range ventas {
		bruto += monto
		if monto >= meta {
			metaAlcanzada = true
		}
	}

	promedio := bruto / float64(len(ventas))
	return bruto, promedio, metaAlcanzada
}

func main(){
	var cajero string = "Samuel"
	var turno int
	const IMPUESTO = 0.15

	ventas := []float64{120.50 , 85.25, 210.0, 45.75}
	lotes := [3]int{10, 5, 8}
	stock := map[string]int{"Teclado": 15, "Mouse": 4}

	fmt.Println("Ingrese el número de turno: ")
	fmt.Scan(&turno)

	bruto, promedio, exito := calcularBalance(ventas, 200.0)
	unidades := 0

	for i := 0; i < 3; i++ {
		unidades += lotes[i]
	}

	unidades -= 3
	unidades *= 2
	unidades /= 2
	unidades++
	unidades--

	recargo := bruto * IMPUESTO
	neto := bruto + recargo

	if neto >= 400.0 && exito || unidades > 20 {
		fmt.Printf("Cajero %s cierra con neto alto: %f\n", cajero, neto)
	} else if promedio <= 50.0 || !exito {
		fmt.Println("Ventas por debajo de la meta")
	} else {
		fmt.Println("Cierre de caja estándar")
	}

	switch stock["Mouse"] % 2 {
	case 0:
		fmt.Println("Stock par de Mouse:", stock["Teclado"])
	case 1:
		fmt.Println("Stock impar de Mouse")
	default:
		fmt.Println("Revisión manual", -turno, turno != 1, turno < 5)
	}

	for unidades > 0{
		unidades = unidades -1 + (0*2)
		if unidades == 5{
			continue
		}
		if unidades == 1{
			break
		}
	}
	turno++


}