from ..tools.grammar import Grammar, Item
from ..tools.utils import tokenizer, Token
from ..firsts_follows import compute_firsts, compute_follows
from .lr0_automata import build_LR0_DFA, build_LR0_automaton
from .parse_trees import parse_tree_right
from .shift_reduce_parser import ShiftReduceParser

class SLR1Parser(ShiftReduceParser):        

    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        firsts = compute_firsts(G)
        follows = compute_follows(G, firsts)
        self.errors = []

        automaton = build_LR0_DFA(G)#.to_deterministic()
        self.automaton = automaton
        # self.automaton.set_formatter(lr0_formatter)
        
        for i, node in enumerate(automaton):
            if self.verbose: print(i, node)
            node.idx = i

        for node in automaton:
            idx = node.idx
            for state in node.state:
                item = state
                prod = item.production
                if item.IsReduceItem:
                    if prod.Left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), (self.OK, idx))
                    else:
                        for symbol in follows[prod.Left]:
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



    def derivation_tree(self,word):
        tokenize = tokenizer(self.G, {t.name: Token(t.name, t) for t in self.G.terminals}) 
        tokens = tokenize(word)
        # print(tokens)
        derivations = self([t.token_type for t in tokens])

        parse_tree_right(derivations).write_svg('static/img/slr_parse_tree.svg')



if __name__ == '__main__':
    G = Grammar()
    S = G.NonTerminal('S', True)
    A, = G.NonTerminals('A')
    a, b, c, d = G.Terminals('a b c d')

    S %= A + a | b + A + c | d + c | b + d + a
    A %= d


    parser = SLR1Parser(G, verbose=True)
    parser.display_action_table()
    parser.display_goto_table()

    derivation = parser([num, plus, num, star, num, G.EOF])
    assert str(derivation) == '[F -> int, T -> F, E -> T, F -> int, T -> F, F -> int, T -> T * F, E -> E + T]'
