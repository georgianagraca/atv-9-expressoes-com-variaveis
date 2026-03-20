import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from lexer import Lexer
from parser import Parser
from semantico import AnalisadorSemantico
from gerador import GeradorCodigo

def compilar(arquivo_entrada, arquivo_saida):
    try:
        with open(arquivo_entrada, 'r') as f:
            codigo_fonte = f.read()

        # 1. Análise Léxica
        lexer  = Lexer(codigo_fonte)
        tokens = lexer.listar_tokens()

        # 2. Análise Sintática
        parser  = Parser(tokens)
        programa = parser.parse()

        if not programa:
            print("Erro: programa vazio.")
            return

        # 3. Análise Semântica (verificação de variáveis)
        semantico = AnalisadorSemantico()
        semantico.analisar(programa)

        # 4. Geração de Código
        gerador          = GeradorCodigo()
        codigo_assembly  = gerador.gerar(programa)

        # 5. Salva no arquivo de saída
        destino = os.path.dirname(arquivo_saida)
        if destino:
            os.makedirs(destino, exist_ok=True)
        with open(arquivo_saida, 'w') as f:
            f.write(codigo_assembly)

        print(f"Compilação concluída! Saída: {arquivo_saida}")

    except Exception as e:
        print(f"ERRO DE COMPILAÇÃO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python src/compilador.py <arquivo.ev> <saida.s>")
        sys.exit(1)

    compilar(sys.argv[1], sys.argv[2])
