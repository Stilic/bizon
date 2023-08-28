from enum import Enum

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


class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

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
                num = self.code[self.pos]
                is_float = False
                check_next_token = False
                if self.advance():
                    while self.pos < len(self.code):
                        if self.code[self.pos] == ".":
                            if is_float:
                                continue
                            else:
                                num += "."
                                is_float = True
                            self.advance()
                        elif self.code[self.pos].isdigit():
                            num += self.code[self.pos]
                            self.advance()
                        else:
                            check_next_token = True
                            break
                    if is_float:
                        self.tokens.append(Token(TokenType.FLOAT, float(num)))
                    else:
                        self.tokens.append(Token(TokenType.INT, int(num)))
                    if check_next_token:
                        self.check_current_pos()
            elif self.code[self.pos] == "+":
                self.tokens.append(Token(TokenType.PLUS))
            elif self.code[self.pos] == "-":
                self.tokens.append(Token(TokenType.MINUS))
            elif self.code[self.pos] == "*":
                self.tokens.append(Token(TokenType.MULT))
            elif self.code[self.pos] == "/":
                self.tokens.append(Token(TokenType.DIV))
            elif self.code[self.pos] == "=":
                self.tokens.append(Token(TokenType.EQUAL))
            elif self.code[self.pos] == "(":
                self.tokens.append(Token(TokenType.LPAREN))
            elif self.code[self.pos] == ")":
                self.tokens.append(Token(TokenType.RPAREN))
            else:
                raise Exception(
                    f"Illegal character at {self.line}:{self.col} ({self.code[self.pos]})"
                )

    def tokenize(self):
        self.line = 0
        self.col = 0

        self.tokens = []
        self.pos = -1

        while self.advance():
            self.check_current_pos()

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
        return f"{self.left_node}, {Node.__repr__(self)}, {self.right_node}"


# PARSER


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens

    def advance(self):
        if self.pos + 1 < len(self.tokens):
            self.pos += 1
            return True
        return False

    def parse(self):
        self.ast = []
        self.pos = -1

        self.groups = [self.ast]

        while self.advance():
            token = self.tokens[self.pos]
            # TODO: redo the group parsing
            if token.type == TokenType.LPAREN:
                node = Node([])

                previous_node = self.groups[0][-1] if len(self.groups[0]) > 0 else None                
                print(previous_node)
                if type(previous_node) == BinOpNode:
                    previous_node.right_node = node
                else:
                    node.token.append(previous_node)
                    self.groups[0].append(node)

                self.groups.insert(0, node.token)
            elif token.type == TokenType.RPAREN:
                self.groups.pop(0)
            elif self.is_operator(token.type):
                self.groups[0].append(BinOpNode(Node(self.tokens[self.pos - 1]), token, Node(self.tokens[self.pos + 1])))

        return self.ast


# RUN


def run(code):
    # Make tokens
    tokens = Lexer(code).tokenize()
    print(tokens)

    # Generate AST
    ast = Parser(tokens).parse()
    print(ast)


run("(1.17) + 9 * (8 + 7)")
