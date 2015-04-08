import time
import sys
import random

from base_client import LiacBot
from board import Board

WHITE = 1
BLACK = -1
NONE = 0

# BOT =========================================================================
class Bot(LiacBot):
	name = 'Bot'

	def __init__(self):
		super(Bot, self).__init__()
		self.last_move = None

	def on_move(self, state):
		print 'Generating a move...',
		board = Board(state)

		if state['bad_move']:
			print state['board']
			raw_input()

		moves = board.generate()

		# necessario implementar
		move = random.choice(moves) # <----------------------------------------
		# necessario implementar

		self.last_move = move
		print move
		self.send_move(move[0], move[1])
		color = state["who_moves"]
		print color

	def on_game_over(self, state):
		if state['draw']:
			print 'Draw!'
		elif state['winner'] == color:
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






