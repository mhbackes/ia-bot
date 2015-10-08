from constants import *

# MODELS ======================================================================
class Board(object):
	def __init__(self, state):
		self.cells = [[None for j in xrange(8)] for i in xrange(8)]
		self.white_pieces = []
		self.black_pieces = []
		self.removed_pieces = []

		PIECES = {
			'r': Rook,
			'p': Pawn,
			'b': Bishop,
			'q': Queen,
			'n': Knight,
		}
		c = state['board']
		i = 0

		for row in xrange(7, -1, -1):
			for col in xrange(0, 8):
				if c[i] != '.':
					cls = PIECES[c[i].lower()]
					team = BLACK if c[i].lower() == c[i] else WHITE

					piece = cls(self, team, (row, col))
					self.cells[row][col] = piece

					if team == WHITE:
						self.white_pieces.append(piece)
					else:
						self.black_pieces.append(piece)
				i += 1

		self.string = self._calculate_string()
		self.value = self._calculate_value()

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
				if None == piece:
					string += '.'
				else:
					string += piece.to_string()
		return string

	def is_empty(self, pos):
		return self[pos] is None

	def generate(self, color):
		moves = []
		pieces = self.white_pieces if color == 1 else self.black_pieces
		for piece in pieces:
			ms = piece.generate()
			ms = [(piece.position, m) for m in ms]
			moves.extend(ms)
		move_value = []
		for move in moves:
			self.move(move, color)
			value = self.value
			self.unmove(move, color)
			pair = (move, value)
			move_value.append(pair)
		return move_value

	def _current_pieces(self, color):
		return self.white_pieces if color == WHITE else self.black_pieces

	def _enemy_pieces(self, color):
		return self.white_pieces if color == BLACK else self.black_pieces

	@staticmethod
	def pawns(pieces):
		pawns = []
		for piece in pieces:
			if isinstance(piece, Pawn):
				pawns.append(piece)
		return pawns

	# retorna  1 se branco ganhou
	#         -1 se preto ganhou
	#          0 se o jogo nao acabou
	def is_end(self):

		black_pawns = self.pawns(self.black_pieces)
		if not black_pawns:
			return 1
		white_pawns = self.pawns(self.white_pieces)
		if not white_pawns:
			return -1

		WHITE_LAST_ROW = 7
		BLACK_LAST_ROW = 0

		for pawn in white_pawns:
			if pawn.position[0] == WHITE_LAST_ROW:
				return 1

		for pawn in black_pawns:
			if pawn.position[0] == BLACK_LAST_ROW:
				return -1
		return 0

	# color = cor da peca a ser movida
	def move(self, move, color, value=None, string=None):
		enemy_pieces = self._enemy_pieces(color)
		(old, new) = move
		(new_row, new_col) = new
		(old_row, old_col) = old
		to_be_removed = self.cells[new_row][new_col]
		self.removed_pieces.append( (to_be_removed, self.string, self.value) )
		if None != to_be_removed:
			enemy_pieces.remove(to_be_removed)
		self.cells[new_row][new_col] = self.cells[old_row][old_col]
		self.cells[new_row][new_col].position = new
		self.cells[old_row][old_col] = None

		self.string = self._calculate_string() if None == string else string
		self.value = self._calculate_value() if None == value else value

	# color = cor da peca a ser desmovida
	def unmove(self, move, color):
		enemy_pieces = self._enemy_pieces(color)
		(old, new) = move
		(new_row, new_col) = new
		(old_row, old_col) = old
		self.cells[old_row][old_col] = self.cells[new_row][new_col]
		self.cells[old_row][old_col].position = old
		last_removed, self.string, self.value = self.removed_pieces.pop()
		self.cells[new_row][new_col] = last_removed
		if None != last_removed:
			enemy_pieces.append(last_removed)

	def _calculate_value(self):
		end = self.is_end()
		if end == WHITE:
			return POS_INF
		if end == BLACK:
			return NEG_INF
		value = 0
		for piece in self.white_pieces:
			value += piece.value()
		for piece in self.black_pieces:
			value -= piece.value()
		return value

	def debug_string(self):
		string = ''
		for i in range(7,-1,-1):
			for j in range(8):
				piece = self.cells[i][j]
				if None == piece:
					string += '.'
				else:
					string += piece.to_string()
				string += ' '
			string+='\n'
		return string


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
		pos = (my_row + d * 1, my_col)
		if self.board.is_empty(pos):
			moves.append(pos)

		# Normal capture to right
		pos = (my_row + d * 1, my_col + 1)
		piece = self.board[pos]
		if self.is_opponent(piece):
			moves.append(pos)

		# Normal capture to left
		pos = (my_row + d * 1, my_col - 1)
		piece = self.board[pos]
		if self.is_opponent(piece):
			moves.append(pos)

		return moves

	def value(self):
		row, col = self.position
		t = self.team

		val = 300 + PIECE_SQUARE_TABLE_PAWN[t][row][col]
		return min(val, POS_INF)

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
			yield (my_row, my_col + d * col)

	def _row(self, dir_):
		my_row, my_col = self.position

		d = -1 if dir_ < 0 else 1
		for row in xrange(1, abs(dir_)):
			yield (my_row + d * row, my_col)

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
		self._gen(moves, self._col, 8 - my_col)  # RIGHT
		self._gen(moves, self._col, -my_col - 1)  # LEFT
		self._gen(moves, self._row, 8 - my_row)  # TOP
		self._gen(moves, self._row, -my_row - 1)  # BOTTOM

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
			row = row_dir * i
			col = col_dir * i
			q_row, q_col = my_row + row, my_col + col

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

		self._gen(moves, row_dir=1, col_dir=1)  # TOPRIGHT
		self._gen(moves, row_dir=1, col_dir=-1)  # TOPLEFT
		self._gen(moves, row_dir=-1, col_dir=-1)  # BOTTOMLEFT
		self._gen(moves, row_dir=-1, col_dir=1)  # BOTTOMRIGHT

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
			yield (my_row, my_col + d * col)

	def _row(self, dir_):
		my_row, my_col = self.position

		d = -1 if dir_ < 0 else 1
		for row in xrange(1, abs(dir_)):
			yield (my_row + d * row, my_col)

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
			row = row_dir * i
			col = col_dir * i
			q_row, q_col = my_row + row, my_col + col

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
		self._gen_rook(moves, self._col, 8 - my_col)  # RIGHT
		self._gen_rook(moves, self._col, -my_col - 1)  # LEFT
		self._gen_rook(moves, self._row, 8 - my_row)  # TOP
		self._gen_rook(moves, self._row, -my_row - 1)  # BOTTOM
		self._gen_bishop(moves, row_dir=1, col_dir=1)  # TOPRIGHT
		self._gen_bishop(moves, row_dir=1, col_dir=-1)  # TOPLEFT
		self._gen_bishop(moves, row_dir=-1, col_dir=-1)  # BOTTOMLEFT
		self._gen_bishop(moves, row_dir=-1, col_dir=1)  # BOTTOMRIGHT

		return moves

	def value(self):
		row, col = self.position
		t = self.team
		val = 1500 + PIECE_SQUARE_TABLE_QUEEN[t][row][col]
		return min(val, POS_INF)

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

		self._gen(moves, my_row + 1, my_col + 2)
		self._gen(moves, my_row + 1, my_col - 2)
		self._gen(moves, my_row - 1, my_col + 2)
		self._gen(moves, my_row - 1, my_col - 2)
		self._gen(moves, my_row + 2, my_col + 1)
		self._gen(moves, my_row + 2, my_col - 1)
		self._gen(moves, my_row - 2, my_col + 1)
		self._gen(moves, my_row - 2, my_col - 1)

		return moves

	def value(self):
		row, col = self.position
		t = self.team
		val = 350 + PIECE_SQUARE_TABLE_KNIGHT[t][row][col]
		return min(val, POS_INF)

	def to_string(self):
		if self.team == WHITE:
			return 'N'
		else:
			return 'n'

# =============================================================================

