from arvore import Programa, Decl, Const, Var, OpBin

class AnalisadorSemantico:
    """
    Etapa de análise semântica da linguagem EV.

    Percorre a AST verificando se toda variável usada foi declarada
    anteriormente. Utiliza uma tabela de símbolos (dict) que mapeia
    nome → True conforme as variáveis vão sendo declaradas.

    Regra da linguagem EV:
        - Uma variável só pode ser usada após sua declaração.
        - A expressão de resultado pode usar todas as variáveis declaradas.
        - Referência a variável não declarada é um erro semântico.
    """

    def __init__(self):
        self.tabela = {}   # tabela de símbolos: {nome: True}

    def analisar(self, programa):
        """
        Recebe o nó Programa da AST e verifica todas as declarações
        e a expressão de resultado. Lança Exception em caso de erro.
        """
        # verifica cada declaração em ordem
        for decl in programa.declaracoes:
            self._verificar_exp(decl.exp)          # expressão deve usar só vars já declaradas
            self.tabela[decl.nome] = True           # após verificação, adiciona à tabela

        # verifica a expressão de resultado
        self._verificar_exp(programa.resultado)

    def _verificar_exp(self, no):
        """Percorre recursivamente um nó de expressão verificando variáveis."""
        if isinstance(no, Const):
            return

        if isinstance(no, Var):
            if no.nome not in self.tabela:
                raise Exception(
                    f"Erro Semântico: variável '{no.nome}' usada antes de ser declarada"
                )
            return

        if isinstance(no, OpBin):
            self._verificar_exp(no.esq)
            self._verificar_exp(no.dir)
            return

        raise Exception(f"Nó desconhecido na AST: {type(no)}")
