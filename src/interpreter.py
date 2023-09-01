from enum import Enum

# HELPERS


def make_error(message, line, col):
    return Exception(f"{message} [{line}:{col}]")


# TOKENS


class TokenType(Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULT = "MULT"
    DIV = "DIV"
    EQUAL = "EQUAL"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"


class Token:
    def __init__(
        self,
        type,
        value=None,
        start_pos_line=None,
        start_pos_col=None,
        end_pos_line=None,
        end_pos_col=None,
    ):
        self.type = type
        self.value = value

        self.start_pos_line = start_pos_line
        self.start_pos_col = start_pos_col

        if end_pos_line:
            self.end_pos_line = end_pos_line
        else:
            self.end_pos_line = start_pos_line
        if end_pos_col:
            self.end_pos_col = end_pos_col
        else:
            self.end_pos_col = start_pos_col

    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return str(self.type)


def _check_character(char):
    return char != " " and char != "\t"


# LEXER


class Lexer:
    def __init__(self, code: str):
        self.code = code

        self.line = 0
        self.col = 0

        self.pos = -1

    def make_token(self, type, value=None):
        return Token(type, value, self.line, self.col)

    def advance(self):
        if self.pos + 1 < len(self.code):
            if self.code[self.pos] == "\n":
                self.line += 1
                self.col = 0
            else:
                self.col += 1

            self.pos += 1

            return True
        return False

    def check_current_pos(self):
        if _check_character(self.code[self.pos]):
            if self.code[self.pos].isdigit() or self.code[self.pos] == "-":
                start_pos_line = self.line
                start_pos_col = self.col
                num = str(self.code[self.pos])
                is_float = False
                while self.advance():
                    if self.code[self.pos].isdigit():
                        num += self.code[self.pos]
                    elif self.code[self.pos] == ".":
                        num += "."
                        is_float = True
                    else:
                        self.pos -= 1
                        break
                if num == "-":
                    self.tokens.append(self.make_token(TokenType.MINUS))
                elif is_float:
                    self.tokens.append(
                        Token(
                            TokenType.FLOAT,
                            float(num),
                            start_pos_line,
                            start_pos_col,
                            self.line,
                            self.col,
                        )
                    )
                else:
                    self.tokens.append(
                        Token(
                            TokenType.INT,
                            int(num),
                            start_pos_line,
                            start_pos_col,
                            self.line,
                            self.col,
                        )
                    )
            elif self.code[self.pos] == "+":
                self.tokens.append(self.make_token(TokenType.PLUS))
            elif self.code[self.pos] == "*":
                self.tokens.append(self.make_token(TokenType.MULT))
            elif self.code[self.pos] == "/":
                self.tokens.append(self.make_token(TokenType.DIV))
            elif self.code[self.pos] == "=":
                self.tokens.append(self.make_token(TokenType.EQUAL))
            elif self.code[self.pos] == "(":
                self.tokens.append(self.make_token(TokenType.LPAREN))
            elif self.code[self.pos] == ")":
                self.tokens.append(self.make_token(TokenType.RPAREN))
            else:
                raise make_error(
                    f"Illegal character: {self.code[self.pos]}", self.line, self.col
                )

    def tokenize(self):
        self.tokens = []

        while self.advance():
            self.check_current_pos()

        self.tokens.append(self.make_token(TokenType.EOF))

        return self.tokens


# NODES


class Node:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return str(self.token)


class BinOpNode(Node):
    def __init__(self, left_node, token, right_node):
        Node.__init__(self, token)

        self.left_node = left_node
        self.right_node = right_node

    def __repr__(self):
        return f"({self.left_node}, {Node.__repr__(self)}, {self.right_node})"


class UnaryOpNode(Node):
    def __init__(self, token, node):
        Node.__init__(self, token)
        self.node = node

    def __repr__(self):
        return f"({Node.__repr__(self)}, {self.node})"


# PARSER


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens

    def advance(self):
        if self.pos + 1 < len(self.tokens):
            self.pos += 1
            return True
        return False

    def factor(self):
        token = self.tokens[self.pos]

        if token.type in (TokenType.PLUS, TokenType.MINUS):
            self.advance()
            return UnaryOpNode(token, self.factor())
        elif token.type in (TokenType.INT, TokenType.FLOAT):
            self.advance()
            return Node(token)
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.expr()
            token = self.tokens[self.pos]
            if token.type == TokenType.RPAREN:
                self.advance()
                return expr
            else:
                raise make_error(
                    "Expected )", token.start_pos_line, token.start_pos_col
                )

    def bin_op(self, func, ops):
        left = func()

        while self.tokens[self.pos].type in ops:
            op_token = self.tokens[self.pos]
            self.advance()
            left = BinOpNode(left, op_token, func())

        return left

    def term(self):
        return self.bin_op(self.factor, (TokenType.MULT, TokenType.DIV))

    def expr(self):
        return self.bin_op(self.term, (TokenType.PLUS, TokenType.MINUS))

    def parse(self):
        self.line = 0
        self.col = 0

        self.pos = 0

        expr = self.expr()

        token = self.tokens[self.pos]
        if token.type != TokenType.EOF:
            raise make_error(
                "Unexpected ')'"
                if token.type == TokenType.RPAREN
                else "Expected '+', '-', '*' or '/'",
                token.start_pos_line,
                token.start_pos_col,
            )

        return expr


# RUN


def run(code):
    # Make tokens
    tokens = Lexer(code).tokenize()
    print(tokens)

    # Generate AST
    ast = Parser(tokens).parse()
    print(ast)


run("-8 - 2.3")
