import enum
import math


class TokenType(enum.Enum):
    STRING = 'string'
    NUMBER = 'number'
    HASH = '#'
    OPEN_GROUP = '{'
    CLOSE_GROUP = '}'
    OPEN_TUPLE = '('
    CLOSE_TUPLE = ')'
    OPEN_BRACE = '['
    CLOSE_BRACE = ']'
    COMMA = ','
    SEMICOLON = ';'
    NULL = 'Null'
    QUOTE = '"'
    TRUE = 'true'
    FALSE = 'false'
    EOL = '\n'
    ANY = 'any'
    END_TOKEN = 'end'


class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=self.value
        )

    def __repr__(self):
        return self.__str__()


class CharReader:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def _skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.read()

    def read(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
        self._skip_whitespace()


class TokenParser:
    def __init__(self, char_reader):
        self.next_parser = None
        self.char_reader = char_reader

    def parse(self):
        pass

    def set_next_parser(self, next_parser):
        self.next_parser = next_parser

    def _integer(self):
        c = self.char_reader.read()
        value = ''
        while c is not None and c.isdigit():
            value += c
            c = self.char_reader.read()


class AnyTokenParser(TokenParser):
    def __init__(self, char_reader):
        super().__init__(char_reader)

    def handle(self, c):
        return Token(TokenType.ANY)


class HashTokenParser(TokenParser):
    def __init__(self, char_reader):
        super().__init__(char_reader)

    def handle(self, c):
        if not c == '#':
            return None

        return Token(TokenType.HASH, self._integer())


class NumberTokenParser(TokenParser):
    def __init__(self, char_reader):
        super().__init__(char_reader)
        self.keywords = ["null", "true", "false", "inf", "-inf"]
        self.tokens = [
            Token(TokenType.NULL),
            Token(TokenType.TRUE),
            Token(TokenType.FALSE),
            Token(TokenType.NUMBER, math.inf),
            Token(TokenType.NUMBER, -math.inf)
        ]

    def handle(self, c):
        starts_with_digit = c.isdigit()
        starts_with_minus = c is '-'
        if c.isalpha() or starts_with_digit or starts_with_minus:
            value = ''
            while c is not None and (c.isalpha() or c.isdigit() or c is '-' or c is '.'):
                value += c
                c = self.char_reader.read()

            # special keywords tokens
            value = value.lower()
            if value in self.keywords:
                return self.tokens[self.keywords.index(value)]

            if starts_with_digit or starts_with_minus:
                try:
                    return Token(TokenType.NUMBER, float(value))
                except:
                    return Token(TokenType.STRING, value)
        else:
            return None


class Tokenizer:
    def __init__(self, char_reader):
        self.char_reader = char_reader

    def error(self):
        raise Exception('invalid character')

    def get_next_token(self):
        pass
