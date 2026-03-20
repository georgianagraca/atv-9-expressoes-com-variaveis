from arvore import Const, Var, OpBin, Programa

class GeradorCodigo:
    """
    Gerador de código Assembly para a linguagem EV.

    Processo:
        1. Seção .bss — uma diretiva .lcomm por variável declarada (8 bytes cada).
        2. Seção .text — código para cada declaração seguido de mov %rax, <var>.
        3. Código para a expressão de resultado.
        4. Chamadas a imprime_num e sair.

    A geração de expressões usa a estratégia de pilha.
    """

    def gerar(self, programa):
        bss   = self._gerar_bss(programa.declaracoes)
        texto = self._gerar_texto(programa)
        return bss + texto

    # seção BSS 

    def _gerar_bss(self, declaracoes):
        if not declaracoes:
            return ""
        linhas = ["    .section .bss"]
        for decl in declaracoes:
            linhas.append(f"    .lcomm {decl.nome}, 8")
        linhas.append("")
        return "\n".join(linhas) + "\n"

    # seção TEXT 

    def _gerar_texto(self, programa):
        corpo = ""

        # código de cada declaração
        for decl in programa.declaracoes:
            corpo += f"    # {decl.nome} = {decl.exp};\n"
            corpo += self.gerar_exp(decl.exp)
            corpo += f"    mov %rax, {decl.nome}\n"

        # código da expressão de resultado
        corpo += f"    # = {programa.resultado}\n"
        corpo += self.gerar_exp(programa.resultado)

        return (
            "    .section .text\n"
            "    .globl _start\n"
            "\n"
            "_start:\n"
            f"{corpo}\n"
            "    call imprime_num\n"
            "    call sair\n"
            "\n"
            '    .include "asm/runtime.s"\n'
        )

    # geração de expressões

    def gerar_exp(self, no):
        """
        Gera código para um nó de expressão usando a estratégia de pilha.
        Para nós Var, emite mov <nome>, %rax.
        """
        codigo = ""

        if isinstance(no, Const):
            codigo += f"    mov ${no.valor}, %rax\n"

        elif isinstance(no, Var):
            codigo += f"    mov {no.nome}, %rax\n"

        elif isinstance(no, OpBin):
            # avalia direito primeiro, empilha, depois avalia esquerdo
            codigo += self.gerar_exp(no.dir)
            codigo += "    push %rax\n"
            codigo += self.gerar_exp(no.esq)
            codigo += "    pop %rbx\n"

            if no.op == '+':
                codigo += "    add %rbx, %rax\n"
            elif no.op == '-':
                codigo += "    sub %rbx, %rax\n"
            elif no.op == '*':
                codigo += "    imul %rbx, %rax\n"
            elif no.op == '/':
                codigo += "    cqo\n"
                codigo += "    idiv %rbx\n"

        return codigo
