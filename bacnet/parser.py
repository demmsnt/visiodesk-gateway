import enum
import math
import logging
from bacnet.bacnet import bacnet_name_map


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
            token = Token(TokenType.SEMICOLON, ':')
        elif c == ',':
            token = Token(TokenType.COMMA, ',')
        elif c == '{':
            token = Token(TokenType.OPEN_GROUP, '{')
        elif c == '}':
            token = Token(TokenType.CLOSE_GROUP, '}')
        elif c == '[':
            token = Token(TokenType.OPEN_BRACE, '[')
        elif c == ']':
            token = Token(TokenType.CLOSE_BRACE, ']')
        elif c == '(':
            token = Token(TokenType.OPEN_TUPLE, '(')
        elif c == ')':
            token = Token(TokenType.CLOSE_TUPLE, ')')
        if token is not None:
            # move to next
            self.char_reader.read()
        return token


class TokensAnalyzer:
    @staticmethod
    def open_close_idx(open_type, close_type, token_reader):
        """
        :param token_reader:
        :type token_reader TokenReader
        :return:
        """
        logger = logging.getLogger(__name__)
        pos = token_reader.tell()
        while token_reader.current_token is not None and token_reader.current_token.type != open_type:
            token = token_reader.read()
        open_idx = -1
        close_idx = -1
        opened = 0
        if token_reader.current_token is not None and token_reader.current_token.type == open_type:
            open_idx = token_reader.tell()
            opened = 1
            logger.debug("[{}] {} opened={}".format(token_reader.tell(), open_type, opened))
            token_reader.read()
        while token_reader.current_token is not None and opened != 0:
            if token_reader.current_token.type == close_type:
                opened -= 1
                logger.debug("[{}] {} opened={}".format(token_reader.tell(), token_reader.current_token.type, opened))
                if opened == 0:
                    # because ignore read next token before break
                    close_idx = token_reader.tell()
                    break
            if token_reader.current_token.type == open_type:
                opened += 1
                logger.debug("[{}] {} opened={}".format(token_reader.tell(), token_reader.current_token.type, opened))
            token_reader.read()
        # restore position before return
        token_reader.seek(pos)
        return open_idx, close_idx


class TokensExtractor:
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

    def extract_tokens(self):
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
        self.current_token = self.tokens[self.pos] if len(self.tokens) > pos else None

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
        self.logger = logging.getLogger(__name__)

    def _extract_key(self):
        key = []
        # alias for less typing
        tr = self.token_reader
        while tr.current_token is not None and tr.current_token.type != TokenType.SEMICOLON:
            if tr.current_token.value is not None:
                key.append(str(tr.current_token.value))
            self.token_reader.read()
        if tr.current_token is not None and tr.current_token.type == TokenType.SEMICOLON:
            # going to next after semicolon token
            self.token_reader.read()
        return " ".join(key)

    def _extract_value(self):
        value = ""
        # alias for less typing
        tr = self.token_reader
        while tr.current_token is not None and tr.current_token.type != TokenType.EOL:
            value += str(tr.current_token.value) if tr.current_token.value is not None else ""
            self.token_reader.read()
        if tr.current_token is not None and tr.current_token.type == TokenType.EOL:
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
        pos = self.token_reader.tell()
        while parser is not None:
            self.token_reader.seek(pos)
            entity = parser._try_parse_next_entity()
            if entity is not None:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug("entity: {}".format(entity))
                return entity
            else:
                parser = parser.next_parser


class StringArrayParser(EntityPairParser):

    def __init__(self, token_reader):
        super().__init__(token_reader)

    def _extract_values(self):
        tr = self.token_reader
        if tr.current_token is None:
            return None
        opening_token_types = [TokenType.OPEN_TUPLE, TokenType.OPEN_BRACE, TokenType.OPEN_GROUP]
        closing_token_types = [TokenType.CLOSE_TUPLE, TokenType.CLOSE_BRACE, TokenType.CLOSE_GROUP]
        values = None
        if tr.current_token.type in opening_token_types:
            values = []
            idx_opening_token_type = opening_token_types.index(tr.current_token.type)
            while tr.current_token is not None and tr.current_token.type != closing_token_types[idx_opening_token_type]:
                # does not expect separate tokens described one entity
                if tr.current_token.type == TokenType.STRING \
                        or tr.current_token.type == TokenType.NUMBER \
                        or tr.current_token.type == TokenType.TRUE \
                        or tr.current_token.type == TokenType.FALSE \
                        or tr.current_token.type == TokenType.NULL:
                    values.append(tr.current_token.value)
                self.token_reader.read()
            # going to next after closing token
            self.token_reader.read()
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


class PairsExtractor:

    def __init__(self, tokens):
        self.token_reader = TokenReader(tokens)

        # this settings can be encapsulated into Entitinizer?
        any_pair_parser = EntityPairParser(self.token_reader)
        array_parser = StringArrayParser(self.token_reader)
        object_identifier_parser = ObjectIdentifierParser(self.token_reader)
        object_identifier_parser.next_parser = array_parser
        array_parser.next_parser = any_pair_parser
        self._head_parser = object_identifier_parser
        self._entities = []

    def __find_begin_pairs_container(self):
        # find beginning of pairs container
        token = self.token_reader.current_token
        while token is not None and token.type != TokenType.OPEN_GROUP:
            token = self.token_reader.read()
        found = True if token is not None and token.type == TokenType.OPEN_GROUP else False
        if found:
            # going to next token
            self.token_reader.read()
        return found

    def extract_pairs(self):
        self._entities = []
        open_idx, close_idx = TokensAnalyzer.open_close_idx(TokenType.OPEN_GROUP,
                                                            TokenType.CLOSE_GROUP,
                                                            self.token_reader)
        if open_idx == -1 or close_idx == -1:
            return self._entities
        self.token_reader.seek(open_idx + 1)
        entities = self._head_parser.parse_next_entity()
        while entities is not None and self.token_reader.tell() <= close_idx:
            for entity in entities:
                self._entities.append(entity)
            entities = self._head_parser.parse_next_entity()
        return self._entities


class BACnetParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_bacrpm(self, text):
        char_reader = CharReader(text)
        tokens_extractor = TokensExtractor(char_reader)
        tokens = tokens_extractor.extract_tokens()

        if self.logger.isEnabledFor(logging.DEBUG):
            idx = 0
            for token in tokens:
                self.logger.debug("[{}] {}".format(idx, token))

        pairs_extractor = PairsExtractor(tokens)
        pairs = pairs_extractor.extract_pairs()
        bacnet_object = {}
        for entity in pairs:
            name = entity[0]
            value = entity[1]
            if name in bacnet_name_map:
                bacnet_object[bacnet_name_map[name]] = value
        return bacnet_object

    @staticmethod
    def parse_bacwi(text):
        """
        Parse text file format of address_cache
        return list of objects with fields: 'device_id', 'host', 'port', 'snet', 'sadr', 'apdu'
        example of file format
        ;Device   MAC (hex)            SNET  SADR (hex)           APDU
        ;-------- -------------------- ----- -------------------- ----
          200     0A:15:50:0C:BA:C0    0     00                   480
          300     0A:15:50:0D:BA:C0    0     00                   480
          400     0A:15:50:0E:BA:C0    0     00                   480
          500     0A:15:50:0F:BA:C0    0     00                   480
          600     0A:15:50:10:BA:C0    0     00                   480
        ;
        ; Total Devices: 5
        :return:
        """
        devices = []
        for line in text.split('\n'):
            trimmed = line.strip()
            if trimmed.startswith(';'):
                continue
            values = trimmed.split()
            mac = values[1].split(':')
            host = "{}.{}.{}.{}".format(int(mac[0], 16), int(mac[1], 16), int(mac[2], 16), int(mac[3], 16))
            port = int(mac[4] + mac[5], 16)
            device_id = int(values[0])
            apdu = int(values[4])
            devices.append({
                'device_id': device_id,
                'host': host,
                'port': port,
                'snet': 0,
                'sadr': '0',
                'apdu': apdu
            })
        return devices

    @staticmethod
    def create_bacwi(self, devices):
        # TODO implement it
        pass