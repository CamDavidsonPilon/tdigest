import operator
from bintrees.rbtree import RBTree, Node


class AccumulationTree(RBTree):
    def __init__(self, mapper, reducer=operator.add, zero=0):
        RBTree.__init__(self)
        self._zero = zero
        self._mapper = mapper
        self._reducer = reducer

        self._dirty_nodes = set()

        class AccumulatingNode(Node):
            """Internal object, represents a tree node."""
            __slots__ = ['accumulation']

            def __init__(node, key, value):
                Node.__init__(node, key, value)
                node.accumulation = self._mapper(value)

            def __setitem__(node, key, value):
                Node.__setitem__(node, key, value)
                self._dirty_nodes.add(node.key)

        self._Node = AccumulatingNode


    def _new_node(self, key, value):
        """Create a new tree node."""
        self._count += 1
        node = self._Node(key, value)
        return node

    def insert(self, key, value):
        RBTree.insert(self, key, value)
        self._update_dirty_nodes()

    def remove(self, key):
        try:
            RBTree.remove(self, key)
        finally:
            self._update_dirty_nodes()

    def _get_full_accumulation(self, node):
        if not node:
            return self._zero
        else:
            return node.accumulation

    def _get_right_accumulation(self, node, lower):
        if not node:
            return self._zero
        if(lower <= node.key):
            return self._reducer(
                self._reducer(
                    self._get_right_accumulation(node[0], lower),
                    self._get_full_accumulation(node[1]),
                ),
                self._mapper(node.value),
            )
        else:
            return self._get_right_accumulation(node[1], lower)

    def _get_left_accumulation(self, node, upper):
        if not node:
            return self._zero
        if(upper > node.key):
            return self._reducer(
                self._reducer(
                    self._get_full_accumulation(node[0]),
                    self._get_left_accumulation(node[1], upper),
                ),
                self._mapper(node.value),
            )
        else:
            return self._get_left_accumulation(node[0], upper)

    def _get_accumulation(self, node, lower, upper):
        if not node or lower > upper:
            return self._zero
        if node < lower:
            return self._get_accumulation(node[1])
        if node >= upper:
            return self._get_accumulation(node[0])
        return self.reducer(
            self._reducer(
                self._get_right_accumulation(node[0], lower),
                self._get_left_accumulation(node[1], upper),
            ),
            self._mapper(node.value),
        )

    def get_accumulation(self, lower, upper):
        return self._get_accumulation(self._root, lower, upper)

    def get_left_accumulation(self, upper):
        return self._get_left_accumulation(self._root, upper)

    def get_right_accumulation(self, lower):
        return self._get_right_accumulation(self._root, lower)

    def get_full_accumulation(self):
        return self._get_full_accumulation(self._root)

    def _update_dirty_nodes(self):
        for key in self._dirty_nodes:
            path = self._path_to_key(key)
            self._update_accumulation(path)
        self._dirty_nodes.clear()

    def _path_to_key(self, key):
        path = []
        node = self._root
        while True:
            if not node:
                break
            path.append(node)
            if node.key == key:
                break
            elif node.key < key:
                node = node[0]
            else:
                node = node[1]
        return path

    def _update_accumulation(self, nodes):
        for x in reversed(nodes):
            if x[0] and x[1]:
                x.accumulation = self._reducer(
                    self._reducer(
                        x[0].accumulation,
                        x[1].accumulation,
                    ),
                    self._mapper(x.value)
                )
            elif x[0]:
                x.accumulation = self._reducer(
                    x[0].accumulation,
                    self._mapper(x.value),
                )
            elif x[1]:
                x.accumulation = self._reducer(
                    x[1].accumulation,
                    self._mapper(x.value),
                )
            else:
                x.accumulation = self._mapper(x.value)

