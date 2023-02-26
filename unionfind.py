import typing

T = typing.TypeVar('T')

class Node:

    def __init__(
        self,
        item: T,
        parent: "Node"=None,
        size: int=1
    ):
        self.item = item
        self.parent = self
        self.size = size

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            raise NotImplementedError
        return self.item == other.item

    def __hash__(self) -> int:
        return hash(self.item)

    def __repr__(self) -> str:
        if self.parent == self:
            return f"{self.__class__.__name__}({self.item})"
        else:
            return (
                f"{self.__class__.__name__}("
                + ", ".join(
                    f"{key}={value!r}"
                    for key, value in self.__dict__.items()
                )
                + ")"
            )

class UnionFind:

    def __init__(self, _nodes=None):
        if _nodes is None:
            _nodes = {}
        self._nodes = _nodes

    def _to_node(self, item: T) -> Node:
        if item not in self._nodes:
            self._nodes[item] = Node(item)
        return self._nodes[item]

    def find(self, item: T) -> T:
        return self._find(self._to_node(item)).item

    def _find(self, node: Node) -> Node:
        if node.parent == node:
            return node
        else:
            node.parent = self._find(node.parent)
            return node.parent

    def join(self, x: T, y: T) -> None:

        node_x = self._to_node(x)
        node_y = self._to_node(y)

        root_x = self._find(node_x)
        root_y = self._find(node_y)

        if root_x == root_y:
            return

        if root_x.size < root_y.size:
            root_x, root_y = root_y, root_x

        root_y.parent = root_x
        root_x.size += root_y.size

    def groups(self) -> typing.FrozenSet[typing.FrozenSet[T]]:

        d: typing.Dict[Node, set] = {}
        for node in self._nodes.values():
            root = self._find(node)
            if root not in d:
                d[root] = set()
            d[root].add(node)

        return frozenset(
            frozenset(node.item for node in nodes)
            for nodes in d.values()
        )
    def __str__(self) -> str:
        return str(self.groups())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(_nodes={self._nodes!r})"




if __name__ == "__main__":
    u = UnionFind()
    u.join(0, 1)
    u.join(2, 3)
    u.join(3, 4)
    for i in range(6):
        print(u.find(i))
    print(u.groups())
    print(u)
    print(repr(u))
