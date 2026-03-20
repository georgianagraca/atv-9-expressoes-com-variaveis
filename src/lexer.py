import sys

class TokenType:
    # tokens herdados de EC2
    NUMERO      = "Numero"
    PAREN_ESQ   = "ParenEsq"
    PAREN_DIR   = "ParenDir"
    SOMA        = "Soma"
    SUB         = "Sub"
    MULT        = "Mult"
    DIV         = "Div"
    EOF         = "EOF"
    # novos tokens EV
    IDENT       = "Ident"        # nome de variável
    IGUAL       = "Igual"        # = (atribuição e início de resultado)
    PONTO_VIR   = "PontoVirgula" # ;

class Token:
    def __init__(self, tipo, lexema, posicao):
        self.tipo    = tipo
        self.lexema  = lexema
        self.posicao = posicao

    def __str__(self):
        return f'<{self.tipo}, "{self.lexema}", {self.posicao}>'

class Lexer:
    """
    Analisador léxico para a linguagem EV.

    Novos tokens em relação a EC2:
        IDENT       — sequência começando por letra, seguida de letras/dígitos
        IGUAL       — caractere '='
        PONTO_VIR   — caractere ';'

    Regra: sequência de letras/dígitos começando por dígito (ex: 3abc)
    continua sendo erro léxico.
    """

    def __init__(self, entrada):
        self.entrada  = entrada
        self.pos      = 0
        self.tamanho  = len(entrada)

    def erro(self, mensagem):
        raise Exception(f"Erro léxico na posição {self.pos}: {mensagem}")

    def proximo_token(self):
        while self.pos < self.tamanho:
            c = self.entrada[self.pos]

            # espaços e quebras de linha
            if c.isspace():
                self.pos += 1
                continue

            # número
            if c.isdigit():
                inicio = self.pos
                lexema = ""
                while self.pos < self.tamanho and self.entrada[self.pos].isdigit():
                    lexema += self.entrada[self.pos]
                    self.pos += 1
                return Token(TokenType.NUMERO, lexema, inicio)

            # identificador (letra seguida de letras/dígitos)
            if c.isalpha():
                inicio = self.pos
                lexema = ""
                while self.pos < self.tamanho and (
                    self.entrada[self.pos].isalpha() or
                    self.entrada[self.pos].isdigit()
                ):
                    lexema += self.entrada[self.pos]
                    self.pos += 1
                return Token(TokenType.IDENT, lexema, inicio)

            # símbolos de um caractere
            mapa = {
                '(': TokenType.PAREN_ESQ,
                ')': TokenType.PAREN_DIR,
                '+': TokenType.SOMA,
                '-': TokenType.SUB,
                '*': TokenType.MULT,
                '/': TokenType.DIV,
                '=': TokenType.IGUAL,
                ';': TokenType.PONTO_VIR,
            }
            if c in mapa:
                tok = Token(mapa[c], c, self.pos)
                self.pos += 1
                return tok

            self.erro(f"Caractere inválido '{c}'")

        return Token(TokenType.EOF, "EOF", self.pos)

    def listar_tokens(self):
        tokens = []
        while True:
            tok = self.proximo_token()
            tokens.append(tok)
            if tok.tipo == TokenType.EOF:
                break
        return tokens
