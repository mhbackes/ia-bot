import time
import sys
from operator import itemgetter
from constants import POS_INF, NEG_INF

from base_client import LiacBot
from board import Board
from transposition_table import TranspositionTable

# BOT =========================================================================
class Bot(LiacBot):
	name = 'Optimus Prime'

	def __init__(self, depth):
		super(Bot, self).__init__()
		self.transpositionTable = TranspositionTable()
		self._depth = depth
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
			return (move, value)
		
		moves = board.generate()
		if moves == []: # DRAW
			return (None, 0)
		sorted(moves, key=itemgetter(1), reverse=True)
		
		firstChild = True
		currentBoardValue = board.value
		currentBoardString = board.string
		for moveValue in moves:
			(move, value) = moveValue
			board.move_with_val(move, value)
			if firstChild:
				firstChild = False
				bestValue = -(self.__negaScout(board, depth - 1, -beta, -alpha)[1])
				bestMove = move
			else:
				score = -(self.__negaScout(board, depth - 1, -alpha -1, -alpha)[1])
				if alpha < score and score < beta:
					score = -(self.__negaScout(board, depth - 1, -beta, -alpha)[1])
				if bestValue < score:
					bestValue = score
					bestMove = move
			board.unmove_with_val_str(move, currentBoardValue, currentBoardString)
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
		moves = sorted(moves, key=itemgetter(1), reverse=True)
		
		bestValue = NEG_INF
		(bestMove, _) = moves[0]
		for moveValue in moves:
			(move, _) = moveValue
			
			board.move(move)
			val = -(self.__alphaBeta(board, depth - 1, -beta, -alpha)[1])
			board.unmove(move)
			
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
		self.color = state["who_moves"]
		print 'Generating a move...\n',
		board = Board(state)

		if state['bad_move']:
			print state['board']
			raw_input()

		t0 = time.time()
		move, value = self.__negaScout(board, self._depth, NEG_INF, POS_INF)
		t = time.time()
		print 'Time:', t - t0

		self.last_move = move
		print move, ' value: ', value
		self.send_move(move[0], move[1])	

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






