from keywords import keywords
from operators import operators
from delimitators import delimitators
from sys import argv
import regex

token_table = []
symbol_table = {}

def is_identifier_or_keyword(char: str):
    return regex.match("[A-Za-z_]", char)

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

def read_identifier_or_keyword(source: str, begin_pointer: int, forward_pointer: int) -> int:
    char = source[forward_pointer]
    while regex.match("[A-Za-z0-9_]", char):
        forward_pointer += 1
        char = source[forward_pointer]
    
    lexeme = source[begin_pointer:forward_pointer]
    if lexeme in keywords:
        create_token("KEYWORD", lexeme)
        return forward_pointer
    create_token("IDENTIFIER", lexeme)
    return forward_pointer

def read_number(source: str, begin_pointer: int, forward_pointer: int) -> int:
    char = source[forward_pointer]
    while regex.match("[0-9]", char):
        forward_pointer += 1
        char = source[forward_pointer]
    if source[forward_pointer] == ".":
        return read_float(source, source[begin_pointer:forward_pointer], forward_pointer)
    if source[forward_pointer] not in "+-*/%; )":
        while forward_pointer < len(source) and source[forward_pointer] not in "+-*/%; ":
            forward_pointer += 1
        lexeme = source[begin_pointer:forward_pointer]
        create_error_token(lexeme)
        return forward_pointer
    
    lexeme = source[begin_pointer:forward_pointer]
    create_token("INT", lexeme, int(lexeme))
    return forward_pointer

def read_float(source: str, int_part: str, forward_pointer: int) -> int:
    begin_pointer = forward_pointer
    char = source[forward_pointer + 1]
    while regex.match("[0-9]", char):
        forward_pointer += 1
        char = source[forward_pointer]
    if begin_pointer == forward_pointer:
        create_error_token(int_part + '.')
        return forward_pointer + 1
    lexeme = int_part + source[begin_pointer:forward_pointer]
    create_token("FLOAT", lexeme, float(lexeme))
    return forward_pointer

def read_operator_or_comment(source: str, begin_pointer: int, forward_pointer: int) -> int:
    char = source[begin_pointer]
    next_char = source[begin_pointer + 1]
    if char == "/" and (next_char == "/" or next_char == "*"):
        return ignore_comment(source, begin_pointer, forward_pointer)
    return read_operator(source, begin_pointer, forward_pointer)

def ignore_comment(source: str, begin_pointer: int, forward_pointer: int) -> int:
    char = source[begin_pointer]
    next_char = source[begin_pointer + 1]
    if char == "/" and next_char == "*":
        return ignore_multiline_comment(source, begin_pointer, forward_pointer)
    while forward_pointer < len(source) and char != "\n": 
        forward_pointer += 1
        char = source[forward_pointer]
    return forward_pointer

def ignore_multiline_comment(source: str, begin_pointer: int, forward_pointer: int) -> int:
    closed = False
    while forward_pointer < len(source):
        char = source[forward_pointer]
        forward_pointer += 1
        if char == "*" and forward_pointer < len(source) and source[forward_pointer] == "/":
            closed = True
            break
    if not closed:
        create_error_token(source[begin_pointer:forward_pointer])
        return forward_pointer 
    return forward_pointer + 1

def read_operator(source: str, begin_pointer: int, forward_pointer: int) -> int:
    char = source[begin_pointer]
    next_char = source[begin_pointer + 1]
    if char + next_char in operators:
        lexeme = char + next_char
        create_token("OPERATOR", lexeme)
        return forward_pointer + 1
    lexeme = char
    create_token("OPERATOR", lexeme)
    return forward_pointer

def read_delimitator(source: str, begin_pointer: int, forward_pointer: int) -> int:
    char = source[begin_pointer]
    lexeme = char
    create_token("DELIMITATOR", lexeme)
    return forward_pointer

def read_char(source: str, begin_pointer: int, forward_pointer: int) -> int:
    quote = 1
    while forward_pointer < len(source) and quote != 2:
        char = source[forward_pointer]
        if char == "'":
            quote += 1
        forward_pointer += 1
    if forward_pointer - begin_pointer <= 2:
        create_error_token(source[begin_pointer:forward_pointer])
        return forward_pointer
    if forward_pointer - begin_pointer > 3 and source[begin_pointer + 1] != "\\" or source[begin_pointer + 2] not in "btnfr\"'\\":
        create_error_token(source[begin_pointer:forward_pointer])
        return forward_pointer
    lexeme = source[begin_pointer:forward_pointer]
    create_token("CHAR", lexeme, lexeme[1:-1])
    return forward_pointer

def read_string(source: str, begin_pointer: int, forward_pointer: int) -> int:
    double_quote = 1
    while forward_pointer < len(source) and double_quote != 2:
        char = source[forward_pointer]
        if char == '"' and source[forward_pointer - 1] != "\\":
            double_quote += 1
        forward_pointer += 1
        if char == "\n":
            create_error_token(source[begin_pointer:forward_pointer-1])
            return forward_pointer
    lexeme = source[begin_pointer:forward_pointer]
    create_token("STRING", lexeme, lexeme[1:-1])
    return forward_pointer

def create_token(token_type: str, lexeme: str, attribute = None):
    if token_type == "IDENTIFIER":
        data = symbol_table.get(lexeme, {"occurrences": 0, "index": len(symbol_table)})
        occurrences = data["occurrences"]
        index = data["index"]
        symbol_table[lexeme] = {"occurrences": occurrences + 1, "index": index}
        attribute = index
    token_table.append((token_type, lexeme, attribute))

def create_error_token(lexeme: str):
    token_table.append(("ERROR", lexeme))

def lexical_analyzer(filename: str):

    file = open(filename, mode='r')
    source = file.read()
    begin_pointer = forward_pointer = 0

    while forward_pointer < len(source):
        
        begin_pointer = forward_pointer
        char = source[forward_pointer]
        forward_pointer += 1

        if is_whitespace(char):
            continue

        if is_identifier_or_keyword(char):
            forward_pointer = read_identifier_or_keyword(source, begin_pointer, forward_pointer)
            continue

        if is_digit(char):
            forward_pointer = read_number(source, begin_pointer, forward_pointer)
            continue

        if is_char(char):
            forward_pointer = read_char(source, begin_pointer, forward_pointer)
            continue

        if is_string(char):
            forward_pointer = read_string(source, begin_pointer, forward_pointer)
            continue

        if is_operator_or_comment(char):
            forward_pointer = read_operator_or_comment(source, begin_pointer, forward_pointer)
            continue

        if is_delimitator(char):
            forward_pointer = read_delimitator(source, begin_pointer, forward_pointer)
            continue

        create_error_token(char)
    
    file.close()

def main(filename: str):
    return lexical_analyzer(filename)

main(argv[1])
print(symbol_table)
for token in token_table:
    print(token)
