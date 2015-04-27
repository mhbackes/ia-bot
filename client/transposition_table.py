
class TranspositionTable(object):

    def __init__(self):
        self._table = {}
        
    def lookUp(self, key, depth):
        if key in self._table:
            move, value, move_depth = self._table[key]
            if move_depth >= depth:
                return (move, value)
        return None

    def store(self, key, depth, move, value):
        if key in self._table:
            _, _, tt_depth = self._table[key]
            if tt_depth >= depth:
                return
        self._table[key] = (move, value, depth)
        