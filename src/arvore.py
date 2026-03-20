from abc import ABC, abstractmethod

# nós de expressão 

class Exp(ABC):
    @abstractmethod
    def avaliar(self, env):
        """Avalia a expressão dado um dicionário env {nome: valor}."""
        pass

    @abstractmethod
    def __str__(self):
        pass

class Const(Exp):
    def __init__(self, valor):
        self.valor = int(valor)

    def avaliar(self, env):
        return self.valor

    def __str__(self):
        return str(self.valor)

class Var(Exp):
    """Referência a uma variável pelo nome."""
    def __init__(self, nome):
        self.nome = nome

    def avaliar(self, env):
        if self.nome not in env:
            raise Exception(f"Variável não declarada: '{self.nome}'")
        return env[self.nome]

    def __str__(self):
        return self.nome

class OpBin(Exp):
    def __init__(self, op, esq, dir):
        self.op  = op
        self.esq = esq
        self.dir = dir

    def avaliar(self, env):
        ve = self.esq.avaliar(env)
        vd = self.dir.avaliar(env)
        if self.op == '+': return ve + vd
        if self.op == '-': return ve - vd
        if self.op == '*': return ve * vd
        if self.op == '/': return ve // vd
        raise Exception(f"Operador desconhecido: {self.op}")

    def __str__(self):
        return f"({self.esq} {self.op} {self.dir})"

# nós de programa 

class Decl:
    """Declaração:  nome = exp ;"""
    def __init__(self, nome, exp):
        self.nome = nome
        self.exp  = exp

    def __str__(self):
        return f"{self.nome} = {self.exp};"

class Programa:
    """Raiz da AST: lista de declarações + expressão de resultado."""
    def __init__(self, declaracoes, resultado):
        self.declaracoes = declaracoes  # list[Decl]
        self.resultado   = resultado    # Exp

    def __str__(self):
        linhas = [str(d) for d in self.declaracoes]
        linhas.append(f"= {self.resultado}")
        return "\n".join(linhas)
