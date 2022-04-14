from ..tools.grammar import Grammar, Item
from ..tools.utils import ContainerSet
from ..tools.automata import State, multiline_formatter
from ..firsts_follows import compute_firsts, compute_local_first

def expand(item, firsts):
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []
    
    lookaheads = ContainerSet()
    for prev in item.Preview():
        print(prev)
        lookaheads.update(compute_local_first(firsts, prev))            
    
    print(next_symbol.productions)
    print(prev)
    assert not lookaheads.contains_epsilon
    return [Item(prod, 0, lookaheads) for prod in next_symbol.productions]
            
           
def compress(items):
    centers = {}

    for item in items:
        center = item.Center()
        try:
            lookaheads = centers[center]
        except KeyError:
            centers[center] = lookaheads = set()
        lookaheads.update(item.lookaheads)

    return { Item(x.production, x.pos, set(lookahead)) for x, lookahead in centers.items() }


def closure_lr1(items, firsts):
    closure = ContainerSet(*items)
    
    changed = True
    while changed:
        changed = False
        
        new_items = ContainerSet()
        for item in closure:
            new_items.extend(expand(item, firsts))
        changed = closure.update(new_items)
        
    return compress(closure)


def goto_lr1(items, symbol, firsts=None, just_kernel=False):
    assert just_kernel or firsts is not None, '`firsts` must be provided if `just_kernel=False`'
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_lr1(items, firsts)


def build_LR1_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'
    
    firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)
    
    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])
    
    closure = closure_lr1(start, firsts)
    automaton = State(frozenset(closure), True)
    
    pending = [ start ]
    visited = { start: automaton }
    
    while pending:
        current = pending.pop()
        current_state = visited[current]
        
        closure = closure_lr1(current, firsts)
        for symbol in G.terminals + G.nonTerminals:
            new_items = frozenset(goto_lr1(closure, symbol, just_kernel=True))
            if not new_items:
                continue
            try:
                next_state = visited[new_items]
            except KeyError:
                pending.append(new_items)
                next_state = State(frozenset(closure_lr1(new_items, firsts)), True)
                visited[new_items] = next_state 
            current_state.add_transition(symbol.name, next_state)
    
    automaton.set_formatter(multiline_formatter)
    return automaton


if __name__ == "__main__":
    G = Grammar()
    E = G.NonTerminal('E', True)
    A = G.NonTerminal('A')
    equal, plus, num = G.Terminals('= + int')

    E %=  A + equal + A | num
    A %= num + plus + A | num

    automaton = build_LR1_automaton(G.AugmentedGrammar())

    assert automaton.recognize('E')
    assert automaton.recognize(['A','=','int'])
    assert automaton.recognize(['int','+','int','+','A'])

    assert not automaton.recognize(['int','+','A','+','int'])
    assert not automaton.recognize(['int','=','int'])

    automaton.write_to('../web/img/lr1_automaton.svg')