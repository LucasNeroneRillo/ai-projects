import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | Conj NP VP | Conj VP | S S
NP -> N | Det N | Det Adj N | Det MultAdj N | P N | NP NP | P NP | NP Adv
MultAdj -> Adj Adj | Adj MultAdj
VP -> V | V NP | V Adv | Adv V | V Adv NP | Adv V NP 
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # Perform tokenization
    tokens = nltk.word_tokenize(sentence)

    # Remove non-letter tokens and lowercase lettered tokens
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()
        if not tokens[i].isalpha():
            tokens.remove(tokens[i])

    return tokens


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np = []

    # For each subtree:
    for subtree in tree.subtrees():

        # If it is a NP, check for inner NPs
        if subtree.label() == "NP":

            no_inner_np = True
            for sub_subtree in subtree.subtrees():

                # If inner NPs found, subtree won't be added to list
                # As all tree is a subtree of itself, second statement must be done
                if sub_subtree.label() == "NP" and sub_subtree != subtree:
                    no_inner_np = False
            if no_inner_np:
                np.append(subtree)

    return np


if __name__ == "__main__":
    main()
