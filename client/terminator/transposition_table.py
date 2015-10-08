from constants import POS_INF, NEG_INF

class TranspositionTable(object):

    def __init__(self):
        self._table = {}
        
    def look_up(self, key, depth):
        if key in self._table:
            tt_move, tt_value, tt_depth = self._table[key]
            if tt_depth >= depth:
                return tt_move, tt_value
        return None

    def store(self, key, depth, move, value):
        if key in self._table:
            _, tt_value, tt_depth = self._table[key]
            if tt_depth < depth and tt_value < value:
                self._table[key] = move, value, depth
        else:
            self._table[key] = move, value, depth