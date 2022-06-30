import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        for variable in self.domains:

            # Get set with words inconsistent with variable's unary constraints
            to_be_removed = set()
            for word in self.domains[variable]:
                if not variable.length == len(word):
                    to_be_removed.add(word)

            # Remove inconsistent words from variable's domain
            for word in to_be_removed:
                self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        changes = False

        # Check if words intersect each other
        intersect = self.crossword.overlaps[x, y]
        if intersect is not None:

            # Get characters of overlapping
            x_index = intersect[0]
            y_index = intersect[1]

            # Check for each word's consistency
            to_be_removed = set()
            for x_word in self.domains[x]:
                consistency = False

                # If one y's value satisfies constraint, word from x is consistent
                for y_word in self.domains[y]:
                    if x_word[x_index] == y_word[y_index]:
                        consistency = True

                # If word word from x is not consistent, add it to set of words to be removed
                if not consistency:
                    to_be_removed.add(x_word)
                    changes = True

            # Remove inconsistent words
            for word in to_be_removed:
                self.domains[x].remove(word)

        return changes

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # Get initial queue
        queue = []
        if arcs is not None:
            queue = arcs
        else:
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    queue.append((x, y))

        # While tuples in the queue, enforce binary consistency
        while queue:

            # Pop first item of the queue and enforce binary consistence on it
            (x, y) = queue.pop(0)

            # Check if alterations were made to x's domain
            if self.revise(x, y):

                # If all values of x were removed, impossible consistency; return false
                if not self.domains[x]:
                    return False

                # Changes were made in x, so revise consistency of x with its neighbors
                for z in self.crossword.neighbors(x):
                    if not z == y:
                        queue.append((z, x))

        # If false was not returned, consistence was successfully enforced
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if assignment.get(variable) is None:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var_1 in assignment:

            # Check if word's length is correct
            if not var_1.length == len(assignment[var_1]):
                return False

            # Check for repeated words
            for var_2 in assignment:
                if var_1 != var_2 and assignment[var_1] == assignment[var_2]:
                    return False

            # Check for consistency between neighboring values already assigned
            for neighbor in self.crossword.neighbors(var_1):
                if assignment.get(neighbor):
                    intersect = self.crossword.overlaps[var_1, neighbor]
                    i = intersect[0]
                    j = intersect[1]
                    if not assignment[var_1][i] == assignment[neighbor][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Create set with unassigned neighbors
        neighbors = self.crossword.neighbors(var) - set(assignment.keys())

        # Create map that maps var words to their counters
        words_map = {}

        # Fill words map
        for var_word in self.domains[var]:
            count = 0

            for neighbor in neighbors:
                intersect = self.crossword.overlaps[var, neighbor]
                v_index = intersect[0]
                n_index = intersect[1]

                # If neighbor word is constrained by var word, update counter
                for n_word in self.domains[neighbor]:
                    if not var_word[v_index] == n_word[n_index]:
                        count += 1

            # Update words map
            words_map[var_word] = count

        # Create list of sorted tuples by number of words that var_words constrain
        # Tuple example: (var_word, count)
        sorted_tuples = sorted(words_map.items(), key=lambda x: x[1])

        # Create list of sorted var_words based on sorted tuples
        sorted_words = []
        for tup in sorted_tuples:
            sorted_words.append(tup[0])

        return sorted_words

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Set that keeps track of variables with smallest domain
        min_set = set()

        # Variable that keeps track of size of smallest domain (initialized as biggest possible value)
        min_size = len(self.crossword.words)

        # Get set with unassigned variables
        unassigned = set(self.crossword.variables - assignment.keys())

        # Get set with smallest domain variables
        for variable in unassigned:
            v_len = len(self.domains[variable])

            # If variable's domain is smaller than smallest domain found, update set and min_size
            if v_len < min_size:
                min_set.clear()
                min_set.add(variable)
                min_size = v_len

            # If variable's domain is equal smallest domain found, only update set
            elif v_len == min_size:
                min_set.add(variable)

        # If only one variable with smallest domain, return it
        if len(min_set) == 1:
            return min_set.pop()

        # Else, if tied variables, untie using degree heuristic
        else:
            highest_degree = 0
            highest_var = None
            for var in min_set:
                degree = len(self.crossword.neighbors(var))
                if degree > highest_degree:
                    highest_degree = degree
                    highest_var = var
            return highest_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If assignment complete, return it
        if self.assignment_complete(assignment):
            return assignment

        # Get an unassigned variable and its values
        var = self.select_unassigned_variable(assignment)
        values = self.order_domain_values(var, assignment)

        # Check possible assignment for each value
        for value in values:

            # Copy assignment so that changes made to assignment are not permanent
            new_assignment = assignment.copy()

            # Check if assigning value to variable is consistent
            new_assignment[var] = value
            if self.consistent(new_assignment):

                # Recursively call function back until complete assignment or failure
                result = self.backtrack(new_assignment)

                # If complete assignment, return it
                if result is not None:
                    return result

        # Return failure
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
