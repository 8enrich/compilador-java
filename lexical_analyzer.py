from keywords import keywords
from operators import operators
from delimitators import delimitators
import regex

EOB = '\0'

class LexicalAnalyzer:

    def __init__(self, filename: str, buffer_size: int = 5):

        self.token_table = []
        self.symbol_table = {}
        self.file = open(filename, mode='r')
        self.begin_pointer = self.forward_pointer = (0, 0)
        self.buffers = ["", ""]
        self.lexeme = ""
        self.eof = False
        self.BUFFER_SIZE = buffer_size
        for i in range(2):
            self.data = self.file.read(self.BUFFER_SIZE - 1)
            self.eof = self.eof or len(self.data) < self.BUFFER_SIZE - 1
            self.buffers[i] = self.data + EOB

    def set_begin_pointer(self):
        self.lexeme = ""
        self.begin_pointer = self.forward_pointer

    def current_char(self) -> str:
        return self.buffers[self.forward_pointer[0]][self.forward_pointer[1]]

    def end_of_buffer(self, step: int = 0):
        return self.forward_pointer[1] + step >= len(self.buffers[self.forward_pointer[0]])

    def get_next_char(self) -> str: 
        if self.end_of_buffer(1):
            return self.buffers[1 - self.forward_pointer[0]][0]
        return self.buffers[self.forward_pointer[0]][self.forward_pointer[1] + 1]

    def advance(self):

        current_buffer = self.forward_pointer[0]
        char = self.current_char()

        self.lexeme += char

        self.forward_pointer = (current_buffer, self.forward_pointer[1] + 1)
        if self.buffers[current_buffer][self.forward_pointer[1]] != EOB: return

        self.forward_pointer = (1 - current_buffer, 0)
        self.data = self.file.read(self.BUFFER_SIZE - 1)
        if not self.data:
            self.buffers[current_buffer] = ""

        if self.eof: return

        self.eof = self.eof or len(self.data) < self.BUFFER_SIZE - 1

        self.buffers[current_buffer] = self.data + EOB

    def end_of_file(self):
        return self.eof and not self.buffers[0] and not self.buffers[1] or (self.buffers[0] == EOB or self.buffers[1] == EOB)

    def get_lexeme(self) -> str:
        return self.lexeme

    def analyze(self):

        while not self.end_of_file():
            
            char = self.current_char()

            if self.is_whitespace(char):
                self.advance()
                self.set_begin_pointer()
                continue

            if self.is_identifier_or_keyword_start(char):
                self.read_identifier_or_keyword()
                continue

            if self.is_digit(char):
                self.read_number()
                continue

            if self.is_char(char):
                self.read_char()
                continue

            if self.is_string(char):
                self.read_string()
                continue

            if self.is_operator_or_comment(char):
                self.read_operator_or_comment()
                continue

            if self.is_delimitator(char):
                self.read_delimitator()
                continue

            self.create_error_token(char)
        
        return self.token_table, self.symbol_table,
        

    def is_identifier_or_keyword_start(self, char: str):
        return regex.match("[A-Za-z_]", char)

    def is_identifier_or_keyword(self, char: str):
        return regex.match("[A-Za-z0-9_]", char)

    def is_digit(self, char: str):
        return regex.match("[0-9]", char)

    def is_char(self, char: str):
        return char == "'"

    def is_string(self, char: str):
        return char == '"'

    def is_operator_or_comment(self, char: str):
        return char in "+-=*&|!></%"

    def is_delimitator(self, char: str):
        return char in delimitators

    def is_whitespace(self, char: str):
        return char in " \n\t\r"

    def read_identifier_or_keyword(self):
        while not self.end_of_file() and self.is_identifier_or_keyword(self.current_char()): self.advance()
        lexeme = self.get_lexeme()
        if lexeme in keywords:
            self.create_token("KEYWORD", lexeme)
            return
        self.create_token("IDENTIFIER", lexeme)

    def read_number(self):
        while not self.end_of_file() and self.is_digit(self.current_char()): self.advance()
        if self.current_char() == ".":
            return self.read_float()
        if self.current_char() not in "+-*/%; )":
            while not self.end_of_file() and self.current_char() not in "+-*/%; ": self.advance()
            lexeme = self.get_lexeme()
            self.create_error_token(lexeme)
            return
        
        lexeme = self.get_lexeme()
        self.create_token("INT", lexeme, int(lexeme))

    def read_float(self):
        self.advance()
        while not self.end_of_file() and self.is_digit(self.current_char()): self.advance()
        lexeme = self.get_lexeme()
        if lexeme[-1] == ".": 
            self.create_error_token(lexeme)
            return
        self.create_token("FLOAT", lexeme, float(lexeme))

    def read_operator_or_comment(self):
        char = self.current_char()
        next_char = self.get_next_char()
        if char == "/" and (next_char == "/" or next_char == "*"):
            return self.ignore_comment()
        return self.read_operator()

    def ignore_comment(self):
        char = self.current_char()
        next_char = self.get_next_char()
        if char == "/" and next_char == "*":
            return self.ignore_multiline_comment()
        while not self.end_of_file() and self.current_char() != "\n": self.advance()

    def ignore_multiline_comment(self):
        closed = False
        while not self.end_of_file():
            char = self.current_char()
            next_char = self.get_next_char()
            self.advance()
            if char == "*" and next_char == "/":
                self.advance()
                closed = True
                break
        if not closed:
            self.create_error_token(self.get_lexeme())

    def read_operator(self):
        char = self.current_char()
        next_char = self.get_next_char()
        if char + next_char in operators:
            lexeme = char + next_char
            self.advance()
            self.advance()
            self.create_token("OPERATOR", lexeme)
            return
        lexeme = char
        self.advance()
        self.create_token("OPERATOR", lexeme)

    def read_delimitator(self):
        char = self.current_char()
        lexeme = char
        self.advance()
        self.create_token("DELIMITATOR", lexeme)

    def read_char(self):
        quote = 0
        while not self.end_of_file():
            if quote == 2:
                break
            if self.current_char() == "'":
                quote += 1
            self.advance()
        lexeme = self.get_lexeme()
        if len(lexeme) <= 2:
            self.create_error_token(self.get_lexeme())
            return
        if len(lexeme) > 3 and lexeme[1] != "\\" or lexeme[2] not in "btnfr\"'\\":
            self.create_error_token(self.get_lexeme())
            return
        self.create_token("CHAR", lexeme, lexeme[1:-1])

    def read_string(self):
        double_quote = 0
        while not self.end_of_file():
            if double_quote == 2:
                break
            char = self.current_char()
            if char == "\\":
                self.advance()
            if char == '"':
                double_quote += 1
            if char == "\n":
                self.create_error_token(self.get_lexeme())
                return
            self.advance()
        lexeme = self.get_lexeme()
        self.create_token("STRING", lexeme, lexeme[1:-1])

    def create_token(self, token_type: str, lexeme: str, attribute = None):
        if token_type == "IDENTIFIER":
            data = self.symbol_table.get(lexeme, {"occurrences": 0, "index": len(self.symbol_table)})
            occurrences = data["occurrences"]
            index = data["index"]
            self.symbol_table[lexeme] = {"occurrences": occurrences + 1, "index": index}
            attribute = index
        self.token_table.append((token_type, lexeme, attribute))
        self.set_begin_pointer()

    def create_error_token(self, lexeme: str):
        self.create_token("ERROR", lexeme) 
