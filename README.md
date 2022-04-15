# Grammar Analyzer
The objective of this project is to design a program that allows certain processing of grammars to be carried out. The project has a visual interface that allows both describing the grammar and reporting the results.

## Objective

Given a grammar (represented in a plain text format) perform the following analyses:

- Compute the **First** and **Follow** sets.
- Determine if the grammar is **LL(1)**. If so, show the table of the non-recursive predictive method and give the derivation trees for a given set of strings. If not, please report a conflict string along with the explanation of the conflict. Transform the grammar to remove common prefixes and immediate left recursion.
- Perform analysis similar to the previous one but with the **SLR**, **LR** and **LALR** parsers.
- If the grammar is regular, convert it to automaton and regular expression.
- Show version of grammar without immediate left recursion, common prefixes, and unnecessary productions.