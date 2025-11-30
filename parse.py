import sys
from typing import Type
from lex import *


class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter
        self.currentToken = None
        self.peekToken = None
        self.symbols = set()
        self.labelSymbols = set()
        self.gotoSymbols = set()
        self.nextToken()
        self.nextToken()

    def checkToken(self, kind):
        return self.currentToken.kind == kind

    def checkPeek(self, kind):
        return self.peekToken.kind == kind

    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.currentToken.kind.name)
        self.nextToken()

    def nextToken(self):
        self.currentToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    def abort(self, message):
        sys.exit("Error. " + message)

    def program(self):
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(void){")

        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        while not self.checkToken(TokenType.EOF):
            self.statement()

        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")

        for label in self.gotoSymbols:
            if label not in self.labelSymbols:
                self.abort("Attempting to GOTO to undeclared label: " + label)

    def statement(self):
        if self.checkToken(TokenType.PRINT):
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                self.emitter.emitLine('printf("' + self.currentToken.text + '\\n");')
                self.nextToken()
            else:
                self.emitter.emit('printf("%' + '.2f\\n", (float)(')
                self.expression()
                self.emitter.emitLine("));")

        elif self.checkToken(TokenType.IF):
            self.nextToken()
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine("){")

            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            self.emitter.emitLine("}")

        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine("){")

            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emitLine("}")

        elif self.checkToken(TokenType.LABEL):
            self.nextToken()
            if self.currentToken.text in self.labelSymbols:
                self.abort(f"Duplicate delcaration of LABEL {self.currentToken.text}")

            self.emitter.emitLine(self.currentToken.text + ":")
            self.match(TokenType.IDENT)

        elif self.checkToken(TokenType.GOTO):
            self.nextToken()
            self.gotoSymbols.add(self.currentToken.text)
            self.emitter.emitLine("goto " + self.currentToken.text + ";")
            self.match(TokenType.IDENT)

        elif self.checkToken(TokenType.LET):
            self.nextToken()
            if self.currentToken.text not in self.symbols:
                self.symbols.add(self.currentToken.text)
                self.emitter.headerLine("float " + self.currentToken.text + ";")
            self.emitter.emit(self.currentToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            self.emitter.emitLine(";")

        elif self.checkToken(TokenType.INPUT):
            self.nextToken()

            if self.currentToken.text not in self.symbols:
                self.symbols.add(self.currentToken.text)
                self.emitter.headerLine("float " + self.currentToken.text + ";")

            self.emitter.emitLine(
                'if(0 == scanf("%' + 'f", &' + self.currentToken.text + ")) {"
            )
            self.emitter.emitLine(self.currentToken.text + " = 0;")
            self.emitter.emit('scanf("%')
            self.emitter.emitLine('*s");')
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)
        else:
            self.abort(
                "Invalid statement at "
                + self.currentToken.text
                + " ("
                + self.currentToken.kind.name
                + ")"
            )

        self.nl()

    def nl(self):
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    def comparison(self):
        self.expression()

        if self.isComparisonOperator():
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
            self.expression()

        while self.isComparisonOperator():
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
            self.expression()

    def expression(self):
        self.term()

        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
            self.term()

    def term(self):
        self.unary()

        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
            self.unary()

    def unary(self):
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
        self.primary()

    def primary(self):
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            if self.currentToken.text not in self.symbols:
                self.abort(
                    "Referencing variable before assignment: " + self.currentToken.text
                )

            self.emitter.emit(self.currentToken.text)
            self.nextToken()
        else:
            self.abort("Unexpected token at " + self.currentToken.text)

    def isComparisonOperator(self):
        return (
            self.checkToken(TokenType.GT)
            or self.checkToken(TokenType.GTEQ)
            or self.checkToken(TokenType.LT)
            or self.checkToken(TokenType.LTEQ)
            or self.checkToken(TokenType.EQEQ)
            or self.checkToken(TokenType.NOTEQ)
        )
