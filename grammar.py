
grammar = {
    "PROG": ["public class id { public static void id ( ) { CMDS } }"],
    "CMDS": ["CMD CMDS", ""],
    "CMD": ["DECL", "ATRIB", "IF_STMT"],
    "DECL": ["TIPO id ;"],
    "TIPO": ["int", "float", "char"],
    "ATRIB": ["id = E ;"],
    "IF_STMT": ["if ( COND ) { CMDS } SENAO"],
    "SENAO": ["else { CMDS }", ""],
    "COND": ["E OP_REL E"],
    "OP_REL": ["==", "!=", "<", ">"],
    "E": ["T E'"],
    "E'": ["+ T E'", "- T E'", ""],
    "T": ["F T'"],
    "T'": ["* F T'", "/ F T'", ""],
    "F": ["( E )", "id", "num"]
    # "D": ["T id IDS ; D", ""],
    # "IDS": [", id IDS", ""],
    # "T": ["TB V"],
    # "TB": ["char", "int"],
    # "V": ["[ num_int ] V", ""]
    # "E": ["T E'"],
    # "E'": ["+ T E'", ""],
    # "T": ["F T'"],
    # "T'": ["* F T'", ""],
    # "F": ["id", "( E )"]
}

start_symbol = "PROG"
end_of_input = "$"

non_terminals_symbols = set(grammar.keys())

def is_terminal(symbol): return symbol not in non_terminals_symbols

def is_start_symbol(symbol): return start_symbol == symbol
