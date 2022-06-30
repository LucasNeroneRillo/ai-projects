class Node():
    def __init__(self, person_id, parent_id, movie):
        self.person_id = person_id
        self.parent_id = parent_id
        self.movie = movie


class QueueFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_person_id(self, person_id1):
        return any(node.person_id == person_id1 for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


class NodeSet():
    def __init__(self):
        self.list = set()

    def append(self, node):
        self.list.add(node)

    def contains_person_id(self, person_id):
        return any(node.person_id == person_id for node in self.list)

    def get_node_with_child_as(self, person_id):
        for node in self.list:
            if node.person_id == person_id:
                return node
        return None