import time
import sys
from operator import itemgetter
from constants import POS_INF, NEG_INF, WHITE, BLACK

from base_client import LiacBot
from board import Board
from transposition_table import TranspositionTable

# BOT =========================================================================
class Bot(LiacBot):
    name = 'Terminator'

    def __init__(self, depth):
        super(Bot, self).__init__()
        self.transpositionTable = TranspositionTable()
        self._depth = depth
        self.last_move = None
        self.color = 0

    # Retorna board de maior value da lista
    def _maxTake(self, moves):
        (move, board) = moves.head()
        maxi = (move, board, board.value)

        for (m, board) in moves:
            val = board.value
            if val > maxi[2]:
                maxi = (m, board, val)
        newMoves = moves.remove(maxi[0:2])
        return (maxi, newMoves)

    def _sortMoves(self, moves):
        for _ in range(5):
            (maxi, newMoves) = self._maxTake(moves)
        for (_, board) in moves:
            val = board.value

    def _nega_scout(self, board, depth, alpha, beta, color):
        if board.value == POS_INF:  # WIN
            return None, POS_INF * color
        if board.value == NEG_INF:  # LOSE
            return None, NEG_INF * color
        if depth == 0:
            return None, board.value * color

        # busca na tabela de transposicao
        tt_entry = self.transpositionTable.look_up(board.debug_string, depth)
        if None != tt_entry:
            move, value = tt_entry
            return move, value * value

        moves = board.generate(color)
        if not moves:  # DRAW
            return None, 0

        moves = sorted(moves, key=itemgetter(1), reverse=(color==WHITE))

        first_child = True
        for moveValue in moves:
            move, value = moveValue
            board.move(move, color, value)
            if first_child:
                first_child = False
                best_value = -(self._nega_scout(board, depth - 1, -beta, -alpha, -color)[1])
                best_move = move
            else:
                score = -(self._nega_scout(board, depth - 1, -alpha - 1, -alpha, -color)[1])
                if alpha < score < beta:
                    score = -(self._nega_scout(board, depth - 1, -beta, -alpha, -color)[1])
                if best_value < score:
                    best_value = score
                    best_move = move
            board.unmove(move, color)
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break

        # armazena na tabela de transposicao
        self.transpositionTable.store(board.string, depth, best_move, best_value * color)

        return best_move, best_value

    # gera o proximo movimento a partir da poda alfa e beta
    def _alpha_beta(self, board, depth, alpha, beta, color):
        if board.value == POS_INF:  # WIN
            return None, POS_INF * color
        if board.value == NEG_INF:  # LOSE
            return None, NEG_INF * color
        if depth == 0:
            return None, board.value * color

        # busca na tabela de transposicao
        tt_entry = self.transpositionTable.look_up(board.string, depth)
        if None != tt_entry:
            move, value = tt_entry
            return move, value * color

        moves = board.generate(color)
        if not moves:  # DRAW
            return None, 0

        moves = sorted(moves, key=itemgetter(1), reverse=(color==WHITE))

        best_move, best_value = moves[0], NEG_INF
        for moveValue in moves:
            move, _ = moveValue

            board.move(move, color)
            val = -(self._alpha_beta(board, depth - 1, -beta, -alpha, -color)[1])
            board.unmove(move, color)

            if best_value < val:
                best_value = val
                best_move = move
            alpha = max(alpha, val)
            if alpha >= beta:
                break

        # armazena na tabela de transposicao
        self.transpositionTable.store(board.string, depth, best_move, best_value * color)

        return best_move, best_value

    def on_move(self, state):
        self.color = state["who_moves"]
        print 'Talk to the hand...\n',
        board = Board(state)

        if state['bad_move']:
            print state['board']
            raw_input()

        t0 = time.time()
        move, value = self._nega_scout(board, self._depth, NEG_INF, POS_INF, self.color)
        #value *= self.color
        t = time.time()
        print 'Time:', t - t0

        self.last_move = move
        print move, ' value: ', value
        self.send_move(move[0], move[1])

    def on_game_over(self, state):
        if state['draw']:
            print 'No problemo.'
        elif state['winner'] == self.color:
            print 'You have been terminated.'
        else:
            print 'I\'ll be back.'
        # sys.exit()

# =============================================================================

if __name__ == '__main__':
    color = 0
    port = 50100
    depth = 4

    if len(sys.argv) > 1:
        if sys.argv[1] == 'black':
            color = 1
            port = 50200

    if len(sys.argv) > 2:
        depth = int(sys.argv[2])

    bot = Bot(depth)
    bot.port = port

    bot.start()
