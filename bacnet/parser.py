import enum
import math

import logging


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
    SEMICOLON = ':'
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

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.read(skip_whitespace=True)

    def read(self, skip_whitespace=True):
        self.seek(self.pos + 1)
        if skip_whitespace:
            self.skip_whitespace()
        return self.current_char

    def seek(self, pos):
        self.pos = pos
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def tell(self):
        return self.pos


class TokenParser:
    def __init__(self, char_reader):
        """
        :param char_reader:
        :type char_reader: CharReader
        """
        self.next_parser = None
        self.char_reader = char_reader
        self.logger = logging.getLogger(__name__)

    def set_next_parser(self, next_parser):
        self.next_parser = next_parser

    def _integer(self):
        c = self.char_reader.read()
        value = ''
        while c is not None and c.isdigit():
            value += c
            c = self.char_reader.read()

    def parse_next_token(self):
        """
        Parse next token from char reader and return token or None
        """
        token_parser = self
        token = None
        pos = self.char_reader.tell()
        while token_parser is not None:
            token = token_parser._try_parse_next_token()
            if token is not None:
                break
            else:
                token_parser = token_parser.next_parser
                self.char_reader.seek(pos)
        return token

    def _try_parse_next_token(self):
        raise Exception("Unimplemented handle")


class AnyTokenParser(TokenParser):
    def __init__(self, char_reader):
        super().__init__(char_reader)

    def _try_parse_next_token(self):
        return Token(TokenType.ANY)


class NumberOrStringTokenParser(TokenParser):
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

    def _extract_string(self):
        c = self.char_reader.current_char
        if c is None:
            return ''

        starts_with_digit = c.isdigit()
        starts_with_minus = c == '-'
        value = ''
        if c.isalpha() or starts_with_digit or starts_with_minus:
            while c is not None and (c.isalpha() or c.isdigit() or c == '-' or c == '.'):
                value += c
                c = self.char_reader.read(skip_whitespace=False)
        return value

    def _try_parse_next_token(self):
        self.char_reader.skip_whitespace()
        value = self._extract_string()
        if len(value) == 0:
            return None

        # special keywords tokens
        probably_keyword = value.lower()
        if probably_keyword in self.keywords:
            return self.tokens[self.keywords.index(probably_keyword)]

        # check if token is number
        starts_with_minus = value.startswith('-')
        starts_with_digit = value[0].isdigit()
        if starts_with_digit or starts_with_minus:
            try:
                return Token(TokenType.NUMBER, float(value))
            except:
                return Token(TokenType.STRING, value)
        else:
            return Token(TokenType.STRING, value)


class QuotedStringTokenParser(TokenParser):

    def __init__(self, char_reader):
        super().__init__(char_reader)

    def _try_parse_next_token(self):
        self.char_reader.skip_whitespace()
        c = self.char_reader.current_char
        if not c == '"':
            return None
        value = "\""
        prev_c = '"'
        c = self.char_reader.read()
        while c is not None and not prev_c == '\\' and not c == '"':
            try:
                value += c
                prev_c = c
                c = self.char_reader.read(skip_whitespace=False)
            except:
                self.logger.debug("Failed parse quoted string, value: {}".format(value))
        value += '"'
        # move next char because current char is "
        self.char_reader.read(skip_whitespace=False)
        return Token(TokenType.STRING, value)


class IntegerTokenParser(NumberOrStringTokenParser):

    def _extract_integer(self):
        """
        :return: extract next string and parse it as integer value
        """
        value = self._extract_string()
        if len(value) == 0:
            return None
        if len(value) == 0:
            return None
        try:
            return int(value)
        except:
            return None

    def _try_parse_next_token(self):
        self.char_reader.skip_whitespace()
        value = self._extract_integer()
        if value is None:
            return None
        try:
            return Token(TokenType.NUMBER, value)
        except:
            return None


class HashTokenParser(IntegerTokenParser):
    def __init__(self, char_reader):
        super().__init__(char_reader)

    def _try_parse_next_token(self):
        self.char_reader.skip_whitespace()
        c = self.char_reader.current_char
        if not c == '#':
            return None
        # move char reader to next char
        c = self.char_reader.read()
        if c is None:
            return None

        value = self._extract_integer()
        if value is not None:
            return Token(TokenType.HASH, value)
        return Token


class PunctuationTokenParser(TokenParser):

    def __init__(self, char_reader):
        super().__init__(char_reader)

    def _try_parse_next_token(self):
        self.char_reader.skip_whitespace()
        c = self.char_reader.current_char
        token = None
        if c == ':':
            token = Token(TokenType.SEMICOLON)
        elif c == ',':
            token = Token(TokenType.COMMA)
        elif c == '{':
            token = Token(TokenType.OPEN_GROUP)
        elif c == '}':
            token = Token(TokenType.CLOSE_GROUP)
        elif c == '[':
            token = Token(TokenType.OPEN_BRACE)
        elif c == ']':
            token = Token(TokenType.CLOSE_BRACE)
        elif c == '(':
            token = Token(TokenType.OPEN_TUPLE)
        elif c == ')':
            token = Token(TokenType.CLOSE_TUPLE)
        if token is not None:
            # move to next
            self.char_reader.read()
        return token


class Tokenizer:
    def __init__(self, char_reader):
        self.char_reader = char_reader
        hash_token_parser = HashTokenParser(char_reader)
        number_or_string_token_parser = NumberOrStringTokenParser(char_reader)
        punctuation_parser = PunctuationTokenParser(char_reader)
        quoted_string_parser = QuotedStringTokenParser(char_reader)

        punctuation_parser.set_next_parser(hash_token_parser)
        hash_token_parser.set_next_parser(number_or_string_token_parser)
        number_or_string_token_parser.set_next_parser(quoted_string_parser)
        self.head_parser = punctuation_parser
        self.tokens = []

    def error(self):
        raise Exception('invalid character')

    def _get_next_token(self):
        return self.head_parser.parse_next_token()

    def tokenize(self):
        token = self._get_next_token()
        while token is not None:
            self.tokens.append(token)
            token = self._get_next_token()
        return self.tokens


class BACnetParser:
    def parse_bacrpm(self, text):
        char_reader = CharReader(text)
        tokenizer = Tokenizer(char_reader)
        tokens = tokenizer.tokenize()
        for token in tokens:
            print(token)
