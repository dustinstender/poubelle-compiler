import sys
from lex import *


# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()
        self.labels_declared = set()
        self.labels_go_to = set()

        self.current_token = None
        self.peek_token = None
        self.next_token()
        self.next_token()

    # Return true if the current token matches.
    def check_token(self, kind):
        return kind == self.current_token.kind

    # Return true if the next token matches.
    def check_peek(self, kind):
        return kind == self.peek_token.kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind):
        if not self.check_token(kind):
            self.abort("Expected " + kind.name + "got " + self.current_token.kind)
        self.next_token()

    # Advances the current token.
    def next_token(self):
        self.current_token = self.peek_token
        self.peek_token = self.lexer.get_token()

    def abort(self, message):
        sys.exit("Error. " + message)

    def program(self):
        print("Program")

        self.emitter.header_line("console.log('you are emitting something...')")

        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        while not self.check_token(TokenType.EOF):
            self.statement()

        for label in self.labels_go_to:
            if label not in self.labels_declared:
                self.abort("attemping to 'go-to' undeclared label:" + label)

    def is_comparison_operator(self):
        return (
            self.check_token(TokenType.GT)
            or self.check_token(TokenType.GTEQ)
            or self.check_token(TokenType.LT)
            or self.check_token(TokenType.LTEQ)
            or self.check_token(TokenType.EQEQ)
            or self.check_token(TokenType.NOTEQ)
        )

    def expression(self):
        self.term()

        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.term()

    def term(self):
        self.unary()

        while self.check_token(TokenType.ASTERISK) or self.check_token(TokenType.SLASH):
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.unary()

    def unary(self):
        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.current_token.text)
            self.next_token()
        self.primary()

    def primary(self):
        if self.check_token(TokenType.NUMBER):
            self.emitter.emit(self.current_token.text)
            self.next_token()
        elif self.check_token(TokenType.IDENT):
            # ensure the variable already exists
            if self.current_token.text not in self.symbols:
                self.abort(
                    "referencing a variable before assignment:"
                    + self.current_token.text
                )
            self.emitter.emit(self.current_token.text)
            self.next_token()
        else:
            self.abort("Unexpected token at " + self.current_token.text)

    def comparison(self):
        self.expression()

        if self.is_comparison_operator():
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.current_token.text)

        while self.is_comparison_operator():
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.comparison()

    def statement(self):
        if self.check_token(TokenType.PRINT):
            self.next_token()

            if self.check_token(TokenType.STRING):
                self.emitter.emit_line(
                    "console.log('" + self.current_token.text + "');"
                )
                self.next_token()
            else:
                self.emitter.emit("console.log(")
                self.expression()
                self.emitter.emit_line(");")

        elif self.check_token(TokenType.IF):
            self.next_token()
            self.emitter.emit("if (")
            self.comparison()

            self.match(TokenType.THEN)
            self.new_line()
            self.emitter.emit_line(") {")

            while not self.check_token(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            self.emitter.emit_line("}")

        elif self.check_token(TokenType.WHILE):
            self.next_token()
            self.emitter.emit("while (")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.new_line()
            self.emitter.emit_line(") {")

            while not self.check_token(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emit_line("}")

        elif self.check_token(TokenType.LABEL):
            self.next_token()

            if self.current_token.text in self.labels_declared:
                self.abort("label already exists")
            self.labels_declared.add(self.current_token.text)

            self.emitter.emit(self.current_token.text + ":")
            self.match(TokenType.IDENT)

        elif self.check_token(TokenType.GOTO):
            self.next_token()
            self.labels_go_to.add(self.current_token.text)
            self.emitter.emit("goto" + self.current_token.text + ";")
            self.match(TokenType.IDENT)

        elif self.check_token(TokenType.LET):
            self.next_token()

            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)
                self.emitter.emit("let ")

            self.emitter.emit(self.current_token.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            self.emitter.emit_line(";")

        elif self.check_token(TokenType.INPUT):
            self.next_token()

            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)
                self.emitter.emit_line("let " + self.current_token.text + ";")

            self.emitter.emit_line(
                self.current_token.text
                + " = prompt('Enter a value for "
                + self.current_token.text
                + ":');"
            )

            self.match(TokenType.IDENT)

        else:
            self.abort("invalid statement" + self.current_token.text)

        self.new_line()

    def new_line(self):
        self.match(TokenType.NEWLINE)

        while self.check_token(TokenType.NEWLINE):
            self.next_token()
