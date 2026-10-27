from sys import argv, exit
from lexical_analyzer import LexicalAnalyzer
from syntax_analyzer import SyntaxAnalyzer

def main(filename: str):
    lexical_analyzer = LexicalAnalyzer(filename)
    token_table, symbol_table = lexical_analyzer.analyze()
    syntax_analyzer = SyntaxAnalyzer()
    syntax_analyzer.analyze(token_table)

if len(argv) != 2:
    print(f"Uso: python3 {argv[0]} <java-file>")
    exit(1)

filename = argv[1]
main(filename)
