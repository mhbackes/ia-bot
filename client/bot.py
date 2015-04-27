import time
import sys
import random
from operator import itemgetter, attrgetter

from base_client import LiacBot
from board import Board
from transposition_table import TranspositionTable

WHITE = 1
BLACK = -1
NONE = 0
POS_INF = 10000
NEG_INF = -10000

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






