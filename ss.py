import itertools
import nltk
from nltk import Tree
from nltk.parse import CoreNLPParser

def find_np_subtrees(tree, np_subtrees):
    if isinstance(tree, Tree) and tree.label() == 'NP':
        np_subtrees.append(tree)
    for subtree in tree:
        if isinstance(subtree, Tree):
            find_np_subtrees(subtree, np_subtrees)

def permute_nps(tree):
    if isinstance(tree, Tree):
        if tree.label() == 'NP' and any(isinstance(subtree, Tree) and subtree.label() in ('CC', ',') for subtree in tree):
            nps = []
            current_np = []
            for subtree in tree:
                if subtree.label() == 'NP':
                    current_np.append(subtree)
                elif subtree.label() in ('CC', ','):
                    if current_np:
                        nps.append(current_np)
                        current_np = []
            if current_np:
                nps.append(current_np)

            if nps:
                perms = list(itertools.permutations(nps))
                return [Tree('NP', list(itertools.chain(*perm))) for perm in perms]

        return [Tree(tree.label(), [permute_nps(subtree) for subtree in tree])]
    return tree

def paraphrase_syntax_tree(tree):
    np_subtrees = []
    find_np_subtrees(tree, np_subtrees)

    paraphrased_trees = []
    for np_tree in np_subtrees:
        np_permutations = permute_nps(np_tree)
        for np_perm in np_permutations:
            paraphrased_tree = tree.copy(deep=True)
            np_tree_positions = [pos for pos in paraphrased_tree.treepositions() if paraphrased_tree[pos] == np_tree]
            if np_tree_positions:
                np_tree_position = np_tree_positions[0]
                paraphrased_tree[np_tree_position] = np_perm
                paraphrased_trees.append(paraphrased_tree)

    return paraphrased_trees


# Example usage
tree_string = """(S
(NP
(NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter))
(, ,)
(CC or)
(NP (NNP Barri) (NNP Gòtic)))
(, ,)
(VP
(VBZ has)
(NP
(NP (JJ narrow) (JJ medieval) (NNS streets))
(VP
(VBN filled)
(PP
(IN with)
(NP
(NP (JJ trendy) (NNS bars))
(, ,)
(NP (NNS clubs))
(CC and)
(NP (JJ Catalan) (NNS restaurants))))))))"""
parsed_tree = Tree.fromstring(tree_string)
paraphrased_trees = paraphrase_syntax_tree(parsed_tree)

print(parsed_tree.pretty_print())
    