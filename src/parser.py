from lexer import TokenType, Token
from arvore import Const, Var, OpBin, Decl, Programa

class Parser:
    """
    Parser descendente recursivo para a linguagem EV.

    Gramática EV:
        <programa> ::= <decl>* <result>
        <decl>     ::= <ident> '=' <exp> ';'
        <result>   ::= '=' <exp>
        <exp>      ::= <exp_m> (('+' | '-') <exp_m>)*
        <exp_m>    ::= <prim>  (('*' | '/') <prim>)*
        <prim>     ::= <num> | <ident> | '(' <exp> ')'

    Precedência e associatividade herdadas de EC2.
    """

    def __init__(self, tokens):
        self.tokens  = tokens
        self.pos     = 0
        self.tamanho = len(tokens)

    # navegação 

    def token_atual(self):
        if self.pos < self.tamanho:
            return self.tokens[self.pos]
        return Token(TokenType.EOF, "EOF", -1)

    def consumir(self, tipo_esperado):
        tok = self.token_atual()
        if tok.tipo == tipo_esperado:
            self.pos += 1
            return tok
        raise Exception(
            f"Erro Sintático: esperado '{tipo_esperado}', "
            f"encontrado '{tok.tipo}' ('{tok.lexema}') na posição {tok.posicao}"
        )

    def avancar(self):
        tok = self.token_atual()
        self.pos += 1
        return tok

    # regras da gramática 

    def parse(self):
        """Ponto de entrada — analisa um programa EV completo."""
        if not self.tokens or self.tokens[0].tipo == TokenType.EOF:
            return None
        return self.programa()

    def programa(self):
        """
        <programa> ::= <decl>* <result>

        Enquanto o próximo token for IDENT, analisa uma declaração.
        Quando for IGUAL, analisa a expressão de resultado.
        """
        declaracoes = []

        while self.token_atual().tipo == TokenType.IDENT:
            declaracoes.append(self.decl())

        self.consumir(TokenType.IGUAL)
        resultado = self.exp_a()

        tok_final = self.token_atual()
        if tok_final.tipo != TokenType.EOF:
            raise Exception(
                f"Erro Sintático: tokens sobrando a partir da posição {tok_final.posicao}"
            )

        return Programa(declaracoes, resultado)

    def decl(self):
        """
        <decl> ::= <ident> '=' <exp> ';'
        """
        tok_nome = self.consumir(TokenType.IDENT)
        self.consumir(TokenType.IGUAL)
        exp = self.exp_a()
        self.consumir(TokenType.PONTO_VIR)
        return Decl(tok_nome.lexema, exp)

    def exp_a(self):
        """
        <exp> ::= <exp_m> (('+' | '-') <exp_m>)*
        """
        esq = self.exp_m()
        while self.token_atual().tipo in (TokenType.SOMA, TokenType.SUB):
            op  = self.avancar()
            dir = self.exp_m()
            esq = OpBin(op.lexema, esq, dir)
        return esq

    def exp_m(self):
        """
        <exp_m> ::= <prim> (('*' | '/') <prim>)*
        """
        esq = self.prim()
        while self.token_atual().tipo in (TokenType.MULT, TokenType.DIV):
            op  = self.avancar()
            dir = self.prim()
            esq = OpBin(op.lexema, esq, dir)
        return esq

    def prim(self):
        """
        <prim> ::= <num> | <ident> | '(' <exp> ')'
        """
        tok = self.token_atual()

        if tok.tipo == TokenType.NUMERO:
            self.consumir(TokenType.NUMERO)
            return Const(tok.lexema)

        if tok.tipo == TokenType.IDENT:
            self.consumir(TokenType.IDENT)
            return Var(tok.lexema)

        if tok.tipo == TokenType.PAREN_ESQ:
            self.consumir(TokenType.PAREN_ESQ)
            no = self.exp_a()
            self.consumir(TokenType.PAREN_DIR)
            return no

        raise Exception(
            f"Erro Sintático: início de expressão inválido "
            f"'{tok.lexema}' na posição {tok.posicao}"
        )
