from enum import Enum


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


class Lexer:
    def __init__(self, code: str):
        self.code = code

    def advance(self):
        if self.code[self.pos] == "\n":
            self.line += 1
            self.col = 0
        else:
            self.col += 1

        self.pos += 1

    def check_current_pos(self):
        if _check_character(self.code[self.pos]):
            if self.code[self.pos].isdigit():
                num = self.code[self.pos]
                is_float = False
                check_next_token = False
                self.advance()
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
                if check_next_token:
                    self.check_current_pos()
                if is_float:
                    self.tokens.append(Token(TokenType.FLOAT, float(num)))
                else:
                    self.tokens.append(Token(TokenType.INT, int(num)))
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

        self.pos = 0

        self.tokens = []

        while True:
            self.check_current_pos()
            if self.pos < len(self.code):
                self.advance()
            else:
                break

        return self.tokens


lexer = Lexer("1.17 + 9")
print(lexer.tokenize())
