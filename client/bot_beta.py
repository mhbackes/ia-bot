import time
import sys
import random
from operator import itemgetter, attrgetter

from __builtin__ import str
from twisted.persisted.aot import Instance
import copy
import sys

from base_client import LiacBot
from transposition_table import TranspositionTable

WHITE = 1
BLACK = -1
NONE = 0
POS_INF = 10000
NEG_INF = -10000

# ============================================================================
class Board(object):
    def __init__(self, state):
        self.cells = [[None for j in xrange(8)] for i in xrange(8)]
        self.my_pieces = []
        self.enemy_pieces = []
        self.my_team = 0
        
        PIECES = {
            'r': Rook,
            'p': Pawn,
            'b': Bishop,
            'q': Queen,
            'n': Knight,
        }

        self.my_team = state['who_moves']
        c = state['board']
        i = 0

        for row in xrange(7, -1, -1):
            for col in xrange(0, 8):
                if c[i] != '.':
                    cls = PIECES[c[i].lower()]
                    team = BLACK if c[i].lower() == c[i] else WHITE

                    piece = cls(self, team, (row, col))
                    self.cells[row][col] = piece

                    if team == self.my_team:
                        self.my_pieces.append(piece)
                    else:
                        self.enemy_pieces.append(piece)

                i += 1
        
        self.string = self._calculate_string()
        self.value = self.calculate_value()

    def __getitem__(self, pos):
        if not 0 <= pos[0] <= 7 or not 0 <= pos[1] <= 7:
            return None

        return self.cells[pos[0]][pos[1]]

    def __setitem__(self, pos, value):
        self._cells[pos[0]][pos[1]] = value

    def __lt__(self, other):
        return self.value < other.value
    
    def _calculate_string(self):
        string = ''
        for i in xrange(8):
            for j in xrange(8):
                piece = self.cells[i][j]
                if  piece == None:
                    string += '.'
                else:
                    string += piece.to_string()
        return string

    def is_empty(self, pos):
        return self[pos] is None
    
    def generate(self):
        moves = []
        for piece in self.my_pieces:
            ms = piece.generate()
            ms = [(piece.position, m) for m in ms]
            moves.extend(ms)
        move_board = []
        for move in moves:
            board = copy.deepcopy(self)
            board.move(move)
            pair = (move, board)
            move_board.append(pair)
        return move_board
    
    def pawns(self, pieces):
        pawns = []
        for piece in pieces:
            if isinstance(piece, Pawn):
                pawns.append(piece)
        return pawns
    
    # retorna  1 se ganhou o jogo
    #         -1 se perdeu o jogo
    #          0 se o jogo nao acabou
    def is_end(self):
        enemy_pawns = self.pawns(self.enemy_pieces)
        if enemy_pawns == []:
            return 1
        my_pawns = self.pawns(self.my_pieces)
        if my_pawns == []:
            return -1

        if self.my_team == WHITE:
            my_last_row = 7
            enemy_last_row = 0
        else:
            my_last_row = 0
            enemy_last_row = 7
            
        for pawn in my_pawns:
            if pawn.position[0] == my_last_row:
                return 1
            
        for pawn in enemy_pawns:
            if pawn.position[0] == enemy_last_row:
                return -1
        return 0
    
    
    # move a peca selecionada, atualiza as pecas do oponente  se uma peca foi
    # eliminada e inverte as pecas dos jogadores
    def move(self, move):
        (old, new) = move
        toBeRemoved = self.cells[new[0]][new[1]]
        if toBeRemoved != None:
            self.enemy_pieces.remove(toBeRemoved)
        self.cells[new[0]][new[1]] = self.cells[old[0]][old[1]]
        self.cells[new[0]][new[1]].position = new
        self.cells[old[0]][old[1]] = None
        
        temp = self.my_pieces
        self.my_pieces = self.enemy_pieces
        self.enemy_pieces = temp
        self.string = self._calculate_string()
        self.value = self.calculate_value()
        
    def calculate_value(self):
            end = self.is_end()
            if end == 1:
                    return POS_INF
            if end == 0:
                    return NEG_INF
            value = 0.0
            for piece in self.my_pieces:
                    value += piece.value()
            for piece in self.enemy_pieces:
                    value -= piece.value()
                
    # avaliacao heuristica do tabuleiro atual:
    # Q*9 + N*3 + P*1 - q*9 - n*3 - p*1
    def calculate_value(self):
        end = self.is_end()
        if end == 1:
            return POS_INF
        if end == -1:
            return NEG_INF
        value = 0.0
        for piece in self.my_pieces:
            value += piece.value()
        for piece in self.enemy_pieces:
            value -= piece.value()
        return value

class Piece(object):
    def __init__(self):
        self.board = None
        self.team = None
        self.position = None
        self.type = None

    def generate(self):
        pass
        
    def value(self):
        pass
    
    def to_string(self):
        pass

    def is_opponent(self, piece):
        return piece is not None and piece.team != self.team

class Pawn(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def generate(self):
        moves = []
        my_row, my_col = self.position

        d = self.team

        # Movement to 1 forward
        pos = (my_row + d*1, my_col)
        if self.board.is_empty(pos):
            moves.append(pos)

        # Normal capture to right
        pos = (my_row + d*1, my_col+1)
        piece = self.board[pos]
        if self.is_opponent(piece):
            moves.append(pos)

        # Normal capture to left
        pos = (my_row + d*1, my_col-1)
        piece = self.board[pos]
        if self.is_opponent(piece):
            moves.append(pos)

        return moves    

    # detecta se esta em uma posicao para ser comido por outra peca        
    def __to_be_eaten(self):
        d = self.team
        my_row, my_col = self.position

        # detects pawn or queen on both diagonals
        pos_left = (my_row + d, my_col - 1)
        pos_right = (my_row + d, my_col + 1)
                
        piece = self.board[pos_left]
        if self.is_opponent(piece):
            if type(piece) is (Pawn):
                return True
            elif type(piece) is (Queen):
                return True
                
        piece = self.board[pos_right]
        if self.is_opponent(piece):
            if type(piece) is (Pawn):
                return True
        elif type(piece) is (Queen):
                return True
        return False

    def value(self):
        row, col = self.position
        if col < 4:
            col_value = col * 0.1
        else:
            col_value = (7 - col) * 0.1
        if self.team == WHITE:
            row_value = row * 0.1
        else:
            row_value = (7 - row) * 0.1
        val = 1 + row_value + col_value
                
        if self.__to_be_eaten == True:
            val -= 0.5

        return val
    
    def to_string(self):
        if self.team == WHITE:
            return 'C'
        else:
            return 'c'

class Rook(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position
        
    def _col(self, dir_):
        my_row, my_col = self.position
        d = -1 if dir_ < 0 else 1
        for col in xrange(1, abs(dir_)):
            yield (my_row, my_col + d*col)

    def _row(self, dir_):
        my_row, my_col = self.position

        d = -1 if dir_ < 0 else 1
        for row in xrange(1, abs(dir_)):
            yield (my_row + d*row, my_col)

    def _gen(self, moves, gen, idx):
        for pos in gen(idx):
            piece = self.board[pos]
            
            if piece is None: 
                moves.append(pos)
                continue
            
            elif piece.team != self.team:
                moves.append(pos)

            break

    def generate(self):
        moves = []

        my_row, my_col = self.position
        self._gen(moves, self._col, 8-my_col) # RIGHT
        self._gen(moves, self._col, -my_col-1) # LEFT
        self._gen(moves, self._row, 8-my_row) # TOP
        self._gen(moves, self._row, -my_row-1) # BOTTOM
        
    def value(self):
        return 5

class Bishop(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def _gen(self, moves, row_dir, col_dir):
        my_row, my_col = self.position

        for i in xrange(1, 8):
            row = row_dir*i
            col = col_dir*i
            q_row, q_col = my_row+row, my_col+col

            if not 0 <= q_row <= 7 or not 0 <= q_col <= 7:
                break

            piece = self.board[q_row, q_col]
            if piece is not None:
                if piece.team != self.team:
                    moves.append((q_row, q_col))
                break

            moves.append((q_row, q_col))

    def generate(self):
        moves = []

        self._gen(moves, row_dir=1, col_dir=1) # TOPRIGHT
        self._gen(moves, row_dir=1, col_dir=-1) # TOPLEFT
        self._gen(moves, row_dir=-1, col_dir=-1) # BOTTOMLEFT
        self._gen(moves, row_dir=-1, col_dir=1) # BOTTOMRIGHT

        return moves
        
    def value(self):
        return 3

class Queen(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def _col(self, dir_):
        my_row, my_col = self.position
        
        d = -1 if dir_ < 0 else 1
        for col in xrange(1, abs(dir_)):
            yield (my_row, my_col + d*col)

    def _row(self, dir_):
        my_row, my_col = self.position

        d = -1 if dir_ < 0 else 1
        for row in xrange(1, abs(dir_)):
            yield (my_row + d*row, my_col)

    def _gen_rook(self, moves, gen, idx):
        for pos in gen(idx):
            piece = self.board[pos]
            
            if piece is None: 
                moves.append(pos)
                continue
            
            elif piece.team != self.team:
                moves.append(pos)

            break

    def _gen_bishop(self, moves, row_dir, col_dir):
        my_row, my_col = self.position

        for i in xrange(1, 8):
            row = row_dir*i
            col = col_dir*i
            q_row, q_col = my_row+row, my_col+col

            if not 0 <= q_row <= 7 or not 0 <= q_col <= 7:
                break

            piece = self.board[q_row, q_col]
            if piece is not None:
                if piece.team != self.team:
                    moves.append((q_row, q_col))
                break

            moves.append((q_row, q_col))

    def generate(self):
        moves = []

        my_row, my_col = self.position
        self._gen_rook(moves, self._col, 8-my_col) # RIGHT
        self._gen_rook(moves, self._col, -my_col-1) # LEFT
        self._gen_rook(moves, self._row, 8-my_row) # TOP
        self._gen_rook(moves, self._row, -my_row-1) # BOTTOM
        self._gen_bishop(moves, row_dir=1, col_dir=1) # TOPRIGHT
        self._gen_bishop(moves, row_dir=1, col_dir=-1) # TOPLEFT
        self._gen_bishop(moves, row_dir=-1, col_dir=-1) # BOTTOMLEFT
        self._gen_bishop(moves, row_dir=-1, col_dir=1) # BOTTOMRIGHT

        return moves
    
    def value(self):
        return 9
    
    def to_string(self):
        if self.team == WHITE:
            return 'Q'
        else:
            return 'q'

class Knight(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def _gen(self, moves, row, col):
        if not 0 <= row <= 7 or not 0 <= col <= 7:
            return

        piece = self.board[(row, col)]
        if piece is None or self.is_opponent(piece):
            moves.append((row, col))

    def generate(self):
        moves = []
        my_row, my_col = self.position

        self._gen(moves, my_row+1, my_col+2)
        self._gen(moves, my_row+1, my_col-2)
        self._gen(moves, my_row-1, my_col+2)
        self._gen(moves, my_row-1, my_col-2)
        self._gen(moves, my_row+2, my_col+1)
        self._gen(moves, my_row+2, my_col-1)
        self._gen(moves, my_row-2, my_col+1)
        self._gen(moves, my_row-2, my_col-1)

        return moves
        
    def value(self):
        return 3
    
    def to_string(self):
        if self.team == WHITE:
            return 'N'
        else:
            return 'n'
        
# BOT =========================================================================
class Bot(LiacBot):
    name = 'Bot'

    def __init__(self):
        super(Bot, self).__init__()
        self.transpositionTable = TranspositionTable()
        self.last_move = None
        
    # Retorna board de maior value da lista
    def __maxTake(self, moves):
        (move, board) = moves.head()
        maxi = (move, board, board.value)
        
        for (m, board) in moves:
            val = board.value
            if val > maxi[2]:
                maxi = (m, board, val)
        newMoves = moves.remove(maxi[0:2])
        return (maxi, newMoves)        
    
    def __sortMoves(self, moves):
        for _ in range(5):
            (maxi, newMoves) = self.__maxTake(moves)
        for (_, board) in moves:
            val = board.value
    
    def __negaScout(self, board, depth, alpha, beta):
        if board.value == POS_INF: # WIN
            return (None, POS_INF)
        if board.value == NEG_INF: # LOSE
            return (None, NEG_INF)
        if depth == 0:
            return (None, board.value)
        
        # busca na tabela de transposicao
        ttEntry = self.transpositionTable.lookUp(board.string, depth)
        if ttEntry != None:
            move, value = ttEntry
            return move, value
        
        moves = board.generate()
        if moves == []: # DRAW
            return (None, 0)
        sorted(moves, key=itemgetter(1), reverse=True)
        
        firstChild = True
        for moveBoard in moves:
            (move, newBoard) = moveBoard
            if firstChild:
                firstChild = False
                bestValue = -(self.__negaScout(newBoard, depth - 1, -beta, -alpha)[1])
                bestMove = move
            else:
                score = -(self.__alphaBeta(newBoard, depth - 1, -alpha -1, -alpha)[1])
                if alpha < score and score < beta:
                    score = -(self.__alphaBeta(newBoard, depth - 1, -beta, -alpha)[1])
                if bestValue < score:
                    bestValue = score
                    bestMove = move
            alpha = max(alpha, bestValue)
            if alpha >= beta:
                break
                
        # armazena na tabela de transposicao
        self.transpositionTable.store(board.string, depth, bestMove, bestValue)
        
        return (bestMove, bestValue)
        
    # gera o proximo movimento a partir da poda alfa e beta
    def __alphaBeta(self, board, depth, alpha, beta):
        if board.value == POS_INF: # WIN
            return (None, POS_INF)
        if board.value == NEG_INF: # LOSE
            return (None, NEG_INF)
        if depth == 0:
            return (None, board.value)
        
        # busca na tabela de transposicao
        ttEntry = self.transpositionTable.lookUp(board.string, depth)
        if ttEntry != None:
            move, value = ttEntry
            return move, value
        
        moves = board.generate()
        if moves == []: # DRAW
            return (None, 0)
        
        sorted(moves, key=itemgetter(1), reverse=True)
        
        bestValue = NEG_INF
        bestMove = moves[0][1]
        for moveBoard in moves:
            (move, newBoard) = moveBoard
            val = -(self.__negaScout(newBoard, depth - 1, -beta, -alpha)[1])
            if bestValue < val:
                bestValue = val
                bestMove = move
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        
        # armazena na tabela de transposicao
        self.transpositionTable.store(board.string, depth, bestMove, bestValue)
        
        return (bestMove, bestValue)

    def on_move(self, state):
        print 'Generating a move...\n',
        board = Board(state)

        if state['bad_move']:
            print state['board']
            raw_input()

        t0 = time.time()
        move, value = self.__alphaBeta(board, 3, NEG_INF, POS_INF)
        t = time.time()
        print 'Time:', t - t0

        self.last_move = move
        print move, ' value: ', value
        self.send_move(move[0], move[1])
        self.color = state["who_moves"]

    def on_game_over(self, state):
        if state['draw']:
            print 'Draw!'
        elif state['winner'] == self.color:
            print 'We won!'
        else:
            print 'We lost!'
        # sys.exit()
# =============================================================================

if __name__ == '__main__':
    color = 0
    port = 50100

    if len(sys.argv) > 1:
        if sys.argv[1] == 'black':
            color = 1
            port = 50200

    bot = Bot()
    bot.port = port

    bot.start()


