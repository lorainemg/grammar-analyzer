#!/usr/bin/env python
from copy import deepcopy
from utils import get_grammar, Data, parse_grammar
from flask import Flask, render_template, request, redirect
from pprint import pprint

from src.firsts_follows import compute_firsts, compute_follows
from src.grammar_transf import left_refactoring, eliminate_recursion, eliminate_useless_prod
from src.regular_grammars import is_regular, get_automata, get_regex

from src.parsers.parser_lalr import LALRParser     
from src.parsers.parser_ll1 import ParserLL1    
from src.parsers.parser_lr1 import LR1Parser   
from src.parsers.parser_slr import SLR1Parser   


app = Flask(__name__, )
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/grammar/', methods=['GET', 'POST'])
def save_grammar():
    g = get_grammar()
    G, errors = parse_grammar(g)
    if errors:
        Data.valid = False
        return render_template('index.html', **g, errors=errors)
    Data.write_grammar(g, G)
    return render_template('index.html', **g, errors=None)


@app.route('/grammar/first_follows/')
def first_follows():
    g, G = Data.read_grammar()
    if not G:
        return redirect('/')
    firsts = compute_firsts(G)
    follows = compute_follows(G, firsts)
    return render_template('grammar/first_follows.html', **g, firsts=firsts.items(), follows=follows.items())


@app.route('/grammar/regular/')
def reg_grammar():
    g, G = Data.read_grammar()
    if not G:
        return redirect('/')

    regular = is_regular(G)
    regexpr = None
    
    if regular:  
        automaton = get_automata(G)
        regexpr = get_regex(deepcopy(automaton))
        automaton.write_to('static/img/automaton_reg.svg')
    
    return render_template('grammar/reg_grammar.html', **g, regular=regular, 
                            name='/static/img/automaton_reg.svg', regexpr=regexpr)


@app.route('/grammar/transformations/')
def transf_grammar():
    g, G = Data.read_grammar()
    if not G:
        return redirect('/')
    
    GG1 = deepcopy(G)
    eliminate_useless_prod(GG1)
    
    GG2 = deepcopy(G)
    eliminate_recursion(GG2)
    
    GG3 = deepcopy(G)
    left_refactoring(GG3)

    return render_template('grammar/transf_grammar.html', **g, 
        rec_prod=GG2.Productions,
        refactor_prod=GG3.Productions,
        no_unreach_prd=GG1.Productions
    )


def parser_ll1(word=None):
    g, G = Data.read_grammar()
    if not G:
        return redirect('/')
    
    parser = ParserLL1(G)
    firsts = compute_firsts(G)
    follows = compute_follows(G, firsts)
    table, errors = parser.build_parsing_table(firsts, follows)
    
    errors_word = False
    if word:
        try:
            parser.derivation_tree(word)
        except Exception as e:
            print(e)
            errors_word = True

    return render_template('parsers/ll1.html', **g, table=table.items(), 
                            parse_tree=True if word else False,
                            errors_word=errors_word, errors=errors,
                            word=word)


def parser_slr(text=None):
    g, G = Data.read_grammar()
    if not G:
        return redirect('/')
    
    parser = SLR1Parser(G)
    
    parser.print_automata('static/img/lr0_automaton.svg')
    
    goto = parser.goto_table
    action = parser.action_table
    errors_word = False

    if text:
        try:
            parser.derivation_tree(text)
        except:
            errors_word = True
    return render_template('parsers/slr.html', **g, 
        goto_key= goto,
        goto = zip(goto.axes[0], goto.get_values()),
        action_key=action,
        action= zip(action.axes[0], action.get_values()),
        parse_tree=True if text else False,
        errors_word=errors_word, 
        # error=None,
        word=text, 
        error=parser.errors
    )


def parser_lr(text=None):
    g, G = Data.read_grammar()
    if not G:
        return redirect('/')

    parser = LR1Parser(G)

    goto = parser.goto_table
    action = parser.action_table
    
    parser.print_automata('static/img/lr1_automaton.svg')
    errors_word = False
    if text:
        try:
            parser.derivation_tree(text)
        except:
            errors_word = True

    return render_template('parsers/lr.html', **g,
        goto_key= goto,
        goto = zip(goto.axes[0], goto.get_values()),
        action_key=action,
        action= zip(action.axes[0], action.get_values()),
        parse_tree=True if text else False,
        errors_word=errors_word,
        error=parser.errors,
        word=text
    )


def parser_lalr(text=None):
    g, G = Data.read_grammar()
    if not G:
        return redirect('/')
    
    parser = LALRParser(G)
    
    goto = parser.goto_table
    action = parser.action_table
    parser.print_automata('static/img/lalr_automaton.svg')
    errors_word = False
    if text:
        try:
            parser.derivation_tree(text)
        except:
            errors_word = True
    return render_template('parsers/lalr.html', **g,
        goto_key= goto,
        goto = zip(goto.axes[0], goto.get_values()),
        action_key=action,
        action= zip(action.axes[0], action.get_values()),
        parse_tree=True if text else False,
        errors_word=errors_word,
        error=parser.errors,
        word=text
    )


@app.route('/parser/ll1/')
def ll1():
    return parser_ll1()    


@app.route('/parser/slr/')
def slr():
    return parser_slr()


@app.route('/parser/lr/')
def lr():
    return parser_lr()


@app.route('/parser/lalr/')
def lalr():
    return parser_lalr()
    

@app.route('/parser/<ptype>/', methods=['GET', 'POST'])
def print_parse_tree(ptype):
    text = request.form.get('text')
    _, G = Data.read_grammar()
    if not G:
        return redirect('/')
    # parse_ll1(G, text)
    if ptype == '1':
        return parser_ll1(text) #redirect('/parser/ll1/')
    elif ptype == '2':
        return parser_slr(text)
    elif ptype == '3':
        return parser_lr(text)    
        # return redirect('/parser/lr/')
    elif ptype == '4':
        return parser_lalr(text) 
        # return redirect('/parser/lalr/')
    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)
