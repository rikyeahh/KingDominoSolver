from easyAI import TwoPlayerGame, Human_Player, AI_Player, Negamax
import itertools as it
from game import Dominoes, Board, Deck, Play, Rule


class KingDomino(TwoPlayerGame):

    def __init__(self, players=None):
        # must do these to fit the framework
        self.players = players
        self.nplayer = 1
        self.current_player = 1
        # fill the pile of cards
        self.pile = Deck(Dominoes.from_json("kingdomino2.json"), deck_size=10, draw_num=4)
        self.board1 = Board(Rule.MIGHTY_DUEL)
        self.board2 = Board(Rule.MIGHTY_DUEL)
        self.previously_picked_cards1 = [None, None]
        self.previously_picked_cards2 = [None, None]
        self.cards_on_board = self.pile.draw()

    def possible_moves(self):
        if self.nplayer == 1:
            current_board = self.board1
            prev_picked_cards = self.previously_picked_cards1
        else:
            current_board = self.board2
            prev_picked_cards = self.previously_picked_cards2

        cards_to_pick_next_turn = ["01", "02", "03", "12", "13", "23"] # need just 1 pick each turn?
        
        # for first turn, no previously picked cards
        if prev_picked_cards[0] == None:
            return cards_to_pick_next_turn
            
        positions_for_1st_card = list(current_board.valid_plays(prev_picked_cards[0]))
        positions_for_2nd_card = list(current_board.valid_plays(prev_picked_cards[1]))
        
        positions_to_place = positions_for_1st_card + positions_for_2nd_card
            
        # last turn
        if self.pile.empty():
            return list(it.product("last turn", positions_to_place))
        
        return list(it.product(cards_to_pick_next_turn, positions_to_place))

    def make_move(self, move):

        if self.nplayer == 1:
            current_board = self.board1
            prev_picked_cards = self.previously_picked_cards1
        else:
            current_board = self.board2
            prev_picked_cards = self.previously_picked_cards2
            self.cards_on_board = self.pile.draw()

        # if first move
        if type(move) == str:
            prev_picked_cards[0] = self.cards_on_board[int(move[0])]
            prev_picked_cards[1] = self.cards_on_board[int(move[1])]
            return
        print("move", move, "picked", str(prev_picked_cards), "pile size", len(self.pile.deck), "is valid", current_board.valid_play(move[1]))
        
        # if last move
        if move[0] == 'last turn':
            current_board.play(move[1])
        
        cards_picked = move[0]
        prev_picked_cards[0] = self.cards_on_board[int(cards_picked[0])]
        prev_picked_cards[1] = self.cards_on_board[int(cards_picked[1])]
        current_board.play(move[1])

    def is_over(self):
        return self.pile.empty()

    def show(self):
        pass

    def scoring(self):
        if self.nplayer == 1:
            current_board = self.board1
        else:
            current_board = self.board2
        return current_board.points() if self.is_over() else 0

from easyAI import solve_with_iterative_deepening

r,d,m = solve_with_iterative_deepening(
    game=KingDomino(),
    ai_depths=range(3,5),
    win_score=100
)