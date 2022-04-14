from .tools.grammar import Grammar, Sentence
from copy import copy

def eliminate_recursion(G):
    "Elimina la recursión izquierda en una gramática `G`"
    nonterminals = list(G.nonTerminals)
    for i, non_term in enumerate(nonterminals):
        for j in range(i):
            _replace_productions(G, non_term, nonterminals[j])
        _eliminate_inmediate_recursion(non_term, G)

def _eliminate_inmediate_recursion(symbol, G):
    '''
    Elimina la recursion inmediate en una gramática `G` considerando 
    el no terminal `symbol`
    '''
    symb_prod = [prod for prod in G.Productions if prod.Left == symbol]
    rec_prod = { prod for prod in symb_prod if not prod.Right.IsEpsilon and symbol == prod.Right[0]} 
   
    nonrec_prod = rec_prod.symmetric_difference(symb_prod)
    # print(nonrec_prod)
    if not rec_prod:
        return
    new_term = G.NonTerminal(symbol.name + '\'')
    _eliminate_prod(G, symb_prod)
    for prod in nonrec_prod:
        symbol %= prod.Right + new_term
    for prod in rec_prod:
        if len(prod.Right) > 1:
            new_term %= Sentence(*prod.Right[1:]) + new_term
    new_term %= G.Epsilon


def _eliminate_prod(G, prods):
    'Elimina la lista de producciones `prods` de una gramática `G`'
    for p in prods:
        try:
            G.Productions.remove(p)
        except:
            pass


def _replace_productions(G, left, right):
    """
    Reemplaza las producciones left -> right + alpha, donde se presencia 
    recursividad izquierda indirecta.
    """
    left_prod = [prod for prod in G.Productions if prod.Left == left]
    right_prod = [prod for prod in G.Productions if prod.Left == right]
    
    rec_prod = { prod for prod in left_prod if not prod.Right.IsEpsilon and right == prod.Right[0] } 
    if not rec_prod:
        return
    _eliminate_prod(G, rec_prod)
    for prod in rec_prod:
        for r_prod in right_prod:
            left %= r_prod.Right + Sentence(*prod.Right[1:])



def left_refactoring(G):
    "Elimina los prefijos comunes de una gramática `G`"
    nonterminals = list(G.nonTerminals)
    for symb in nonterminals:
        symb_prod = [prod for prod in G.Productions if prod.Left == symb]
        visited = []
        for prod1 in symb_prod:
            if prod1 not in visited and not prod1.Right.IsEpsilon:
                prods, i = _longer_prefix(prod1, symb_prod)
                visited.extend(prods + [prod1])
                if not prods:
                    continue
                prods += [prod1]
                new_term = G.NonTerminal(symb.name + '\'')
                _eliminate_prod(G, prods)
                symb %= Sentence(*prod1.Right[:i]) + new_term
                for p in prods:
                    if len(p.Right[i:]) == 0:
                        new_term %= G.Epsilon
                    else:
                        new_term %= Sentence(*p.Right[i:])


def _longer_prefix( prod, productions):
    """
    Determina cuál es el mayor prefijo común dado una producción `prod`
    en relación con un conjunto de producciones `productions`
    """
    i = 1
    prods = []
    for p in productions:
        if prod == p or p.Right.IsEpsilon: 
            continue
        if prod.Right[:i] == p.Right[:i]:
            prods.append(p)
            if p.Right[:i+1] == prod.Right[:i+1]:
                prods = [p]
                while p.Right[:i+1] == prod.Right[:i+1]:
                    i += 1
                i += 1
    return prods, i
  

def _eliminate_nongenerating(G):
    change = True
    while change:
        nongenerating = []

        for nonterm in G.nonTerminals:
            if not [p for p in G.Productions if p.Left == nonterm]:
                nongenerating.append(nonterm)   

        prod = [p for p in G.Productions if any(symb in p.Right for symb in nongenerating)]
        _eliminate_prod(G, prod)
        for s in nongenerating:
            G.nonTerminals.remove(s)

        change = len(nongenerating) > 0
    

def _eliminate_unreacheble(G):
    visited = {G.startSymbol}
    pending = [G.startSymbol]

    while pending:
        current = pending.pop()
        if current.IsTerminal:
            continue

        for prod in [p for p in G.Productions if p.Left == current]:
            for symb in prod.Right:
                if symb not in visited:
                    visited.add(symb)
                    pending.append(symb)
    
    unreachable = visited.symmetric_difference(G.nonTerminals + G.terminals)
    prod = [p for p in G.Productions if p.Left in unreachable]
    _eliminate_prod(G, prod)
    for s in unreachable:
        if s.IsTerminal:
            G.terminals.remove(s)
        else:
            G.nonTerminals.remove(s)

# def _eliminate_cycles(G):
#     for nonterm in G.nonTerminals:
#         if len(nonterm.productions) == 1:

        

def eliminate_useless_prod(G):
    "Elimina las producciones innecesarias de una gramática `G`"
    # _eliminate_cycles(G)
    _eliminate_nongenerating(G)
    _eliminate_unreacheble(G)


if __name__ == "__main__":
    G = Grammar()
    S = G.NonTerminal('S', True)
    # A, B, C, D = G.NonTerminals('A B C D')
    a, = G.Terminals('a')
    
    # S %= A + a | B
    # A %= B + a
    # B %= a
    # C %= b + A
    # D %= C + D
    # eliminate_unreachable_prod(G)

    S %= S + a | a
    eliminate_recursion(G)
    print(G)
