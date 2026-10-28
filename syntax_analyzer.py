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
        y = Y.split()
        first_y = self.first(y[0] if len(y) > 0 else "")
        x_set = first_y if first_y == {""} else first_y - {""}
        if "" in first_y and len(y) > 0:
            x_set = x_set.union(self.first_aux(x, y[1:]))
        return x_set

    def get_productions(self):
        productions_tuple = []
        for key, values in grammar.items():
            for value in values:
                if value == "": continue
                productions_tuple.append((key, value.split()))
        return productions_tuple

    def get_next_set(self, values):
        next = {}
        sets = {}
        for value in values:
            key, productions = value
            for index, item in enumerate(productions):
                if is_terminal(item): continue
                if index + 1 < len(productions):
                    if productions[index + 1] in sets.get(item, set()): continue
                    next[item] = next.get(item, []) + [(productions[index + 1], index + 1)]
                    sets[item] = sets.get(item, set()).union({productions[index + 1]})
                    continue
                if key == item: continue
                next[item] = next.get(item, []) + [(key, 0)]
                sets[item] = sets.get(item, set()).union({key})
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
        for production in next.get(x, []):
            a_set = a_set.union(self.follow_aux(production, next))
        return a_set

    def follow_aux(self, x, next):
        value, index = x
        if index > 0:
            return (self.first(value) - {""}).union(self.follow(value, next) if "" in self.first_sets.get(value, []) else {})
        return self.follow(value, next)

    def get_token_index(self, token):
        return self.indexes.get(token[0], token[1])

    def analyze(self, token_table):
        stack = [start_symbol]
        token_table.append(("END_OF_INPUT", end_of_input))
        i = 0
        while len(stack) > 0:
            token = self.get_token_index(token_table[i])
            symbol = stack.pop()
            if symbol == token:
                i += 1
                continue
            production = self.M[symbol, token]
            if production is None: raise Exception(f'Produção do tipo, "{symbol}" "{token}" não existe')
            if production == "": continue
            stack += production.split()[::-1]

if __name__ == "__main__":
    sa = SyntaxAnalyzer()
