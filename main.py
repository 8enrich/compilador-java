from keywords import keywords
from operators import operators
from delimitators import delimitators
from sys import argv
import regex

token_table = []
symbol_table = {}
filename = argv[1]
file = open(filename, mode='r')
source = file.read()
begin_pointer = forward_pointer = 0
EOF = "EOF"

def set_begin_pointer():
    global begin_pointer
    begin_pointer = forward_pointer

def current_char() -> str:
    if end_of_file():
        return EOF
    return source[forward_pointer]

def get_next_char() -> str: 
    if end_of_file(1):
        return EOF
    return source[forward_pointer + 1]

def advance():
    global forward_pointer
    forward_pointer += 1

def end_of_file(step: int = 0):
    return forward_pointer + step >= len(source)

def get_lexeme() -> str:
    return source[begin_pointer:forward_pointer]

def is_identifier_or_keyword_start(char: str):
    return regex.match("[A-Za-z_]", char)

def is_identifier_or_keyword(char: str):
    return regex.match("[A-Za-z]", char)

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
    while current_char() != EOF and regex.match("[A-Za-z0-9_]", current_char()): advance()
    lexeme = get_lexeme()
    if lexeme in keywords:
        create_token("KEYWORD", lexeme)
        return
    create_token("IDENTIFIER", lexeme)

def read_number():
    while current_char() != EOF and regex.match("[0-9]", current_char()): advance()
    if current_char() == ".":
        return read_float()
    if current_char() not in "+-*/%; )":
        while current_char() != EOF and current_char() not in "+-*/%; ": advance()
        lexeme = get_lexeme()
        create_error_token(lexeme)
        return
    
    lexeme = get_lexeme()
    create_token("INT", lexeme, int(lexeme))

def read_float():
    advance()
    while current_char() != EOF and regex.match("[0-9]", current_char()): advance()
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
    while current_char() != EOF and current_char() != "\n": advance()

def ignore_multiline_comment():
    closed = False
    while current_char() != EOF:
        char = current_char()
        next_char = get_next_char()
        advance()
        advance()
        if char == "*" and next_char == "/":
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
    while quote != 2 and current_char() != EOF:
        char = current_char()
        if char == "'":
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
    while double_quote != 2 and current_char() != EOF:
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
    
def main():
    return lexical_analyzer()

main()
file.close()
for symbol, value in symbol_table.items():
    print(symbol, value)
print()
for token in token_table:
    print(token)
