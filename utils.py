from flask import request, json
from src.tools.grammar import Grammar, Production, Sentence
import pickle


class Data:
    valid = False
    version=0
    @classmethod
    def read_grammar(cls):
        if cls.valid:
            with open('static/grammar.json', 'r') as f:
                grammar = json.load(f)
            with open('static/grammar.pkl', 'rb') as f:
                G = pickle.load(f)
            return grammar, G
        return None, None

    @classmethod
    def write_grammar(cls, grammar, G):
        cls.valid = True
        with open('static/grammar.json', 'w') as f:
            json.dump(grammar, f)
        with open('static/grammar.pkl', 'wb') as f:
            pickle.dump(G, f)

    @classmethod
    def get_version(cls):
        cls.version += 1
        return cls.version


def get_grammar():
    return {
        'start': request.form.get('startSymb'), 
        'nonterminals': request.form.get('nonterminals'), 
        'terminals': request.form.get('terminals'), 
        'productions': request.form.get('productions')
    }


def parse_grammar(grammar):
    G = Grammar()

    start = grammar['start']
    try:
        S = G.NonTerminal(start, True)
    except:
        return G, ['Please insert a start symbol']

    nonterminals = grammar['nonterminals'].replace(',', '')
    N = G.NonTerminals(nonterminals)
    
    terminals = grammar['terminals'].replace(',', '')
    T = G.Terminals(terminals)

    errors = add_productions(grammar['productions'], G)
    return G, errors


def add_productions(productions, G):
    prod_list =[p.strip() for p in productions.splitlines() if p and not p.isspace()]
    
    errors = set()
    for prod in prod_list:
        try:
            right, left = (p.strip() for p in prod.split('->'))
            _get_production(G, right, left, errors)
        except ValueError:
            errors.add(f'La producción {prod} no es válida')
    return errors
    

def _get_production(G, right, left, errors):
    nonTerminal = _get_symbol(G, G.nonTerminals, right)
    if nonTerminal is None:
        errors.add(f'El símbolo {right} no está definido')
    sentences = [s.strip() for s in left.split('|')]
    symbols = G.nonTerminals + G.terminals
    for sentence in sentences:
        symb_list = sentence.split()
        symbs = [_get_symbol(G, symbols, n) for n in symb_list]
        if _all_valid(symbs, symb_list, errors) and nonTerminal is not None:
            if len(symbs) == 1 and symbs[0] == G.Epsilon:
                G.Add_Production(Production(nonTerminal, symbs[0]))
            else:
                G.Add_Production(Production(nonTerminal, Sentence(*symbs)))

def _all_valid(symbols, n_symbols, errors):
    mark = True
    for symb, nsymb in zip(symbols, n_symbols):
        if symb is None:
            mark = False
            errors.add(f'El símbolo {nsymb} no está definido')
    return mark

def _get_symbol(G, symbols, name):
    if name == 'epsilon':
        return G.Epsilon
    for s in symbols:
        if s.name == name:
            return s


if __name__ == "__main__":
    grammar = {
        'start': 'S',
        'nonterminals': 'A B',
        'terminals': 'a b',
        'productions': """
            S -> A a A b | B b B a
            A -> epsilon | b B
            B -> epsilon
    """
    }
    parse_grammar(grammar)   
    a = ""
    # print(a.)
    