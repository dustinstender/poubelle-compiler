import enum


class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    # Keywords.
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    # Operators.
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211


class Token:
    def __init__(self, token_text, token_kind):
        self.text = token_text  # The token's actual text. Used for identifiers, strings, and numbers.
        self.kind = token_kind  # The TokenType that this token is classified as.

    @staticmethod
    def checkIfKeyword(token_text):
        for kind in TokenType:
            if kind.name == token_text and kind.value >= 100 and kind.value < 200:
                return kind
        return None


class Lexer:
    def __init__(self, source):
        self.source = (
            source + "\n"
        )  # Source code to lex as a string. Append a newline to simplify lexing/parsing the last token/statement.
        self.cur_char = ""  # Current character in the string.
        self.cur_pos = -1  # Current position in the string.
        self.next_char()

    # Process the next character.
    def next_char(self):
        self.cur_pos += 1
        if self.cur_pos >= len(self.source):
            self.cur_char = "\0"  # EOF
        else:
            self.cur_char = self.source[self.cur_pos]

    # Return the lookahead character.
    def peek(self):
        if self.cur_pos + 1 >= len(self.source):
            return "\0"
        return self.source[self.cur_pos + 1]

    # Invalid token found, print error message and exit.
    def abort(self, message):
        print("Lexing error. " + message)

    # Skip whitespace except newlines, which we will use to indicate the end of a statement.
    def skip_whitespace(self):
        while self.cur_char == " " or self.cur_char == "\t" or self.cur_char == "\r":
            self.next_char()

    # Skip comments in the code.
    def skip_comment(self):
        if self.cur_char == "#":
            while self.cur_char != "\n":
                self.next_char()

    # Return the next token.
    def get_token(self):
        self.skip_whitespace()
        self.skip_comment()
        token = None
        # Check the first character of this token to see if we can decide what it is.
        # If it is a multiple character operator (e.g., !=), number, identifier, or keyword then we will process the rest.
        if self.cur_char == "+":
            token = Token(self.cur_char, TokenType.PLUS)
        elif self.cur_char == "-":
            token = Token(self.cur_char, TokenType.MINUS)
        elif self.cur_char == "*":
            token = Token(self.cur_char, TokenType.ASTERISK)
        elif self.cur_char == "/":
            token = Token(self.cur_char, TokenType.SLASH)
        elif self.cur_char == "=":
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.EQEQ)
            else:
                token = Token(self.cur_char, TokenType.EQ)
        elif self.cur_char == ">":
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.GTEQ)
            else:
                token = Token(self.cur_char, TokenType.GT)
        elif self.cur_char == "<":
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.LTEQ)
            else:
                token = Token(self.cur_char, TokenType.LT)
        elif self.cur_char == "!":
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())
        elif self.cur_char == '"':
            # Get all characters in between the string
            self.next_char()
            starting_position = self.cur_pos

            while self.cur_char != '"':
                # Deal with special characters now because it will complicate things during compilation.
                if (
                    self.cur_char == "\r"
                    or self.cur_char == "\n"
                    or self.cur_char == "\t"
                    or self.cur_char == "\\"
                    or self.cur_char == "%"
                ):
                    self.abort("Illegal character in string.")
                self.next_char()
            token_text = self.source[starting_position : self.cur_pos]
            token = Token(token_text, TokenType.STRING)
        elif self.cur_char.isdigit():
            starting_position = self.cur_pos
            while self.peek().isdigit():
                self.next_char()
            if self.peek() == ".":
                self.next_char()

                if not self.peek().isdigit():
                    self.abort("this is not a number")
                while self.peek().isdigit():
                    self.next_char()
            token_text = self.source[starting_position : self.cur_pos + 1]
            token = Token(token_text, TokenType.NUMBER)
        # Identifier
        elif self.cur_char.isalpha():
            starting_position = self.cur_pos
            while self.peek().isalnum():
                self.next_char()
            # Check that the identifier is not a key word.
            token_text = self.source[starting_position : self.cur_pos + 1]
            keyword = Token.checkIfKeyword(token_text)
            if keyword is None:
                token = Token(token_text, TokenType.IDENT)
            else:
                token = Token(token_text, keyword)
        elif self.cur_char == "\n":
            token = Token(self.cur_char, TokenType.NEWLINE)
        elif self.cur_char == "\0":
            token = Token(self.cur_char, TokenType.EOF)
        else:
            # Unknown token!
            self.abort("Unknown token: " + self.cur_char)

        self.next_char()
        return token
