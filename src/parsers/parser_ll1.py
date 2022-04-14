from ..tools.grammar import Grammar, Sentence, Production
from ..firsts_follows import compute_firsts, compute_follows
from ..tools.utils import tokenizer, Token
from pprint import pprint
from .parse_trees import parse_tree_left

class ParserLL1:
    def __init__(self, G):
        self.G = G
        self.M = None
        self.firsts = None
        self.follows = None

    def build_parsing_table(self, firsts, follows):
        """
        Builds a LL(1) parsing table
        """
        # init parsing table
        M = {}
        errors = []
        
        for production in self.G.Productions:
            # P: X -> alpha
            X = production.Left
            alpha = production.Right
            
            for t in firsts[alpha]:
                if t.IsTerminal:
                    self._register(M, (X, t), production, errors)

            if firsts[alpha].contains_epsilon:
                for t in follows[X]:
                    self._register(M, (X, t), production, errors)


        return M, errors

    @staticmethod
    def _register(table, key, value, errors):
        try:
            table[key].append(value)
            errors.append(f'Follow conflict with the production {key[0]} and the terminal {key[1]}')
        except KeyError:
            table[key] = [value]
    

    def metodo_predictivo_no_recursivo(self):    
        if self.M is None:
            if self.firsts is None:
                self.firsts = compute_firsts(self.G)
            if self.follows is None:
                self.follows = compute_follows(self.G, self.firsts)
            self.M, _ = self.build_parsing_table(self.firsts, self.follows)
        
        def parser(w):
            stack =  [self.G.startSymbol]
            cursor = 0
            output = []
            
            while len(stack) > 0 and cursor < len(w):
                top = stack.pop()
                a = w[cursor]
                
                if top.IsTerminal and w[cursor] == top:
                    cursor += 1
                elif top.IsNonTerminal:
                    prod = self.M[(top, a)][0]
                    output.append(prod)
                    for s in reversed(prod.Right):
                        stack.append(s)
                else:
                    raise Exception(f'The string {w} doesn\'t belongs to the language')
                
            return output
        
        return parser


    def derivation_tree(self, word):    
        parser = self.metodo_predictivo_no_recursivo()
        tokenize = tokenizer(self.G, {t.name: Token(t.name, t) for t in self.G.terminals}) 
        tokens = tokenize(word)
        derivations = parser([t.token_type for t in tokens])
        parse_tree_left(derivations).write_svg('static/img/ll1_parse_tree.svg')

    

if __name__ == '__main__':
    G = Grammar()
    E = G.NonTerminal('E', True)
    T,F,X,Y = G.NonTerminals('T F X Y')
    plus, minus, star, div, opar, cpar, num = G.Terminals('+ - * / ( ) num')

    E %= T + X
    X %= plus + T + X | minus + T + X | G.Epsilon
    T %= F + Y
    Y %= star + F + Y | div + F + Y | G.Epsilon
    F %= num | opar + E + cpar

    firsts = compute_firsts(G)
    follows = compute_follows(G, firsts)

    parser_ll1 = ParserLL1(G)
    M, _ = parser_ll1.build_parsing_table(firsts, follows)

    assert M == {
        ( E, num, ): [ Production(E, Sentence(T, X)), ],
        ( E, opar, ): [ Production(E, Sentence(T, X)), ],
        ( X, plus, ): [ Production(X, Sentence(plus, T, X)), ],
        ( X, minus, ): [ Production(X, Sentence(minus, T, X)), ],
        ( X, cpar, ): [ Production(X, G.Epsilon), ],
        ( X, G.EOF, ): [ Production(X, G.Epsilon), ],
        ( T, num, ): [ Production(T, Sentence(F, Y)), ],
        ( T, opar, ): [ Production(T, Sentence(F, Y)), ],
        ( Y, star, ): [ Production(Y, Sentence(star, F, Y)), ],
        ( Y, div, ): [ Production(Y, Sentence(div, F, Y)), ],
        ( Y, plus, ): [ Production(Y, G.Epsilon), ],
        ( Y, G.EOF, ): [ Production(Y, G.Epsilon), ],
        ( Y, cpar, ): [ Production(Y, G.Epsilon), ],
        ( Y, minus, ): [ Production(Y, G.Epsilon), ],
        ( F, num, ): [ Production(F, Sentence(num)), ],
        ( F, opar, ): [ Production(F, Sentence(opar, E, cpar)), ] 
    }

    parser = parser_ll1.metodo_predictivo_no_recursivo()
    left_parse = parser([num, star, num, star, num, plus, num, star, num, plus, num, plus, num, G.EOF])
    parser_ll1.derivation_tree('num + num')

    assert left_parse == [ 
        Production(E, Sentence(T, X)),
        Production(T, Sentence(F, Y)),
        Production(F, Sentence(num)),
        Production(Y, Sentence(star, F, Y)),
        Production(F, Sentence(num)),
        Production(Y, Sentence(star, F, Y)),
        Production(F, Sentence(num)),
        Production(Y, G.Epsilon),
        Production(X, Sentence(plus, T, X)),
        Production(T, Sentence(F, Y)),
        Production(F, Sentence(num)),
        Production(Y, Sentence(star, F, Y)),
        Production(F, Sentence(num)),
        Production(Y, G.Epsilon),
        Production(X, Sentence(plus, T, X)),
        Production(T, Sentence(F, Y)),
        Production(F, Sentence(num)),
        Production(Y, G.Epsilon),
        Production(X, Sentence(plus, T, X)),
        Production(T, Sentence(F, Y)),
        Production(F, Sentence(num)),
        Production(Y, G.Epsilon),
        Production(X, G.Epsilon),
    ]
