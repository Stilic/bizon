from __future__ import annotations
from enum import Enum

# HELPERS


def make_error(message: str, line: int, col: int):
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
        type: TokenType,
        value=None,
        start_pos_line: int = None,
        start_pos_col: int = None,
        end_pos_line: int = None,
        end_pos_col: int = None,
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


def _check_character(char: str):
    return char != " " and char != "\t"


# LEXER


class Lexer:
    def __init__(self, code: str):
        self.code = code

        self.line = 0
        self.col = 0

        self.pos = -1

    def make_token(self, type: TokenType, value=None):
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
            if self.code[self.pos].isdigit():
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
                if is_float:
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
            elif self.code[self.pos] == "-":
                self.tokens.append(self.make_token(TokenType.MINUS))
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


class NumberNode:
    def __init__(self, token: Token):
        self.token = token

        self.start_pos_line = token.start_pos_line
        self.start_pos_col = token.start_pos_col
        self.end_pos_col = token.end_pos_col
        self.end_pos_line = token.end_pos_line

    def __repr__(self):
        return str(self.token)


class BinOpNode(NumberNode):
    def __init__(self, left_node: NumberNode, token: Token, right_node: NumberNode):
        NumberNode.__init__(self, token)

        self.left_node = left_node
        self.right_node = right_node

        self.start_pos_line = left_node.start_pos_line
        self.start_pos_col = left_node.start_pos_col
        self.end_pos_col = right_node.end_pos_col
        self.end_pos_line = right_node.end_pos_line

    def __repr__(self):
        return f"({self.left_node}, {NumberNode.__repr__(self)}, {self.right_node})"


class UnaryOpNode(NumberNode):
    def __init__(self, token: Token, node: NumberNode):
        NumberNode.__init__(self, token)

        self.node = node

        self.start_pos_line = token.start_pos_line
        self.start_pos_col = token.start_pos_col
        self.end_pos_col = node.end_pos_col
        self.end_pos_line = node.end_pos_line

    def __repr__(self):
        return f"({NumberNode.__repr__(self)}, {self.node})"


# PARSER


class Parser:
    def __init__(self, tokens: list[Token]):
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
            return NumberNode(token)
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

    def bin_op(self, func, ops: list[TokenType]):
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


# VALUES


class Number:
    def __init__(self, value: float):
        self.value = value
        self.set_pos()

    def set_pos(
        self,
        start_pos_line: int = None,
        start_pos_col: int = None,
        end_pos_line: int = None,
        end_pos_col: int = None,
    ) -> Number:
        self.start_pos_line = start_pos_line
        self.start_pos_col = start_pos_col
        self.end_pos_line = end_pos_line
        self.end_pos_col = end_pos_col
        return self

    def added_to(self, other: Number) -> Number:
        if isinstance(other, Number):
            return Number(self.value + other.value)

    def subbed_by(self, other: Number) -> Number:
        if isinstance(other, Number):
            return Number(self.value - other.value)

    def multed_by(self, other: Number) -> Number:
        if isinstance(other, Number):
            return Number(self.value * other.value)

    def dived_by(self, other: Number) -> Number:
        if isinstance(other, Number):
            return Number(self.value / other.value)

    def __repr__(self) -> str:
        return str(self.value)


# INTERPRETER

NEGATIVE_ONE = Number(-1)


class Interpreter:
    def visit(self, node: NumberNode) -> Number:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    def visit_NumberNode(self, node: NumberNode):
        return Number(node.token.value).set_pos(
            node.start_pos_line,
            node.start_pos_col,
            node.end_pos_line,
            node.end_pos_col,
        )

    def visit_BinOpNode(self, node: BinOpNode):
        left = self.visit(node.left_node)
        right = self.visit(node.right_node)

        if node.token.type == TokenType.PLUS:
            left = left.added_to(right)
        elif node.token.type == TokenType.MINUS:
            left = left.subbed_by(right)
        elif node.token.type == TokenType.MULT:
            left = left.multed_by(right)
        elif node.token.type == TokenType.DIV:
            left = left.dived_by(right)

        return left.set_pos(
            node.start_pos_line,
            node.start_pos_col,
            node.end_pos_line,
            node.end_pos_col,
        )

    def visit_UnaryOpNode(self, node: UnaryOpNode):
        number = self.visit(node.node)

        if node.token.type == TokenType.MINUS:
            number = number.multed_by(NEGATIVE_ONE)

        return number.set_pos(
            node.start_pos_line,
            node.start_pos_col,
            node.end_pos_line,
            node.end_pos_col,
        )


# RUN


def run(code):
    # Make tokens
    tokens = Lexer(code).tokenize()

    # Generate AST
    ast = Parser(tokens).parse()

    interp = Interpreter()
    return interp.visit(ast)


print(run("1+"))
