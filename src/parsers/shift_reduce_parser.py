from ..tools.utils import ContainerSet
from pandas import DataFrame
from pprint import pprint


class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'
    
    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()
    
    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [ 0 ]
        cursor = 0
        output = []
        
        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, w[cursor:])
            
            try:
                action, tag = self.action[state, lookahead][0]
            except KeyError:
                raise Exception()
                
            # (Shift case) 
            if action == self.SHIFT:
                stack.append(tag)
                cursor += 1
            
            # (Reduce case)
            elif action == self.REDUCE:
                prod = tag
                for _ in prod.Right:
                    stack.pop()
                output.append(prod)
                stack.append(self.goto[stack[-1], prod.Left][0])
            
            # (OK case)
            elif action == self.OK: 
                stack.pop()
                assert len(stack) == 1 and stack[-1] == 0
                return output
            
            # (Invalid case)
            else: raise Exception('La cadena no pertenece al lenguaje')

    @property
    def action_table(self):
        return table_to_dataframe(self.action)

    @property
    def goto_table(self):
        return table_to_dataframe(self.goto)

    def print_automata(self, filename):
        self.automaton.write_to(filename)



def encode_value(value):
    try:
        action, tag = value
        if action == ShiftReduceParser.SHIFT:
            return 'S' + str(tag)
        elif action == ShiftReduceParser.REDUCE:
            return repr(tag)
        elif action ==  ShiftReduceParser.OK:
            return action
        else:
            return value
    except TypeError:
        return value


def table_to_dataframe(table):
    d = {}
    for (state, symbol), values in table.items():
        for value in values:
            val = encode_value(value)
            if state not in d:
                d[state] = { symbol: ContainerSet(val) }
            else:
                try:
                    d[state][symbol].add(val)
                except:
                    d[state][symbol] = ContainerSet(val) 

    return DataFrame.from_dict(d, orient='index', dtype=str)

if __name__ == "__main__":
    table = {
        (0, 'b'): [('SHIFT', 4)],
        (0, 'd'): [('SHIFT', 9)],
        (1, '$'): [('OK', 1)],
        (2, 'a'): [('SHIFT', 3)],
        (3, '$'): [('REDUCE', 'S -> A a')],
        (4, 'd'): [('SHIFT', 7)],
        (5, 'c'): [('SHIFT', 6)],
        (6, '$'): [('REDUCE', "S -> b A c")],
        (7, 'c'): [('REDUCE', "A -> d")],
        (7, 'a'): [('SHIFT', 8), ('REDUCE', "A -> d")],
        (8, '$'): [('REDUCE', "S -> b d a")],
        (9, 'c'): [('SHIFT', 10), ('REDUCE', "A -> d")],
        (9, 'a'): [('REDUCE', 'A -> d')],
        (10, '$'): [('REDUCE', "S -> d c")]
    }

    table_to_dataframe(table)


