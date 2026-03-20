import sys
import os

raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(raiz, 'src'))

from lexer import Lexer
from parser import Parser
from semantico import AnalisadorSemantico
from gerador import GeradorCodigo

# helpers 

def compilar_str(codigo):
    """Compila uma string de código EV e retorna (programa, asm)."""
    tokens   = Lexer(codigo).listar_tokens()
    programa = Parser(tokens).parse()
    AnalisadorSemantico().analisar(programa)
    asm = GeradorCodigo().gerar(programa)
    return programa, asm

def testar_valor(nome, codigo, esperado):
    """Testa se a expressão de resultado avalia para o valor esperado."""
    print(f"  '{nome}'")
    try:
        tokens   = Lexer(codigo).listar_tokens()
        programa = Parser(tokens).parse()
        AnalisadorSemantico().analisar(programa)
        # avaliação: executa declarações em ordem, depois resultado
        env = {}
        for decl in programa.declaracoes:
            env[decl.nome] = decl.exp.avaliar(env)
        resultado = programa.resultado.avaliar(env)
        if resultado == esperado:
            print(f"    [OK] => {resultado}")
            return True
        print(f"    [FALHA] esperado {esperado}, obtido {resultado}")
        return False
    except Exception as e:
        print(f"    [ERRO] {e}")
        return False

def testar_asm(nome, codigo, trechos):
    """Testa se o assembly gerado contém os trechos esperados."""
    print(f"  '{nome}'")
    try:
        _, asm = compilar_str(codigo)
        ok = True
        for t in trechos:
            if t not in asm:
                print(f"    [FALHA] trecho ausente: '{t}'")
                ok = False
        if ok:
            print(f"    [OK]")
        return ok
    except Exception as e:
        print(f"    [ERRO] {e}")
        return False

def testar_erro(nome, codigo, tipo_erro=""):
    """Testa se o código causa um erro (léxico, sintático ou semântico)."""
    print(f"  '{nome}'")
    try:
        tokens   = Lexer(codigo).listar_tokens()
        programa = Parser(tokens).parse()
        AnalisadorSemantico().analisar(programa)
        print(f"    [FALHA] deveria ter gerado erro")
        return False
    except Exception as e:
        if tipo_erro and tipo_erro.lower() not in str(e).lower():
            print(f"    [FALHA] tipo de erro errado: {e}")
            return False
        print(f"    [OK] erro detectado: {e}")
        return True

# testes 

def executar_testes():
    print("=" * 60)
    print("  TESTES AUTOMATIZADOS — Compilador EV (Atividade 09)")
    print("=" * 60)
    total = 0
    ok    = 0

    # 1. Programas sem variáveis 
    print("\n[1] Programas sem variáveis (compatibilidade EC2)")
    casos = [
        ("Constante simples",      "= 42",              42),
        ("Soma sem parênteses",    "= 7 + 11",          18),
        ("Precedência",            "= 7 + 5 * 3",       22),
        ("Associatividade",        "= 10 - 3 - 2",       5),
        ("Expressão EC1 PDF",      "= 33 + 912 * 11", 10065),
    ]
    for c in casos:
        r = testar_valor(c[0], c[1], c[2]); total += 1; ok += r

    # 2. Declaração e uso de variáveis 
    print("\n[2] Declaração e uso de variáveis")
    casos = [
        ("Variável simples",
         "x = 42;\n= x",
         42),
        ("Perímetro do retângulo (PDF)",
         "l = 30;\nc = 40;\n= l + l + c + c",
         140),
        ("Programa completo do PDF",
         "x = (7 + 4) * 12;\ny = x * 3 + 11;\n= (x * y) + (x * 11) + (y * 13)",
         60467),
        ("Variável usada em expressão",
         "a = 10;\nb = a * 2 + 5;\n= b - a",
         15),
        ("Encadeamento de variáveis",
         "a = 3;\nb = a * a;\nc = b + a;\n= c * 2",
         24),
        ("Var usada em precedência",
         "x = 4;\n= x + x * 2",
         12),   # x + (x*2) = 4 + 8 = 12
    ]
    for c in casos:
        r = testar_valor(c[0], c[1], c[2]); total += 1; ok += r

    # 3. Assembly gerado com variáveis 
    print("\n[3] Geração de Assembly com variáveis")
    casos_asm = [
        ("Seção .bss declarada",
         "x = 5;\n= x",
         [".section .bss", ".lcomm x, 8"]),
        ("mov %rax, var após declaração",
         "x = 5;\n= x",
         ["mov %rax, x"]),
        ("mov var, %rax para leitura",
         "x = 5;\n= x",
         ["mov x, %rax"]),
        ("Duas variáveis na .bss",
         "x = 3;\ny = 7;\n= x + y",
         [".lcomm x, 8", ".lcomm y, 8"]),
        ("Sem .bss se não há variáveis",
         "= 42",
         [".section .text"]),
    ]
    for c in casos_asm:
        r = testar_asm(c[0], c[1], c[2]); total += 1; ok += r

    # 4. Erros semânticos — variáveis não declaradas 
    print("\n[4] Detecção de variáveis não declaradas (erro semântico)")
    casos_err_sem = [
        ("Variável não declarada na expressão de resultado",
         "= x",               "semântico"),
        ("Variável usada antes da sua declaração",
         "x = 7 + y;\ny = 3;\n= x",  "semântico"),
        ("Variável z nunca declarada",
         "x = 1;\n= x + z",  "semântico"),
        ("Todas as variáveis do exemplo do PDF",
         "x = 7 + y;\ny = x * 11;\n= x * y + z", "semântico"),
    ]
    for c in casos_err_sem:
        r = testar_erro(c[0], c[1], c[2]); total += 1; ok += r

    # 5. Erros léxicos e sintáticos 
    print("\n[5] Detecção de erros léxicos e sintáticos")
    casos_err_lex = [
        ("Caractere inválido",        "= 3 + @2",      "léxico"),
        ("Falta ponto-e-vírgula",     "x = 5\n= x",   "sintático"),
        ("Falta expressão de resultado", "x = 5;",     ""),
        ("Número começando expressão de atribuição",
         "3 = 5;\n= 3",  "sintático"),
    ]
    for c in casos_err_lex:
        r = testar_erro(c[0], c[1], c[2]); total += 1; ok += r

    # resultado 
    print("\n" + "=" * 60)
    print(f"  Resultado: {ok}/{total} testes passaram.")
    print("=" * 60)

if __name__ == "__main__":
    executar_testes()
