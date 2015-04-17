import time
import sys
import random
import copy

from base_client import LiacBot
from board import Board

WHITE = 1
BLACK = -1
NONE = 0
POS_INF = sys.maxint
NEG_INF = -sys.maxint - 1

# BOT =========================================================================
class Bot(LiacBot):
	name = 'Bot'

	def __init__(self):
		super(Bot, self).__init__()
		self.last_move = None
	
	# gera o proximo movimento a partir da poda alfa e beta
	def __alphaBeta(self, board, depth, alpha, beta):
		if depth == 0:
			return (None, board.value())
		bestValue = NEG_INF
		moves = board.generate()
		# TODO sort moves
		for move in moves:
			newBoard = copy.deepcopy(board)
			newBoard.move(move)
			val = -(self.__alphaBeta(newBoard, depth - 1, -beta, -alpha)[1])
			if bestValue < val:
				bestValue = val
				bestMove = move
			alpha = max(alpha, val)
			if alpha > beta:
				break
		return (bestMove, bestValue)

	def on_move(self, state):
		print 'Generating a move...',
		board = Board(state)

		if state['bad_move']:
			print state['board']
			raw_input()

		move = self.__alphaBeta(board, 2, NEG_INF, POS_INF)[0]

		self.last_move = move
		print move
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






