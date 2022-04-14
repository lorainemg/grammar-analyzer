from ..tools.grammar import Production, Sentence, Grammar
import pandas
import pydot
import uuid

def parse_tree_left(productions):
    
    def parse(G, productions, i):
        left, right = productions[i]
        
        node = pydot.Node(uuid.uuid4().hex, label=left.name, shape ="circle", style="filled", fillcolor="white") 
        G.add_node(node)

        for symbol in right:
            if symbol.IsTerminal:
                child = pydot.Node(uuid.uuid4().hex, label=symbol.name, shape="circle", style="filled", fillcolor="white")
                G.add_node(child)
                G.add_edge(pydot.Edge(node, child))
            else:
                child, i = parse(G, productions, i + 1)
                G.add_edge(pydot.Edge(node, child))

        if right.IsEpsilon:
            child = pydot.Node(uuid.uuid4().hex, label='ε', shape="circle", style="filled", fillcolor="white")
            G.add_node(child)
            G.add_edge(pydot.Edge(node, child))
        
        return node, i

    G = pydot.Dot(graph_type='digraph')
    node, i = parse(G, productions, 0)

    return G

def parse_tree_right(productions):
    
    def parse(G, productions, i):
        left, right = productions[i]
        
        node = pydot.Node(uuid.uuid4().hex, label=left.name, shape ="circle", style="filled", fillcolor="white") 
        G.add_node(node)

        for symbol in reversed(right):
            if symbol.IsTerminal:
                child = pydot.Node(uuid.uuid4().hex, label=symbol.name, shape="circle", style="filled", fillcolor="white")
                G.add_node(child)
                G.add_edge(pydot.Edge(node, child))
            else:
                child, i = parse(G, productions, i + 1)
                G.add_edge(pydot.Edge(node, child))

        if right.IsEpsilon:
            child = pydot.Node(uuid.uuid4().hex, label='ε', shape="circle", style="filled", fillcolor="white")
            G.add_node(child)
            G.add_edge(pydot.Edge(node, child)) 
        return node, i
    
    productions.reverse()
    G = pydot.Dot(graph_type='digraph')
    node, i = parse(G, productions, 0)
   
    return G


if __name__ == "__main__":
    # G = Grammar()
    # E = G.NonTerminal('E', True)
    # T,F,X,Y = G.NonTerminals('T F X Y')
    # plus, minus, star, div, opar, cpar, num = G.Terminals('+ - * / ( ) num')

    # E %= T + X
    # X %= plus + T + X | minus + T + X | G.Epsilon
    # T %= F + Y
    # Y %= star + F + Y | div + F + Y | G.Epsilon
    # F %= num | opar + E + cpar

    # productions = [ 
    #     Production(E, Sentence(T, X)),
    #     Production(T, Sentence(F, Y)),
    #     Production(F, Sentence(num)),
    #     Production(Y, Sentence(star, F, Y)),
    #     Production(F, Sentence(num)),
    #     Production(Y, Sentence(star, F, Y)),
    #     Production(F, Sentence(num)),
    #     Production(Y, G.Epsilon),
    #     Production(X, Sentence(plus, T, X)),
    #     Production(T, Sentence(F, Y)),
    #     Production(F, Sentence(num)),
    #     Production(Y, Sentence(star, F, Y)),
    #     Production(F, Sentence(num)),
    #     Production(Y, G.Epsilon),
    #     Production(X, Sentence(plus, T, X)),
    #     Production(T, Sentence(F, Y)),
    #     Production(F, Sentence(num)),
    #     Production(Y, G.Epsilon),
    #     Production(X, Sentence(plus, T, X)),
    #     Production(T, Sentence(F, Y)),
    #     Production(F, Sentence(num)),
    #     Production(Y, G.Epsilon),
    #     Production(X, G.Epsilon),
    # ]

    # result = parse_tree_left(productions, 'test.svg')

    G = Grammar()
    E = G.NonTerminal('E', True)
    T, F = G.NonTerminals('T F')
    plus, minus, star, div, opar, cpar, num = G.Terminals('+ - * / ( ) int')

    E %= E + plus + T | T # | E + minus + T 
    T %= T + star + F | F # | T + div + F
    F %= num | opar + E + cpar

    productions = [ 
        Production(F, Sentence(num)),
        Production(T, Sentence(F)),
        Production(E, Sentence(T)),
        Production(F, Sentence(num)),
        Production(T, Sentence(F)),
        Production(F, Sentence(num)),
        Production(T, Sentence(T, star, F)),
        Production(E, Sentence(E, plus, T)),
    ]

    result = parse_tree_right(productions, 'test1.svg')