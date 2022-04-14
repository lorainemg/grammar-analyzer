from .tools.grammar import Grammar
from .tools.automata import State

def _get_name(sentence):
    try:
        return sentence[0].name
    except:
        return sentence.name

def get_automata(G):
    # G = G.AugmentedGrammar(True)
    start = G.startSymbol
    automaton = State(start)    
    for left, right in start.productions:
        if right.IsEpsilon:
            automaton.final = True
    pending = [start]
    visited = {start: automaton}


    final = State('end', True)
    while pending:
        current = pending.pop()
        state = visited[current]

        for left, rigth in current.productions:
            terminal = _get_name(rigth)
            if len(rigth) == 1:
                state.add_transition(terminal, final)
            elif len(rigth) == 2:
                nonterm = rigth[1]
                try:
                    new_state = visited[nonterm]
                except KeyError:
                    new_state = State(nonterm)
                    pending.append(nonterm)
                    visited[nonterm] = new_state
                state.add_transition(terminal, new_state)
    return automaton


def is_regular(G):
    for left, right in G.Productions:
        if right.IsEpsilon:
            if left != G.startSymbol:
                return False
        elif len(right) > 2:
            return False
        
        elif len(right) == 1:
            if right[0].IsNonTerminal:
                return False
        elif right[0].IsNonTerminal or right[1].IsTerminal: 
            return False
    
    return True  


def add_char(L, ie, je):
    symbol = L[ie][je]
    if symbol == 'e':
        return ''
    if len(symbol.split('|')) > 1 and symbol[-1] != ')':
        return '(' + symbol + ')'
    return symbol

def any_char(L, i, j, k):
    if L[i][k] != 'e' and L[i][k] != '':
        return True
    if L[k][k] != 'e' and L[k][k] != '':
        return True
    if L[k][j] != 'e' and L[k][j] != '':
        return True
    return False
    
def one_epsilon(L, i, j, k):
    if L[i][k] == '' and L[k][k] == '' and L[k][k] == '':
        return False
    return True

def _get_table(automata):
    states = list(automata)
    table = {s : {s1: '' for s1 in states} for s in states}
    
    for state in states:
        for symb, st_list in state.transitions.items():
            for st in st_list:
                if table[state][st] != '':
                    table[state][st] += '|'
                table[state][st] += symb

        for state1 in state.epsilon_transitions:
            if table[state][state1] != '':
                table[state][state1] += '|'    
            table[state][state1] += 'e'
    return table

def get_intermediate_states(states):
    return [state for state in states if not state.final]

def get_predecessors(table, state):
    return [key for key, value in table.items() if state in value.keys() and value[state] != '' and key != state]

def get_successors(table, state):
    return [key for key, value in table[state].items() if value != '' and key != state]

def get_loop(table, state):
    if table[state][state] != '':
        return '(' + table[state][state] + ')*'
    else:
        return ''

def get_regex(automata):
    start, end = add_two_states(automata)
    table = _get_table(start)

    for inter in get_intermediate_states(automata):
        pred = get_predecessors(table, inter)
        succ = get_successors(table, inter)

        for i in pred:
            for j in succ:
                if any_char(table, i, j, inter):
                    if table[i][j] != '':
                        table[i][j] += '|' 
                    table[i][j] += add_char(table, i, inter) + get_loop(table, inter) + add_char(table, inter, j) 
                elif one_epsilon(table, i, j, inter):
                    if table[i][j] != '':
                        table[i][j] += '|' 
                    table[i][j] += 'e'        
        table = {r: {c: v for c, v in val.items() if c != inter} for r, val in table.items() if r != inter}  # remove inter node\
    
    return table[start][end]


def add_two_states(automata):
    start = State('start')
    start.add_epsilon_transition(automata)

    end = State('end', True)
    for node in list(start):
        if node.final:
            node.final = False
            node.add_epsilon_transition(end)
    return start, end


if __name__ == "__main__":
    G = Grammar()

    # S = G.NonTerminal('S', True)
    # A = G.NonTerminal('A')
    # a, b = G.NonTerminals('a b')

    # # S %= a + S | a + A
    # # A %= b + A | b 

    # automaton = get_automata(G)
    # # automaton.write_to('../web/img/automaton_reg.svg')

    # S %= a + S | a
    # automaton = get_automata(G)
    # q0 = State(0)
    # q1 = State(1, True)
    # q2 = State(2)
    # q3 = State(3, True)

    # q0.add_transition('a', q1)
    # q0.add_transition('b', q2)
    # q1.add_transition('a', q3)
    # q2.add_transition('b', q3)
    

    # q0 = State(0)
    # q1 = State(1, True)
    # q2 = State(2)
    # q3 = State(3, True)
    # q4 = State(4, True)

    # q0.add_transition('a', q1)
    # q0.add_transition('a', q2)
    # q1.add_transition('d', q3)
    # q2.add_transition('d', q4)
    # q3.add_transition('d', q3)


    q0 = State(0)
    q1 = State(1)
    q2 = State(2, True)
    q3 = State(3, True)

    q0.add_transition('0', q0)
    q0.add_transition('1', q0)
    q0.add_transition('1', q1)
    
    q1.add_transition('1', q2)
    q1.add_transition('0', q2)
    
    q2.add_transition('0', q3)
    q2.add_transition('1', q3)

    print(automata_to_regex(q0))