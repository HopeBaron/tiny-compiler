import enum
import sys


class Lexer:
    def __init__(self, source):
        self.source = source
        self.position = -1
        self.current = None
        self.size = len(source)
        self.nextChar()

    def nextChar(self):
        next_char = self.position + 1
        if next_char >= self.size:
            self.current = "\0"
            return self.current
        self.position = next_char
        self.current = self.source[self.position]

    def peek(self):
        next_char = self.position + 1
        if next_char >= self.size:
            return "\0"
        return self.source[next_char]

    def abort(self, message):
        sys.exit("Lexer Aborted: " + message)

    def skipWhitespace(self):
        while self.current == " " or self.current == "\t" or self.current == "\r":
            self.nextChar()

    def skipComment(self):
        if self.current == "#":
            while self.current != "\n":
                self.nextChar()

    def getToken(self):
        token = None
        self.skipWhitespace()
        self.skipComment()
        current_character = self.current
        next_character = self.peek()
        if current_character == "\0":
            token = Token(current_character, TokenType.EOF)
        if current_character == ">" and next_character == "=":
            token = Token(current_character + next_character, TokenType.GTEQ)
        if current_character == "<" and next_character == "=":
            token = Token(current_character + next_character, TokenType.LTEQ)

        if current_character == "=" and next_character == "=":
            token = Token(current_character + next_character, TokenType.EQEQ)
        if current_character == "!" and next_character == "=":
            token = Token(current_character + next_character, TokenType.NOTEQ)
        if current_character == "=":
            token = Token(current_character, TokenType.EQ)
        if current_character == ">":
            token = Token(current_character, TokenType.GT)
        if current_character == "<":
            token = Token(current_character, TokenType.LT)
        if current_character == "+":
            token = Token(current_character, TokenType.PLUS)
        if current_character == "-":
            token = Token(current_character, TokenType.MINUS)
        if current_character == "*":
            token = Token(current_character, TokenType.ASTERISK)
        if current_character == "/":
            token = Token(current_character, TokenType.SLASH)
        if current_character == "\n":
            token = Token(current_character, TokenType.NEWLINE)
        if current_character == '"':
            # Get characters between quotations.
            self.nextChar()
            startPos = self.position

            while self.current != '"':
                # Don't allow special characters in the string. No escape characters, newlines, tabs, or %.
                # We will be using C's printf on this string.
                if (
                    self.current == "\r"
                    or self.current == "\n"
                    or self.current == "\t"
                    or self.current == "\\"
                    or self.current == "%"
                ):
                    self.abort("Illegal character in string.")
                self.nextChar()

            string_content = self.source[startPos : self.position]  # Get the substring.
            token = Token(string_content, TokenType.STRING)

        if current_character.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            startPos = self.position
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == ".":  # Decimal!
                self.nextChar()

                # Must have at least one digit after decimal.
                if not self.peek().isdigit():
                    # Error!
                    self.abort("Illegal character in number.")
                while self.peek().isdigit():
                    self.nextChar()

            number_content = self.source[
                startPos : self.position + 1
            ]  # Get the substring.
            token = Token(number_content, TokenType.NUMBER)
        if current_character.isalpha():
            # Leading character is a letter, so this must be an identifier or a keyword.
            # Get all consecutive alpha numeric characters.
            startPos = self.position
            while self.peek().isalnum():
                self.nextChar()

            # Check if the token is in the list of keywords.
            tokText = self.source[startPos : self.position + 1]  # Get the substring.
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None:  # Identifier
                token = Token(tokText, TokenType.IDENT)
            else:  # Keyword
                token = Token(tokText, keyword)
        if token is None:
            self.abort("Unknown Token:")
        self.nextChar()
        return token


class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText
        self.kind = tokenKind

    @staticmethod
    def checkIfKeyword(tokenText):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None


class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3

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
