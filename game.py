import collections
import colored  # type: ignore
import enum
import json
import random
import sys
import typing
import unionfind


class InvalidPlay(ValueError):
    pass


class Point(typing.NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def adjacent_points(self) -> typing.List["Point"]:
        return [
            self + direction
            for direction in Direction
        ]

    def adjacent_edges(self) -> typing.List[typing.Tuple["Point", "Point"]]:
        return [
            (self, point)
            for point in self.adjacent_points()
        ]


class TermColor(enum.Enum):
    BLUE = "blue"
    GREEN = "light_green"
    RED = "red"
    YELLOW = "yellow"
    DARK_GREEN = "dark_green"
    GREY = "light_slate_grey"
    DARK_GREY = "grey_0"
    WHITE = "white"
    NONE = "default"


class MaxTurns(enum.IntEnum):
    TWO_PLAYERS = 6
    STANDARD = 12
    MIGHTY_DUEL = 24


class DrawNum(enum.IntEnum):
    THREE = 3
    FOUR = 4


class GridSize(enum.IntEnum):
    STANDARD = 5
    MIGHTY_DUEL = 7


class BonusPoints(enum.IntEnum):
    HARMONY = 5
    MIDDLE_KINGDOM = 10


class Rule(enum.Flag):
    TWO_PLAYERS = enum.auto()
    THREE_PLAYERS = enum.auto()
    FOUR_PLAYERS = enum.auto()
    DYNASTY = enum.auto()
    MIDDLE_KINGDOM = enum.auto()
    HARMONY = enum.auto()
    MIGHTY_DUEL = enum.auto()

    @classmethod
    def default(cls, num_players):
        if num_players == 2:
            return cls.TWO_PLAYERS
        if num_players == 3:
            return cls.THREE_PLAYERS
        if num_players == 4:
            return cls.FOUR_PLAYERS


class Suit(enum.Enum):
    FOREST = enum.auto()
    GRASS = enum.auto()
    MINE = enum.auto()
    SWAMP = enum.auto()
    WATER = enum.auto()
    WHEAT = enum.auto()
    CASTLE = enum.auto()
    NONE = enum.auto()

    @classmethod
    def from_string(cls, string: str):
        return {
            "forest": cls.FOREST,
            "grass": cls.GRASS,
            "mine": cls.MINE,
            "swamp": cls.SWAMP,
            "water": cls.WATER,
            "wheat": cls.WHEAT,
        }[string]

    def to_string(self) -> str:
        return {
            Suit.FOREST:    "forest",
            Suit.GRASS:     "grass",
            Suit.MINE:      "mine",
            Suit.SWAMP:     "swamp",
            Suit.WATER:     "water",
            Suit.WHEAT:     "wheat",
        }[self]

    def to_color(self) -> TermColor:
        return {
            Suit.FOREST:    TermColor.DARK_GREEN,
            Suit.GRASS:     TermColor.GREEN,
            Suit.MINE:      TermColor.DARK_GREY,
            Suit.SWAMP:     TermColor.GREY,
            Suit.WATER:     TermColor.BLUE,
            Suit.WHEAT:     TermColor.YELLOW,
            Suit.CASTLE:    TermColor.WHITE,
            Suit.NONE:      TermColor.NONE,
        }[self]
    
    def colored_print(self, txt) -> TermColor:
        return {
            Suit.FOREST:    "\033[0;32m" + str(txt) + "\033[0m",
            Suit.GRASS:     "\033[1;32m" + str(txt) + "\033[0m",
            Suit.MINE:      "\033[1;30m" + str(txt) + "\033[0m",
            Suit.SWAMP:     "\033[0;33m" + str(txt) + "\033[0m",
            Suit.WATER:     "\033[0;34m" + str(txt) + "\033[0m",
            Suit.WHEAT:     "\033[1;33m" + str(txt) + "\033[0m",
            Suit.CASTLE:    "\033[0;36m" + str(txt) + "\033[0m",
            Suit.NONE:      txt,
        }[self]


class Direction(Point, enum.Enum):
    EAST = Point(0, 1)
    SOUTH = Point(1, 0)
    WEST = Point(0, -1)
    NORTH = Point(-1, 0)

    @classmethod
    def from_string(cls, string: str):
        return {
            "east":     cls.EAST,
            "e":        cls.EAST,
            "south":    cls.SOUTH,
            "s":        cls.SOUTH,
            "west":     cls.WEST,
            "w":        cls.WEST,
            "north":    cls.NORTH,
            "n":        cls.NORTH,
        }[string]

    @classmethod
    def opposite(cls, direction):
        return {
            cls.EAST:   cls.WEST,
            cls.SOUTH:  cls.NORTH,
            cls.WEST:   cls.EAST,
            cls.NORTH:  cls.SOUTH,
        }[direction]


class Player(typing.NamedTuple):
    name: str
    color: TermColor


class Tile(typing.NamedTuple):
    suit: Suit
    crowns: int = 0

    def valid_connection(self, tile: typing.Optional["Tile"]) -> bool:
        return tile is not None and any(
            (
                tile.suit == Suit.CASTLE,
                tile.suit == self.suit,
            )
        )

    def __str__(self) -> str:
        if self.suit == Suit.CASTLE:
            char = "C"
        elif self.crowns == 0:
            char = " "
        else:
            char = self.crowns

        return colored.stylize(
            char,
            colored.fg("white") + colored.bg(self.suit.to_color().value)
        )


class Domino(typing.NamedTuple):
    number: int
    left: Tile
    right: Tile

    def __str__(self):
        return f"{self.left.suit.colored_print(self.left.crowns)}{self.right.suit.colored_print(self.left.crowns)}"

    def __repr__(self):
        return f"{self.left.suit.colored_print(self.left.crowns)}{self.right.suit.colored_print(self.left.crowns)}"


class Play:

    def __init__(
        self,
        domino: Domino,
        point: Point,
        direction: Direction,
    ):
        self.domino = domino
        self.point = point
        self.direction = direction
        self.points = (self.point, self.point + self.direction)

    def left_adjacent_points(self) -> typing.List[Point]:
        return [
            point for point in self.point.adjacent_points()
            if point != self.point + self.direction
        ]

    def right_adjacent_points(self) -> typing.List[Point]:
        return [
            point for point in (self.point + self.direction).adjacent_points()
            if point != self.point
        ]

    def adjacent_edges(self) -> typing.List[typing.Tuple[Point, Point]]:
        return [
            edge for edge in (
                self.point.adjacent_edges()
                + (self.point + self.direction).adjacent_edges()
            )
            if edge not in (
                (self.point, self.point + self.direction),
                (self.point + self.direction, self.point),
            )
        ]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Play):
            raise NotImplementedError
        return (
            self.domino == other.domino
            and (
                (
                    self.point == other.point
                    and self.direction == other.direction
                )
                or
                (
                    self.point == other.point + other.direction
                    and self.direction == Direction.opposite(other.direction)
                )
            )
        )

    def __hash__(self):
        return hash((self.domino, self.point, self.direction))

    @classmethod
    def flipped(cls, play):
        return cls(
            domino=play.domino,
            point=play.point + play.direction,
            direction=Direction.opposite(play.direction)
        )

    def __repr__(self):
        return f"{self.point.x} {self.point.y} {self.direction.name[:4]}"


class Grid:

    def __init__(self, size: int):
        self.size = size
        self.max_size = size * 2 - 1
        half = size - 1
        self.middle = Point(half, half)

        self.grid = [[None] * self.max_size for _ in range(self.max_size)]
        self.grid[half][half] = Tile(Suit.CASTLE)

        self.max_x = half
        self.max_y = half
        self.min_x = half
        self.min_y = half

    def __getitem__(self, point: Point) -> typing.Optional[Tile]:
        return self.grid[point.x][point.y]

    def __setitem__(self, point: Point, tile: Tile) -> None:
        self.min_x, self.min_y = self.min(point)
        self.max_x, self.max_y = self.max(point)
        self.grid[point.x][point.y] = tile

    def min(self, point: Point) -> Point:
        return Point(min(self.min_x, point.x), min(self.min_y, point.y))

    def max(self, point: Point) -> Point:
        return Point(max(self.max_x, point.x), max(self.max_y, point.y))

    def within_grid(self, point: Point) -> bool:
        return 0 <= point.x < self.max_size and 0 <= point.y < self.max_size

    def within_bounds(self, point: Point) -> bool:
        min_x, min_y = self.min(point)
        max_x, max_y = self.max(point)
        return max_x - min_x < self.size and max_y - min_y < self.size

    def within_grid_and_bounds(self, point: Point) -> bool:
        return self.within_grid(point) and self.within_bounds(point)

    def bounded(self) -> bool:
        """Returns False if there are any tiles placed outside the grid."""
        return not any(
            any(
                (
                    self.grid[1][i],
                    self.grid[self.size - 2][i],
                    self.grid[i][1],
                    self.grid[i][self.size - 2],
                )
            )
            for i in range(2,  self.max_size - 1)
        )

    def __str__(self):
        return "".join(
            (
                "\n↓",
                "".join(map(str, range(self.max_size))),
                "\n",
                "\n".join(
                    str(i)
                    + "".join(
                        str(tile) if tile else " "
                        for tile in row
                    )
                    for i, row in enumerate(self.grid)
                ),
            )
        )


class Board:

    def __init__(
        self,
        rules: Rule,
        discards: typing.List[Domino] = None,
        union: unionfind.UnionFind = None,
    ):
        self.rules = rules

        if discards is None:
            discards = []
        self.discards = discards

        if union is None:
            union = unionfind.UnionFind()
        self.union = union

        self.grid = Grid(
            GridSize.MIGHTY_DUEL
            if Rule.MIGHTY_DUEL in self.rules
            else GridSize.STANDARD
        )

    # SCORING

    def crowns_and_tiles(self) -> typing.List[typing.Tuple[int, int]]:
        return [
            (
                sum(
                    self.grid[point].crowns
                    for point in points
                ),
                len(points)
            )
            for points in self.union.groups()
        ]

    def points(self):
        return (
            sum(
                crowns * tiles
                for crowns, tiles in self.crowns_and_tiles()
            )
            + self.middle_kingdom_points()
            + self.harmony_points()
        )

    def crowns(self):
        return sum(crowns for crowns, tiles in self.crowns_and_tiles())

    def middle_kingdom_points(self):
        return (
            BonusPoints.MIDDLE_KINGDOM
            * int(Rule.MIDDLE_KINGDOM in self.rules)
            * int(self.grid.bounded())
        )

    def harmony_points(self):
        return (
            BonusPoints.HARMONY
            * int(Rule.HARMONY in self.rules)
            * int(not self.discards)
        )

    # PLAYING

    def discard(self, domino: Domino) -> None:
        self.discards.append(domino)

    def play(self, play: Play):
        if not self.valid_play(play):
            raise InvalidPlay

        self.add_to_grid(play)
        self._unionise(play)

    def valid_play(self, play: Play):
        return all(
            (
                self._vacant(play),
                self._play_within_bounds(play),
                self._valid_adjacent(play),
            )
        )

    def _vacant(self, play: Play) -> bool:
        return all(
            self.grid[point] is None
            for point in play.points
        )

    def _play_within_bounds(self, play: Play) -> bool:
        return all(
            self.grid.within_grid_and_bounds(point)
            for point in play.points
        )

    def _valid_adjacent(self, play: Play) -> bool:
        return (
            any(
                play.domino.left.valid_connection(self.grid[point])
                for point in play.left_adjacent_points()
                if self.grid.within_grid_and_bounds(point)
            )
            or any(
                play.domino.right.valid_connection(self.grid[point])
                for point in play.right_adjacent_points()
                if self.grid.within_grid_and_bounds(point)
            )
        )

    def add_to_grid(self, play: Play) -> None:
        left, right = play.points
        self.grid[left] = play.domino.left
        self.grid[right] = play.domino.right

    def _unionise(self, play: Play) -> None:
        for a, b in play.adjacent_edges():
            domino_tile = self.grid[a]
            grid_tile = self.grid[b]
            if grid_tile is None:
                continue
            if domino_tile.suit == grid_tile.suit:
                self.union.join(a, b)

    # VALIDATION

    def valid_plays(
            self,
            domino: Domino,
            point: typing.Optional[Point] = None,
            direction: typing.Optional[Direction] = None
    ) -> typing.Set[Play]:
        """Returns a list of all valid plays given a Play containing a domino."""
        valid = set()
        directions = (direction,) if direction else Direction
        points = (point,) if point else self._vacant_points()
        for point in points:
            for direction in directions:
                new_play = Play(
                    domino=domino,
                    point=point,
                    direction=direction
                )
                if self.valid_play(new_play):
                    valid.add(new_play)
                flipped = Play.flipped(new_play)
                if self.valid_play(flipped):
                    valid.add(flipped)

        return valid

    def _vacant_points(self) -> typing.List[Point]:
        vacant_points = []
        seen: set = set()
        frontier = collections.deque((self.grid.middle, ))
        while frontier:

            point = frontier.popleft()
            if point in seen:
                continue
            else:
                seen.add(point)

            for new_point in point.adjacent_points():
                if not self.grid.within_grid_and_bounds(new_point):
                    continue
                if self.grid[new_point] is None:
                    vacant_points.append(new_point)
                else:
                    frontier.append(new_point)

        return vacant_points

    def __str__(self) -> str:
        return str(self.grid)


class Line:

    def __init__(
        self,
        dominos: typing.List[Domino]
    ):
        self.line = [
            [None, domino]
            for domino in sorted(dominos)
        ]

    def pop(self) -> Domino:
        return self.line.pop(0)

    def empty(self) -> bool:
        return not self.line

    def choose(
        self,
        player: Player,
        index: int = None,
        domino: Domino = None,
    ) -> None:
        # TODO: Refactor
        if domino is not None:
            index = self.line.index(domino)
        self.line[index][0] = player

    def __str__(self):
        return "\n".join(
            (
                colored.stylize(" ", colored.bg(player.color.value))
                if player else str(i)
            )
            + f": {domino}"
            for i, (player, domino) in enumerate(self.line)
        )


class Dominoes(list):

    def to_dict(self) -> typing.List[
        typing.Dict[
            str,
            typing.Union[
                str,
                typing.Dict[
                    str,
                    str,
                ],
            ]
        ]
    ]:
        return [
            {
                "number": domino.number,
                "left": {
                    "suit": domino.left.suit.to_string(),
                    "crowns": domino.left.crowns,
                },
                "right": {
                    "suit": domino.right.suit.to_string(),
                    "crowns": domino.right.crowns,
                },
            }
            for domino in self
        ]

    def to_json(self, filename: str) -> None:
        with open(filename, 'w') as f:
            json.dump(
                self.to_dict(),
                f,
                indent=2,
            )

    @classmethod
    def from_json(cls, filename):
        with open(filename) as f:
            dominos = json.load(f)
            return cls(
                Domino(
                    number=int(domino["number"]),
                    left=Tile(
                        suit=Suit.from_string(domino["left"]["suit"]),
                        crowns=int(domino["left"]["crowns"]),
                    ),
                    right=Tile(
                        suit=Suit.from_string(domino["right"]["suit"]),
                        crowns=int(domino["right"]["crowns"]),
                    ),
                )
                for domino in dominos
            )


class Deck:

    def __init__(
        self,
        dominoes: Dominoes,
        deck_size: int,
        draw_num: int,
    ):
        self.deck_size = deck_size
        self.draw_num = draw_num
        self.deck = random.sample(dominoes, self.deck_size)

    def empty(self):
        return not bool(self.deck)

    def draw(self):
        """Returns n dominos from the shuffled deck."""
        return [
            self.deck.pop()
            for _ in range(self.draw_num)
        ]


class Game:
    boards: typing.Dict[Player, Board]
    line: Line
    turn_num: int = 0

    def __init__(
        self,
        dominoes: Dominoes,
        players: typing.List[Player],
        rules: Rule = None,
    ):
        self.players = players
        self.rules = Rule.default(len(self.players))
        self.add_rules(rules)

        self.deck = Deck(
            dominoes=dominoes,
            draw_num=self.num_to_draw(),
            deck_size=self.deck_size(),
        )

        self.boards = {
            player: Board(rules=self.rules)
            for player in self.players
        }

        self.set_initial_order()

    def add_rules(self, rules):
        if rules:
            self.rules |= rules

    def max_turns(self):
        if Rule.TWO_PLAYERS in self.rules:
            return MaxTurns.TWO_PLAYERS
        elif Rule.MIGHTY_DUEL in self.rules:
            return MaxTurns.MIGHTY_DUEL
        else:
            return MaxTurns.STANDARD

    def deck_size(self):
        turns = self.max_turns() * len(self.players)
        if Rule.TWO_PLAYERS in self.rules:
            turns *= 2
        return turns

    def num_to_draw(self):
        if Rule.THREE_PLAYERS in self.rules:
            return DrawNum.THREE
        elif self.rules in (
            Rule.MIGHTY_DUEL,
            Rule.FOUR_PLAYERS,
            Rule.TWO_PLAYERS,
        ):
            return DrawNum.FOUR
        else:
            raise ValueError

    def set_initial_order(self):
        self.order = random.sample(self.players, len(self.players))
        if Rule.TWO_PLAYERS in self.rules:
            self.order *= 2

    def start(self):
        self.turn_num += 1
        while not self.deck.empty():
            self.turn()
        self.final_score()

    def draw(self):
        self.line = Line(self.deck.draw())

    def select(self):
        while self.order:
            player = self.order.pop(0)
            print(self.line)
            print(self.boards[player])
            while True:
                try:
                    self.line.choose(
                        player,
                        int(input(f"{player.name}: ")),
                    )
                except (InvalidPlay, ValueError):
                    continue
                else:
                    break

    def place(self):
        while not self.line.empty():
            player, domino = self.line.pop()
            board = self.boards[player]

            print(board)
            print(domino)
            while True:
                try:
                    plays = board.valid_plays(domino)
                    if not plays:
                        board.discard(domino)
                        break
                    print(plays)
                    x, y, direction = input("x y direction: ").split()
                    board.play(
                        Play(
                            domino=domino,
                            point=Point(int(x), int(y)),
                            direction=Direction.from_string(direction),
                        )
                    )
                except InvalidPlay:
                    continue
                else:
                    break

            self.order.append(player)

    def turn(self):
        print(f"Turn {self.turn_num}/{self.max_turns()}")
        self.draw()
        self.select()
        self.place()
        self.turn_num += 1

    def final_score(self):
        for i, (points, crowns, player) in enumerate(
            sorted(
                (
                    (
                        self.boards[player].points(),
                        self.boards[player].crowns(),
                        player,
                    )
                    for player in self.players
                ),
                reverse=True,
            ),
            start=1
        ):
            print(f"{i}. {player.name}: {points}")
            print(self.boards[player])


def split_stream(func, filename):
    def wrapper(*args, **kwargs):
        with open(filename, "a") as f:
            output = func(*args, **kwargs)
            print(output, file=f)
        return output
    return wrapper


if __name__ == "__main__":

    if len(sys.argv) == 2:
        input = split_stream(input, sys.argv[1])

    filename = "kingdomino.json"

    dominoes = Dominoes.from_json(filename)

    random.seed(0)

    players = [
        Player(
            name=input(f"Player {i+1} name: "),
            color=color
        )
        for i, color in zip(
            range(int(input("How many players? (2/3/4): "))),
            TermColor,
        )
    ]

    game = Game(
        dominoes=dominoes,
        players=players,
    )
    game.start()
