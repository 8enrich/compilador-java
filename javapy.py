from sys import argv, exit
from lexical_analyzer import LexicalAnalyzer

def main(filename: str):
    lexical_analyzer = LexicalAnalyzer(filename)
    token_table, symbol_table = lexical_analyzer.analyze()
    print(token_table, symbol_table)

if len(argv) != 2:
    print(f"Uso: python3 {argv[0]} <java-file>")
    exit(1)

filename = argv[1]
main(filename)
