# Compilador EV — Expressões com Variáveis

Compilador completo para a linguagem **EV**, que traduz programas com declaração e uso de variáveis para Assembly. Evolução direta do compilador EC2, adicionando análise léxica de identificadores, análise sintática de declarações, análise semântica com tabela de símbolos e geração de código com seção `.bss`.

---

## A Linguagem EV

Um programa EV é uma sequência de zero ou mais declarações de variáveis, seguida de uma expressão de resultado obrigatória.

**Exemplo:**
```
x = (7 + 4) * 12;
y = x * 3 + 11;
= (x * y) + (x * 11) + (y * 13)
```
Resultado: `60467`

**Regras:**
- Cada declaração tem a forma `nome = expressão ;`
- A expressão de resultado começa com `=` (sem nome de variável)
- Uma variável só pode ser usada após ter sido declarada
- Expressões seguem as mesmas regras de precedência e associatividade de EC2

---

## Gramática EV

```
<programa> ::= <decl>* <resultado>
<decl>     ::= <ident> '=' <exp> ';'
<resultado>::= '=' <exp>
<exp>      ::= <exp_m> (('+' | '-') <exp_m>)*
<exp_m>    ::= <prim>  (('*' | '/') <prim>)*
<prim>     ::= <num> | <ident> | '(' <exp> ')'
<ident>    ::= <letra> (<letra> | <digito>)*
<num>      ::= <digito>+
```

Precedência e associatividade idênticas à EC2: `*` e `/` antes de `+` e `-`, todos associando à esquerda.

---

## Estrutura do Projeto

```
atv-9-expressoes-com-variaveis/
├── asm/
│   └── runtime.s           # Funções auxiliares: imprime_num, sair
├── build/                  # Arquivos gerados (criado automaticamente)
│   ├── programa.s
│   ├── programa.o
│   └── executavel
├── src/
│   ├── lexer.py            # ★ Léxico EV: IDENT, IGUAL, PONTO_VIR
│   ├── arvore.py           # ★ AST EV: Var, Decl, Programa
│   ├── parser.py           # ★ Parser EV: programa, decl, exp_a, exp_m, prim
│   ├── semantico.py        # ★ Análise semântica: tabela de símbolos
│   ├── gerador.py          # ★ Geração de código: seção .bss + variáveis
│   └── compilador.py       # Ponto de entrada (CLI)
├── testes/
│   ├── programa.ev         # Exemplo completo do enunciado (resultado: 60467)
│   ├── perimetro.ev        # Perímetro de retângulo (resultado: 140)
│   ├── sem_variaveis.ev    # Apenas expressão de resultado (sem declarações)
│   ├── erro_variavel.ev    # Variáveis não declaradas — deve causar erro
│   └── testes.py           # Suite de testes automatizados
└── README.md
```

---

## O que mudou em relação à EC2

| Módulo | Alteração |
|---|---|
| `lexer.py` | Novos tokens: `IDENT`, `IGUAL`, `PONTO_VIR` |
| `arvore.py` | Novos nós: `Var` (referência), `Decl` (declaração), `Programa` (raiz) |
| `parser.py` | Novas funções: `programa()`, `decl()`; `prim()` reconhece `<ident>` |
| `semantico.py` | **Novo** — tabela de símbolos e verificação de variáveis |
| `gerador.py` | Gera seção `.bss`, `mov %rax, var` e `mov var, %rax` |
| `compilador.py` | Inclui a etapa de análise semântica no pipeline |

---

## Pré-requisitos

- Python 3.6+
- `as` e `ld` (GNU Binutils) — Linux x86-64

```bash
sudo apt install binutils
```

---

## Como Usar

### 1. Crie um arquivo `.ev`

```
l = 30;
c = 40;
= l + l + c + c
```

### 2. Compile para Assembly

Execute sempre a partir da **raiz do projeto**:

```bash
python3 src/compilador.py testes/perimetro.ev build/programa.s
```

### 3. Monte e Ligue

```bash
as --64 -o build/programa.o build/programa.s
ld -o build/executavel build/programa.o
```

### 4. Execute

```bash
./build/executavel
# Saída: 140
```

---

## Exemplos

### Programa com variáveis encadeadas

```bash
echo "x = (7 + 4) * 12;
y = x * 3 + 11;
= (x * y) + (x * 11) + (y * 13)" > testes/teste.ev

python3 src/compilador.py testes/teste.ev build/programa.s
as --64 -o build/programa.o build/programa.s
ld -o build/executavel build/programa.o
./build/executavel
# Saída: 60467
```

### Detectando variável não declarada

```bash
echo "x = 7 + y;
y = x * 11;
= x * y + z" > testes/erro.ev

python3 src/compilador.py testes/erro.ev build/programa.s
# ERRO DE COMPILAÇÃO: Erro Semântico: variável 'y' usada antes de ser declarada
```

---

## Como Rodar os Testes

```bash
python3 testes/testes.py
```

A suite cobre 5 categorias:

| # | Categoria | O que verifica |
|---|---|---|
| 1 | Sem variáveis | Compatibilidade com EC2 (precedência, associatividade) |
| 2 | Uso de variáveis | Declaração, leitura, encadeamento, uso em expressões |
| 3 | Assembly gerado | `.bss`, `.lcomm`, `mov %rax, var`, `mov var, %rax` |
| 4 | Erros semânticos | Variável usada antes de declarada, variável nunca declarada |
| 5 | Erros léxicos/sintáticos | Caractere inválido, falta de `;`, falta de `=` no resultado |

---
