from keywords import keywords
from operators import operators
from delimitators import delimitators
from sys import argv
import regex

EOB = '\0'
BUFFER_SIZE = 5

if len(argv) != 2:
    print(f"Uso: python3 {argv[0]} <java-file>")
    exit(1)

token_table = []
symbol_table = {}
filename = argv[1]
file = open(filename, mode='r')
begin_pointer = forward_pointer = (0, 0)
buffers = ["", ""]
lexeme = ""
eof = False
for i in range(2):
    data = file.read(BUFFER_SIZE - 1)
    eof = eof or len(data) < BUFFER_SIZE - 1
    buffers[i] = data + EOB

def set_begin_pointer():
    global begin_pointer, lexeme
    lexeme = ""
    begin_pointer = forward_pointer

def current_char() -> str:
    return buffers[forward_pointer[0]][forward_pointer[1]]

def end_of_buffer(step: int = 0):
    return forward_pointer[1] + step >= len(buffers[forward_pointer[0]])

def get_next_char() -> str: 
    if end_of_buffer(1):
        return buffers[1 - forward_pointer[0]][0]
    return buffers[forward_pointer[0]][forward_pointer[1] + 1]

def advance():
    global forward_pointer, lexeme, eof

    current_buffer = forward_pointer[0]
    char = current_char()

    lexeme += char

    forward_pointer = (current_buffer, forward_pointer[1] + 1)
    if buffers[current_buffer][forward_pointer[1]] != EOB: return

    forward_pointer = (1 - current_buffer, 0)
    data = file.read(BUFFER_SIZE - 1)
    if not data:
        buffers[current_buffer] = ""

    if eof: return

    eof = eof or len(data) < BUFFER_SIZE - 1

    buffers[current_buffer] = data + EOB

def end_of_file():
    return eof and not buffers[0] and not buffers[1] or (buffers[0] == EOB or buffers[1] == EOB)

def get_lexeme() -> str:
    return lexeme

def lexical_analyzer():

    while not end_of_file():
        
        char = current_char()

        if is_whitespace(char):
            advance()
            set_begin_pointer()
            continue

        if is_identifier_or_keyword_start(char):
            read_identifier_or_keyword()
            continue

        if is_digit(char):
            read_number()
            continue

        if is_char(char):
            read_char()
            continue

        if is_string(char):
            read_string()
            continue

        if is_operator_or_comment(char):
            read_operator_or_comment()
            continue

        if is_delimitator(char):
            read_delimitator()
            continue

        create_error_token(char)

def is_identifier_or_keyword_start(char: str):
    return regex.match("[A-Za-z_]", char)

def is_identifier_or_keyword(char: str):
    return regex.match("[A-Za-z0-9_]", char)

def is_digit(char: str):
    return regex.match("[0-9]", char)

def is_char(char: str):
    return char == "'"

def is_string(char: str):
    return char == '"'

def is_operator_or_comment(char: str):
    return char in "+-=*&|!></%"

def is_delimitator(char: str):
    return char in delimitators

def is_whitespace(char: str):
    return char in " \n\t\r"

def read_identifier_or_keyword():
    while not end_of_file() and is_identifier_or_keyword(current_char()): advance()
    lexeme = get_lexeme()
    if lexeme in keywords:
        create_token("KEYWORD", lexeme)
        return
    create_token("IDENTIFIER", lexeme)

def read_number():
    while not end_of_file() and is_digit(current_char()): advance()
    if current_char() == ".":
        return read_float()
    if current_char() not in "+-*/%; )":
        while not end_of_file() and current_char() not in "+-*/%; ": advance()
        lexeme = get_lexeme()
        create_error_token(lexeme)
        return
    
    lexeme = get_lexeme()
    create_token("INT", lexeme, int(lexeme))

def read_float():
    advance()
    while not end_of_file() and is_digit(current_char()): advance()
    lexeme = get_lexeme()
    if lexeme[-1] == ".": 
        create_error_token(lexeme)
        return
    create_token("FLOAT", lexeme, float(lexeme))

def read_operator_or_comment():
    char = current_char()
    next_char = get_next_char()
    if char == "/" and (next_char == "/" or next_char == "*"):
        return ignore_comment()
    return read_operator()

def ignore_comment():
    char = current_char()
    next_char = get_next_char()
    if char == "/" and next_char == "*":
        return ignore_multiline_comment()
    while not end_of_file() and current_char() != "\n": advance()

def ignore_multiline_comment():
    closed = False
    while not end_of_file():
        char = current_char()
        next_char = get_next_char()
        advance()
        if char == "*" and next_char == "/":
            advance()
            closed = True
            break
    if not closed:
        create_error_token(get_lexeme())

def read_operator():
    char = current_char()
    next_char = get_next_char()
    if char + next_char in operators:
        lexeme = char + next_char
        advance()
        advance()
        create_token("OPERATOR", lexeme)
        return
    lexeme = char
    advance()
    create_token("OPERATOR", lexeme)

def read_delimitator():
    char = current_char()
    lexeme = char
    advance()
    create_token("DELIMITATOR", lexeme)

def read_char():
    quote = 0
    while not end_of_file():
        if quote == 2:
            break
        if current_char() == "'":
            quote += 1
        advance()
    lexeme = get_lexeme()
    if len(lexeme) <= 2:
        create_error_token(get_lexeme())
        return
    if len(lexeme) > 3 and lexeme[1] != "\\" or lexeme[2] not in "btnfr\"'\\":
        create_error_token(get_lexeme())
        return
    create_token("CHAR", lexeme, lexeme[1:-1])

def read_string():
    double_quote = 0
    while not end_of_file():
        if double_quote == 2:
            break
        char = current_char()
        if char == "\\":
            advance()
        if char == '"':
            double_quote += 1
        if char == "\n":
            create_error_token(get_lexeme())
            return
        advance()
    lexeme = get_lexeme()
    create_token("STRING", lexeme, lexeme[1:-1])

def create_token(token_type: str, lexeme: str, attribute = None):
    if token_type == "IDENTIFIER":
        data = symbol_table.get(lexeme, {"occurrences": 0, "index": len(symbol_table)})
        occurrences = data["occurrences"]
        index = data["index"]
        symbol_table[lexeme] = {"occurrences": occurrences + 1, "index": index}
        attribute = index
    token_table.append((token_type, lexeme, attribute))
    set_begin_pointer()

def create_error_token(lexeme: str):
    create_token("ERROR", lexeme)
 
def main():
    lexical_analyzer()

main()
file.close()
for symbol, value in symbol_table.items():
    print(symbol, value)
print()
for token in token_table:
    print(token)
