import enum
import math
import logging
import bacnet

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

    def skip_whitespace(self, ignore_eol=True):
        while self.current_char is not None \
                and self.current_char.isspace() \
                and (self.current_char != '\n' or ignore_eol):
            self.read(skip_whitespace=True, ignore_eol=ignore_eol)

    def read(self, skip_whitespace=True, ignore_eol=True):
        self.seek(self.pos + 1)
        if skip_whitespace:
            self.skip_whitespace()
        return self.current_char

    def seek(self, pos):
        self.pos = pos
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

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
            Token(TokenType.NULL, None),
            Token(TokenType.TRUE, True),
            Token(TokenType.FALSE, False),
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


class WhitespaceTokenParser(TokenParser):

    def __init__(self, char_reader):
        super().__init__(char_reader)

    def _try_parse_next_token(self):
        self.char_reader.skip_whitespace(ignore_eol=False)
        c = self.char_reader.current_char
        if c is None:
            return None
        if c == '\n':
            self.char_reader.read(skip_whitespace=True, ignore_eol=False)
            return Token(TokenType.EOL, None)
        return None


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
        whitespace_parser = WhitespaceTokenParser(char_reader)

        whitespace_parser.set_next_parser(punctuation_parser)
        punctuation_parser.set_next_parser(hash_token_parser)
        hash_token_parser.set_next_parser(number_or_string_token_parser)
        number_or_string_token_parser.set_next_parser(quoted_string_parser)
        self.head_parser = whitespace_parser
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


class TokenReader:
    def __init__(self, tokens) -> None:
        super().__init__()
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def seek(self, pos):
        self.pos = pos
        self.current_token = self.tokens[self.pos] if len(self.tokens) < pos else None

    def tell(self):
        return self.pos

    def read(self):
        self.seek(self.pos + 1)
        return self.current_token


class EntityPairParser:

    def __init__(self, token_reader) -> None:
        """
        Entity pair parser trying to find
        key as tokens until semicolon
        value as rest of tokens until EOL
        :param token_reader:
        :type token_reader TokenReader
        """
        super().__init__()
        self.token_reader = token_reader
        self.next_parser = None

    def _extract_key(self):
        key = ""
        token = self.token_reader.current_token
        while token is not None and token.type != TokenType.SEMICOLON:
            key += str(token.value) if token.value is not None else ""
            token = self.token_reader.read()
        if token is not None and token.type == TokenType.SEMICOLON:
            # going to next after semicolon token
            self.token_reader.read()
        return key

    def _extract_value(self):
        value = ""
        token = self.token_reader.current_token
        while token is not None and token.type != TokenType.EOL:
            value += str(token.value) if token.value is not None else ""
            token = self.token_reader.read()
        if token is not None and token.type == TokenType.EOL:
            # going to next after EOL token
            self.token_reader.read()
        return value

    def _try_parse_next_entity(self):
        key = self._extract_key()
        if key == "":
            return None
        value = self._extract_value()
        if value == "":
            return None
        return [(key, value)]

    def parse_next_entity(self):
        parser = self
        while parser is not None:
            entity = parser._try_parse_next_entity()
            if entity is not None:
                return entity
            else:
                parser = parser.next_parser


class StringArrayParser(EntityPairParser):

    def __init__(self, token_reader):
        super().__init__(token_reader)

    def _extract_values(self):
        token = self.token_reader.current_token
        if token is None:
            return None
        opening_token_types = [TokenType.OPEN_TUPLE, TokenType.OPEN_BRACE, TokenType.OPEN_GROUP]
        closing_token_types = [TokenType.CLOSE_TUPLE, TokenType.CLOSE_BRACE, TokenType.CLOSE_GROUP]
        values = None
        if token.type in opening_token_types:
            values = []
            idx_opening_token_type = opening_token_types.index(token.type)
            while token is not None and token.type != closing_token_types[idx_opening_token_type]:
                # does not expect separate tokens described one entity
                if token.type == TokenType.STRING \
                        or token.type == TokenType.NUMBER \
                        or token.type == TokenType.TRUE \
                        or token.type == TokenType.FALSE \
                        or token.type == TokenType.NULL:
                    values.append(token.value)
                token = self.token_reader.read()
        return values

    def _try_parse_next_entity(self):
        key = self._extract_key()
        if key == "":
            return None
        values = self._extract_values()
        if values is None:
            return None
        if len(values) == 0:
            return None
        return [(key, values)]


class ObjectIdentifierParser(StringArrayParser):

    def __init__(self, token_parser):
        super().__init__(token_parser)

    def _try_parse_next_entity(self):
        key = self._extract_key()
        if not key == "object-identifier":
            return None
        values = self._extract_values()
        if values is None or len(values) != 2:
            return None
        return [
            ("object-type", values[0]),
            ("object-identifier", values[1])
        ]


class Entitynizer:

    def __init__(self, tokens):
        token_reader = TokenReader(tokens)

        # this settings can be encapsulated into Entitinizer?
        any_pair_parser = EntityPairParser(token_reader)
        array_parser = StringArrayParser(token_reader)
        object_identifier_parser = ObjectIdentifierParser(token_reader)
        object_identifier_parser.next_parser = array_parser
        array_parser.next_parser = any_pair_parser
        self._head_parser = object_identifier_parser
        self._entities = []

    def entitynize(self):
        entities = self._head_parser.parse_next_entity()
        while entities is not None:
            for entity in entities:
                self._entities.append(entity)
            entities = self._head_parser.parse_next_entity()
        return self._entities


class BACnetParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_bacrpm(self, text):
        char_reader = CharReader(text)
        tokenizer = Tokenizer(char_reader)
        tokens = tokenizer.tokenize()
        if self.logger.isEnabledFor(logging.DEBUG):
            idx = 0
            for token in tokens:
                self.logger.debug("[{}] {}".format(idx, token))
        entitynizer = Entitynizer(tokens)
        entities = entitynizer.entitynize()
        bacnet_object = {}
        for entity in entities:
            name = entity[0]
            value = entity[1]
            if name in bacnet.property.map:
                bacnet_object[bacnet.property.map[name]] = value
        return bacnet_object