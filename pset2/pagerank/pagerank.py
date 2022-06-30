import copy
import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Check if page has links attached to it
    if len(corpus[page]) == 0:

        # If so, return dictionary with equal probability for all pages
        equal_probability = 1 / len(corpus)
        dictionary = {}
        for link in corpus:
            dictionary[link] = equal_probability
        return dictionary

    # Create dictionary only with probability when not damping
    common_probability = (1 - damping_factor) * (1 / len(corpus))
    dictionary = {}
    for link in corpus:
        dictionary[link] = common_probability

    # Update dictionary adding probability when damping
    for link in corpus[page]:
        link_probability = damping_factor * (1 / len(corpus[page]))
        dictionary[link] = common_probability + link_probability

    # Return updated dictionary
    return dictionary


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Create dictionary to keep track of number of times page was visited
    count_dictionary = {}
    for link in corpus:
        count_dictionary[link] = 0

    # Update dictionary with first sample picked at random
    page = random.choice(list(corpus.keys()))
    count_dictionary[page] += 1

    # Surf through pages
    for i in range(n - 1):

        # Get probabilities for next page to be entered
        probability_dict = transition_model(corpus, page, damping_factor)

        # Create list of keys and list of values from dictionary, with same indexes
        page_list = []
        weight_list = []
        for key in probability_dict:
            page_list.append(key)
            weight_list.append(probability_dict[key])

        # Get a page using the probabilities
        one_item_list = random.choices(page_list, weights=weight_list)
        page = one_item_list[0]

        # Update count_dictionary
        count_dictionary[page] += 1

    # Calculate PageRank, updating count_dictionary to display rank
    for link in count_dictionary:
        count_dictionary[link] /= n

    # Return dictionary with ranks
    return count_dictionary


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initialize dictionary of ranks
    rank_dictionary = {}
    for page in corpus:
        rank_dictionary[page] = 1 / len(corpus)

    # Create a dictionary with pages that link to a given page
    # (Instead of pages a certain page links to)
    links_to = {}
    for page in corpus:
        links_to[page] = []
    for page in corpus:

        # If page has no links, it should link to every page
        if len(corpus[page]) == 0:
            for link in corpus:
                links_to[link].append(page)

        # Else, it links only to its links
        for link in corpus[page]:
            links_to[link].append(page)

    # Create variables for further use in following loop
    constant_term = (1 - damping_factor) / len(corpus)
    rank_copy = copy.deepcopy(rank_dictionary)

    # Loop until PageRank values converge
    update = True
    while update:

        update = False

        # Update ranks based on previous iteration
        for page in corpus:

            # Second term of iterative algorithm
            summation = 0
            for link in links_to[page]:

                # If page has no link, it links to everyone
                if len(corpus[link]) == 0:
                    num_links = len(corpus)
                else:
                    num_links = len(corpus[link])

                # Add: (link's rank divided by number of links in link)
                summation += (rank_dictionary[link] / num_links)
            summation *= damping_factor

            # Sum both terms of iterative algorithm
            probability = constant_term + summation

            # Update rank_copy for further comparision
            rank_copy[page] = probability

        # Compare updated rank with previous rank
        for page in rank_dictionary:

            # Compare ranks values in module (if big change, new iteration needed)
            if abs(rank_dictionary[page] - rank_copy[page]) > 0.001:
                update = True

        # Make rank_dictionary equal to rank_copy
        for page in rank_dictionary:
            rank_dictionary[page] = rank_copy[page]

    return rank_dictionary


if __name__ == "__main__":
    main()
