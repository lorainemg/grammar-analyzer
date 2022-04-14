from .tools.utils import ContainerSet
from .tools.grammar import Grammar, Sentence
from pprint import pprint

def compute_local_first(firsts, alpha):
    "Computes the first of one sentence in one iteration."
    first_alpha = ContainerSet()
    
    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except:
        alpha_is_epsilon = False
    
    # if the sentence is epsilon, then the set contains epsilon
    if alpha_is_epsilon:
        first_alpha.set_epsilon()
    # Otherwise, search through all the symbols and update the firsts
    else:
        for x in alpha:
            first_alpha.update(firsts[x])
            
            # if the set doesn't contains epsilon, then the first of the next symbol is checked
            if not firsts[x].contains_epsilon:
                break
        # If all the first contains epsilon, then the non-terminal produces epsilon
        else:
            first_alpha.set_epsilon()                 
    return first_alpha


def compute_firsts(G):
    "Computes all the first of a grammar `G`"
    firsts = {}
    change = True
    
    # init First(Vt)
    for terminal in G.terminals:
        firsts[terminal] = ContainerSet(terminal)
        
    # init First(Vn)
    for nonterminal in G.nonTerminals:
        firsts[nonterminal] = ContainerSet()
    
    while change:
        change = False 
        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right
            
            # get current First(X)
            first_X = firsts[X]
                
            # init First(alpha)
            try:
                first_alpha = firsts[alpha]
            except:
                first_alpha = firsts[alpha] = ContainerSet()
            
            # returns the local first of the sentence `alpha`
            local_first = compute_local_first(firsts, alpha)
            
            # update First(X) and First(alpha) from CurrentFirst(alpha)
            change |= first_alpha.hard_update(local_first)
            change |= first_X.hard_update(local_first)
                    
    return firsts


from itertools import islice

def compute_follows(G, firsts):
    "Computes the follows of a grammar `G`"
    follows = { } 
    change = True
    
    local_firsts = {}
    
    # init Follow(Vn)
    for nonterminal in G.nonTerminals:
        follows[nonterminal] = ContainerSet()
    follows[G.startSymbol] = ContainerSet(G.EOF)
    
    while change:
        change = False
        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right
            
            follow_X = follows[X]
            
            for i in range(len(alpha)):
                s = alpha[i]
                if s.IsNonTerminal:
                    # gets the next production
                    beta = islice(alpha, i+1, None)

                    # gets the firsts of beta
                    if beta not in local_firsts:
                        first = compute_local_first(firsts, beta)
                        local_firsts[beta] = first 
                    else:
                        first = local_firsts[beta]
                    
                    # update the follows of the nonterminal with the firsts of beta
                    change |= follows[s].update(first)
                    if i == len(alpha) - 1 or first.contains_epsilon:
                        change |= follows[s].update(follow_X)
    return follows

    

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

    print(G)

    firsts = compute_firsts(G)
    pprint(firsts)
    assert firsts == {
        plus: ContainerSet(plus , contains_epsilon=False),
        minus: ContainerSet(minus , contains_epsilon=False),
        star: ContainerSet(star , contains_epsilon=False),
        div: ContainerSet(div , contains_epsilon=False),
        opar: ContainerSet(opar , contains_epsilon=False),
        cpar: ContainerSet(cpar , contains_epsilon=False),
        num: ContainerSet(num , contains_epsilon=False),
        E: ContainerSet(num, opar , contains_epsilon=False),
        T: ContainerSet(num, opar , contains_epsilon=False),
        F: ContainerSet(num, opar , contains_epsilon=False),
        X: ContainerSet(plus, minus , contains_epsilon=True),
        Y: ContainerSet(div, star , contains_epsilon=True),
        Sentence(T, X): ContainerSet(num, opar , contains_epsilon=False),
        Sentence(plus, T, X): ContainerSet(plus , contains_epsilon=False),
        Sentence(minus, T, X): ContainerSet(minus , contains_epsilon=False),
        G.Epsilon: ContainerSet( contains_epsilon=True),
        Sentence(F, Y): ContainerSet(num, opar , contains_epsilon=False),
        Sentence(star, F, Y): ContainerSet(star , contains_epsilon=False),
        Sentence(div, F, Y): ContainerSet(div , contains_epsilon=False),
        Sentence(num): ContainerSet(num , contains_epsilon=False),
        Sentence(opar, E, cpar): ContainerSet(opar , contains_epsilon=False) 
    }

    follows = compute_follows(G, firsts)

    pprint(follows)
    assert follows == {
        E: ContainerSet(G.EOF, cpar , contains_epsilon=False),
        T: ContainerSet(cpar, plus, G.EOF, minus , contains_epsilon=False),
        F: ContainerSet(cpar, star, G.EOF, minus, div, plus , contains_epsilon=False),
        X: ContainerSet(G.EOF, cpar , contains_epsilon=False),
        Y: ContainerSet(cpar, plus, G.EOF, minus , contains_epsilon=False) 
    }