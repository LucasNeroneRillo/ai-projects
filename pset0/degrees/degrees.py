import csv
import sys

from util import Node, QueueFrontier, NodeSet

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # Initialize variables that keep track of "examined/to examine"
    frontier = QueueFrontier()
    examined_set = NodeSet()

    # Add source's neighbors to frontier
    movie_ids = people[source]["movies"]
    for movie_id in movie_ids:
        node = Node(source, None, movie_id)
        frontier.add(node)

    while True:
        # If frontier's length is zero, there is no relation between source and target
        if frontier.empty():
            return None

        # If frontier contains the target, find the used path
        if frontier.contains_person_id(target):
            
            # Add target to examined_set
            for node in frontier.frontier:
                if node.person_id == target:
                    examined_set.append(node)
                    break
                
            # Find used path
            path = []
            current_child = target
            
            """
            - Find any movie where child and parent stared together
            - Make tuple (movie_id, child)
            - Parent becomes target
            - Repeat until child is source
            """
            while not current_child == source:
                current_node = examined_set.get_node_with_child_as(current_child)
                path.append((current_node.movie, current_node.person_id))
                current_child = current_node.parent_id
            
            path.reverse()
            return path

        # Else, update frontier and examined_set
        else:
            # Create a copy from frontier so you can clean it
            tmp = frontier.frontier
            frontier.frontier = []

            # Use frontier's copy to look neighbors of every person
            for node in tmp:

                # If person was not analised yet, analise them
                if not examined_set.contains_person_id(node.person_id):
                    neighbors = neighbors_for_person(node.person_id)

                    for neighbor in neighbors:
                        childNode = Node(person_id=neighbor[1], parent_id=node.person_id, movie=neighbor[0])
                        frontier.add(childNode)
                        examined_set.append(node)


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()