from grammar import grammar, is_start_symbol, is_terminal, end_of_input, start_symbol
from m_table import M_table

class SyntaxAnalyzer:

    def __init__(self):
        self.first_sets = {}
        self.follow_sets = {}
        self.set_first_sets()
        self.set_follow_sets()
        self.M = M_table(self.first_sets, self.follow_sets)
        self.indexes = {
            "IDENTIFIER": "id",
            "INT": "num",
            "FLOAT": "num"
        }

    def set_first_sets(self):
        for symbol in grammar:
            self.first_sets[symbol] = self.first(symbol) 

    def first(self, x):
        x_set = set()
        if self.first_sets.get(x, None):
            return self.first_sets[x]
        if is_terminal(x):
            return {x}
        for production in grammar[x]:
            x_set = x_set.union(self.first_aux(x, production))
        self.first_sets[x] = x_set
        return x_set

    def first_aux(self, x, Y):
        y = Y[0] if isinstance(Y, list) else Y
        first_y = self.first(y)
        x_set = first_y if first_y == {None} else first_y - {None}
        if None in first_y and isinstance(Y, list):
            x_set = x_set.union(self.first_aux(x, Y[1:]))
        return x_set

    def get_productions(self):
        productions_tuple = []
        for key, values in grammar.items():
            for value in values:
                if value is None: continue
                productions_tuple.append((key, value if isinstance(value, list) else [value]))
        return productions_tuple

    def get_next_set(self, values):
        next = {}
        for value in values:
            key, productions = value
            for index, item in enumerate(productions):
                if is_terminal(item): continue
                if index + 1 < len(productions):
                    next[item] = (productions[index + 1], index + 1)
                    continue
                if key == item: continue
                next[item] = (key, 0)
        return next

    def set_follow_sets(self):
        productions_tuple = self.get_productions()
        next = self.get_next_set(productions_tuple)
        for symbol in grammar:
            self.follow_sets[symbol] = self.follow(symbol, next)

    def follow(self, x, next):
        a_set = set()
        if is_start_symbol(x):
            a_set.add(end_of_input)
        if self.follow_sets.get(x, None):
            return self.follow_sets[x].union(a_set)
        value, index = next.get(x, (None, -1))
        if not value:
            return a_set
        if index > 0:
            return (self.first(value) - {None}).union(self.follow(value, next) if None in self.first_sets.get(value, []) else {})
        return a_set.union(self.follow(value, next)) 

    def get_token_index(self, token):
        return self.indexes.get(token[0], token[1])

    def analyze(self, token_table):
        stack = [start_symbol]
        token_table.append(("END_OF_INPUT", end_of_input))
        i = 0
        while len(stack) > 0:
            token = token_table[i]
            symbol = stack.pop()
            if symbol == self.get_token_index(token):
                i += 1
                continue
            production = self.M[symbol, self.get_token_index(token)]
            if production == "": raise Exception()
            if production is None: continue
            if isinstance(production, list):
                stack += production[::-1]
                continue
            stack.append(production)

if __name__ == "__main__":
    sa = SyntaxAnalyzer()
