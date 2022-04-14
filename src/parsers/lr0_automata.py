from ..tools.automata import State, multiline_formatter, lr0_formatter
from ..tools.grammar import Grammar, Item


def build_LR0_automaton(G):
    "Builds a LR(0) automaton given an augmented grammar `G`"
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0)

    automaton = State(start_item, True)

    pending = [ start_item ]
    visited = { start_item: automaton }

    while pending:
        current_item = pending.pop()
        if current_item.IsReduceItem:
            continue
        
        # Decide which transitions to add
        next_trans = current_item.NextItem()
        next_symb = current_item.NextSymbol
        current_state = visited[current_item]

        pending.append(next_trans)
        visited[next_trans] = State(next_trans, True)
        current_state.add_transition(next_symb.name, visited[next_trans])
        
        if next_symb.IsNonTerminal: 
            for production in next_symb.productions:
                next_trans = Item(production, 0)
                if next_trans not in visited:
                    pending.append(next_trans)
                    visited[next_trans] = State(next_trans, True)
                current_state.add_epsilon_transition(visited[next_trans])
    
    # automaton.set_formatter(lr0_formatter) 
    # automaton.set_formatter(multiline_formatter)
           
    return automaton

# ----------------------------- Automata determinista -----------------------------

def closure(items):
    closure_set = set(items)
    pending = list(items)
    
    while pending:
        item = pending.pop()
        if item.IsReduceItem or item.NextSymbol.IsTerminal:
            continue
        for prod in item.NextSymbol.productions:
            new_item = Item(prod, 0)
            if new_item not in closure_set:
                closure_set.add(new_item)
                pending.append(new_item)
    
    return tuple(closure_set)


def goto(items, symbol):
    gotos = set()
    
    for item in items:
        if not item.IsReduceItem and item.NextSymbol == symbol:
            gotos.add(item.NextItem())

    return closure(gotos)


def build_LR0_DFA(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    start_production = G.startSymbol.productions[0]
    start_items = closure({Item(start_production, 0)}) 

    automaton = State(start_items, True)

    pending = [ start_items]
    visited = { start_items: automaton }
    
    while pending:
        current_items = pending.pop()
        symbols = { item.NextSymbol for item in current_items if not item.IsReduceItem }
        current_state = visited[current_items]
        
        for symbol in symbols:
            next_items = goto(current_items, symbol)
            if next_items not in visited:
                pending.append(next_items)
                visited[next_items] = State(next_items, True)
            current_state.add_transition(symbol.name, visited[next_items])
        
    automaton.set_formatter(multiline_formatter)
    return automaton


if __name__ == "__main__":
    G = Grammar()
    E = G.NonTerminal('E', True)
    T, F = G.NonTerminals('T F')
    plus, minus, star, div, opar, cpar, num = G.Terminals('+ - * / ( ) int')

    E %= E + plus + T | T # | E + minus + T 
    T %= T + star + F | F # | T + div + F
    F %= num | opar + E + cpar

    GG = G.AugmentedGrammar()

    automaton = build_LR0_automaton(GG)
    automaton.to_deterministic(lr0_formatter)
    automaton.set_formatter(multiline_formatter)
    automaton.write_to('../web/img/lr0_automaton.svg')