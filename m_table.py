from grammar import grammar, is_terminal, end_of_input
from itertools import chain

class M_table:
    
    def __init__(self, first, follow):
        self.indexes_x = {value: key for key, value in enumerate(grammar.keys())}
        self.indexes_y = self.set_indexes_y()
        self.table = [[None for _ in self.indexes_y] for _ in self.indexes_x]
        self.make_table(first, follow)

    def set_indexes_y(self):
        indexes_y = set(
            filter(
                is_terminal, 
                chain.from_iterable(
                    [
                        x.split() for x in filter(
                            lambda x: x, 
                            chain.from_iterable(grammar.values())
                        )
                    ]
                )
            )
        )
        return {item: index for index, item in enumerate(indexes_y.union({end_of_input}))}

    def make_table(self, first, follow):
        for key, productions in grammar.items():
            for production in productions:
                x = production.split()
                if not x:
                    for item in follow[key]:
                        self[key, item] = production
                    continue
                if is_terminal(x[0]):
                    self[key, x[0]] = production
                    continue
                for item in first[x[0]]:
                    self[key, item] = production

    def __setitem__(self, indexes, value):
        x, y = indexes
        self.table[self.indexes_x[x]][self.indexes_y[y]] = value

    def __getitem__(self, indexes):
        x, y = indexes
        index_x, index_y = self.indexes_x.get(x, None), self.indexes_y.get(y, None)
        if index_x is None or index_y is None:
            raise Exception(f'Indexes "{x}" "{y}" not found')
        return self.table[index_x][index_y]

    def _format_cell(self, cell):
        if cell is None:
            return "-"
        if isinstance(cell, tuple) and len(cell) == 2:
            lhs, rhs = cell
            if isinstance(rhs, list):
                parts = []
                for item in rhs:
                    if item == "":
                        parts.append("&")
                    elif isinstance(item, list):
                        parts.append(" ".join(str(s) for s in item))
                    else:
                        parts.append(str(item))
                return f"{lhs} -> " + " | ".join(parts)
        return str(cell)

    def __repr__(self):
        headers = ["NT"] + list(self.indexes_y.keys())
        
        rows = []
        for x_key, row in zip(self.indexes_x.keys(), self.table):
            formatted_row = [str(x_key)] + [self._format_cell(cell) for cell in row]
            rows.append(formatted_row)

        col_widths = [
            max(len(headers[i]), max(len(row[i]) for row in rows))
            for i in range(len(headers))
        ]

        header_line = " | ".join(f"{headers[i]:^{col_widths[i]}}" for i in range(len(headers)))
        separator = "-+-".join("-" * w for w in col_widths)
        data_lines = [
            " | ".join(f"{cell:<{col_widths[i]}}" for i, cell in enumerate(row))
            for row in rows
        ]

        return "\n" + "\n".join([header_line, separator] + data_lines)
