import math
import operator
import os
import string

import nltk
import sys

FILE_MATCHES = 2
SENTENCE_MATCHES = 5


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files_map = {}

    for file in os.listdir(directory):
        path = os.path.join(directory, file)
        with open(path, 'r', encoding="utf8") as content_file:
            content = content_file.read()
            files_map[file] = content
    return files_map


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    tokens = nltk.word_tokenize(document)
    tokens = [each_string.lower() for each_string in tokens]

    # Remove non-letter tokens and irrelevant words
    to_be_removed = []
    for word in tokens:
        if word in string.punctuation:
            to_be_removed.append(word)
        elif word in nltk.corpus.stopwords.words("english"):
            to_be_removed.append(word)
    for word in to_be_removed:
        tokens.remove(word)

    return tokens


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    # Create dictionary mapping each word to the documents in which it appears
    docs_with_word = {}
    for file in documents:
        for word in documents[file]:
            # If "word" is an existing key in "docs_with_word":
            if word in docs_with_word.keys():
                docs_with_word[word].add(file)
            else:
                docs_with_word[word] = set()
                docs_with_word[word].add(file)

    # Create dictionary mapping each word to its idf
    word_idf = {}
    num_of_docs = len(documents)
    for word in docs_with_word:
        appearances = len(docs_with_word[word])
        word_idf[word] = math.log(num_of_docs/appearances)

    return word_idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # Create dictionary to keep track of sum of tf-idf
    tf_idf_sum = {}
    file_names = files.keys()
    for file_name in file_names:
        tf_idf_sum[file_name] = 0

    # Update tf_idf_sum
    for query_word in query:
        for file in files:

            # Get number of times the query's word appears on file
            tf = 0
            for word in files[file]:
                if word == query_word:
                    tf += 1

            # Calculate tf-idf and update tf_idf_sum
            tf_idf = tf * idfs[query_word]
            tf_idf_sum[file] += tf_idf

    # Sort files by their tf_idf_sum
    sorted_sum = sorted(tf_idf_sum.items(), key=operator.itemgetter(1), reverse=True)
    ranking = []
    for file_tuple in sorted_sum:
        ranking.append(file_tuple[0])

    return ranking[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # Create dictionary to keep track of sum of idf of each sentence
    sentence_idf_sum = {}
    sentences_keys = sentences.keys()
    for sentence_key in sentences_keys:
        sentence_idf_sum[sentence_key] = 0

    # Update sentence_idf_sum dictionary
    for sentence in sentences:
        for word in query:
            if word in sentences[sentence]:
                sentence_idf_sum[sentence] += idfs[word]

    # Sort sentences by their idf_sum
    sorted_sum = sorted(sentence_idf_sum.items(), key=operator.itemgetter(1), reverse=True)

    # Append an item to list for later loop
    sorted_sum.append("END")

    # Make final ranked list, untying with “matching word measure”
    ranking = []
    i = 0
    while i in range(len(sorted_sum)):

        # If last item of list, break the loop
        if sorted_sum[i] == "END":
            break

        # If sentence is not tied with the next one, add it to ranking list
        if sorted_sum[i][1] != sorted_sum[i+1][1]:
            if sorted_sum[i][0] not in ranking:
                ranking.append(sorted_sum[i][0])
            i += 1

        # If sentence tied with next one, untie by “matching word measure”
        else:

            first = i
            while sorted_sum[i][1] == sorted_sum[i+1][1]:
                i += 1
            last = i

            # Make list with tied sentences
            tied = []
            for j in range(first, last+1):
                tied.append(sorted_sum[j][0])

            # Sort tied list by “matching word measure”
            term_density = {}
            for sent in tied:
                term_density[sent] = 0
            for sent in tied:

                sent_words = sentences[sent]
                for word in sent_words:
                    if word in query:
                        term_density[sent] += 1
                term_density[sent] /= len(sent_words)

            sorted_tied = sorted(term_density.items(), key=operator.itemgetter(1), reverse=True)

            # Add sorted tied items to ranking list
            for sent in sorted_tied:
                if sent[0] not in ranking:
                    ranking.append(sent[0])

    return ranking[:n]


if __name__ == "__main__":
    main()
