/** Fases del análisis y textos del tutor (explicación + fragmento de PLY). */

export const PHASES = [
  {id:'lex', name:'Léxico'},
  {id:'syn', name:'Sintáctico'},
  {id:'sem', name:'Semántico'}
];

export const TUTOR = {
  lex:{
    title:'Análisis léxico',
    short:'Agrupa caracteres en tokens: palabras reservadas, identificadores, números y operadores.',
    body:'El analizador léxico lee el código carácter por carácter y forma tokens. No le importa si el programa tiene sentido; solo reconoce las piezas. Si encuentra algo que no encaja con ninguna regla, reporta un error léxico.',
    cap:'Así se define en PLY (ply.lex):',
    ply:
`reserved = {'func': 'FUNC', 'var': 'VAR', 'for': 'FOR'}

t_DEFINE = r':='

def t_ID(t):
    r'[A-Za-z_]\\w*'
    t.type = reserved.get(t.value, 'ID')
    return t`
  },
  syn:{
    title:'Análisis sintáctico',
    short:'Comprueba que los tokens sigan la gramática de Go y construye el árbol sintáctico.',
    body:'El parser recibe la secuencia de tokens y verifica que siga las reglas de la gramática. Si encajan, construye el árbol sintáctico (AST), que muestra cómo se anidan declaraciones, sentencias y expresiones.',
    cap:'Una regla de gramática en PLY (ply.yacc):',
    ply:
`def p_for_stmt(p):
    'for_stmt : FOR simple_stmt SEMICOLON expr SEMICOLON simple_stmt block'
    p[0] = ('ForStmt', p[2], p[4], p[6], p[7])`
  },
  sem:{
    title:'Análisis semántico',
    short:'Revisa el significado: variables declaradas, ámbitos y tipos compatibles.',
    body:'Con el árbol listo se revisa el significado del programa: que cada variable esté declarada antes de usarse y que los tipos sean compatibles. Durante este recorrido se llena la tabla de símbolos.',
    cap:'Una comprobación sobre el AST, en Python:',
    ply:
`def revisar_asignacion(nodo, tabla):
    simbolo = tabla.buscar(nodo.nombre)
    if simbolo is None:
        error(f"'{nodo.nombre}' no está declarado")
    elif simbolo.tipo != nodo.valor.tipo:
        error("tipos incompatibles en la asignación")`
  }
};
