from ..tools.grammar import Grammar
from ..tools.utils import tokenizer, Token
from .lalr_automata import build_LALR_automaton
from .parse_trees import parse_tree_right
from .shift_reduce_parser import ShiftReduceParser


class LALRParser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        
        automaton = build_LALR_automaton(G)
        self.automaton = automaton
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i
        self.errors = []


        for node in automaton:
            idx = node.idx
            for item in node.state:
                prod = item.production
                if item.IsReduceItem:
                    if prod.Left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), (self.OK, 0))
                    else:
                        for symbol in item.lookaheads:
                            self._register(self.action, (idx, symbol), (self.REDUCE, prod))
                else:
                    next_symb = item.NextSymbol
                    if next_symb.IsTerminal:
                        self._register(self.action, (idx, next_symb), (self.SHIFT, node.transitions[next_symb.name][0].idx))
                    else:
                        self._register(self.goto, (idx, next_symb), node.transitions[next_symb.name][0].idx)
      
    # @staticmethod
    def _register(self, table, key, value):
        try:
            if value not in table[key]:
                if any(op != value[0] for op, tag in table[key]):
                    self.errors.append(f'Shift-Reduce conflict in symbol {key[1]} and state {key[0]}')
                if any(op == value[0] == self.REDUCE for op, tag in table[key]):
                    self.errors.append(f'Reduce-Reduce conflict, in symbol {key[1]} and state {key[0]}')
                table[key].append(value)
        except Exception as e: 
            table[key] = [value]


    def derivation_tree(self, word):
        tokenize = tokenizer(self.G, {t.name: Token(t.name, t) for t in self.G.terminals}) 
        tokens = tokenize(word)
        # print(tokens)
        derivations = self([t.token_type for t in tokens])

        parse_tree_right(derivations).write_svg('static/img/lalr_parse_tree.svg')




if __name__ == "__main__":
    G = Grammar()
    S = G.NonTerminal('S', True)
    A, B = G.NonTerminals('A B')
    a, b, c, d = G.Terminals('a b c d')

    S %= A + a | b + A + c | B + c | b + B + a
    A %= d
    B %= d

    parser = LALRParser(G)
    parser.display_action_table()
    parser.display_goto_table()

    derivation = parser([num, plus, num, equal, num, plus, num, G.EOF])
    assert str(derivation) == '[A -> int, A -> int + A, A -> int, A -> int + A, E -> A = A]'
