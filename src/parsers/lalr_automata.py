from ..tools.grammar import Grammar, Item
from ..tools.automata import State, multiline_formatter
from .lr1_automata import build_LR1_automaton, compress

def equal_centers(items1, items2):
    for item in items1:
        core = item.Center()
        if not any(True for itm in items2 if core == itm.Center()):
            return False
    
    return True

def compress_state(node, automata, visited):
    items = [ item for item in node.state ]

    transitions = list(node.transitions.items())
    
    # Get the states with equals centers
    for state in automata:
        if state == node or len(state.state) != len(node.state):
            continue
            
        if equal_centers(state.state, node.state):
            items.extend(state.state)
            transitions.extend(state.transitions.items())
    
    # Create the new state with its transitions
    new_state = State(frozenset(compress(items)), True)

    for symbol, state in transitions:
        items = state[0].state
        # For the auto-references
        if equal_centers(items, node.state):
            visited[items] = new_state
        new_state[symbol] = state
        
    return new_state


def build_LALR_automaton(G):
    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])
    
    automata_lr1 = build_LR1_automaton(G)
    automaton = compress_state(automata_lr1, automata_lr1, {})    
    
    pending = [ start ]
    visited = { start: automaton }
    
    while pending:
        current = pending.pop()
        current_state = visited[current]
        
        # Get the old transitions of the state
        transitions = current_state.transitions
        current_state.transitions = {}
        
        # For every transition in the old automata, add the 
        # transitions with the new LALR states
        for symbol, state in transitions.items():
            items = frozenset(state[0].state)
            try:
                next_state = visited[items]
            except KeyError:
                next_state = compress_state(state[0], automata_lr1, visited)
                pending.append(items)
                visited[items] = next_state 
            current_state.add_transition(symbol, next_state)
    
    automaton.set_formatter(multiline_formatter)
    return automaton


if __name__ == "__main__":
    G = Grammar()
    E = G.NonTerminal('E', True)
    A = G.NonTerminal('A')
    equal, plus, num = G.Terminals('= + int')

    E %=  A + equal + A | num
    A %= num + plus + A | num

    automaton = build_LALR_automaton(G.AugmentedGrammar(True))
    automaton.write_to('../web/img/lalr_automaton.svg')