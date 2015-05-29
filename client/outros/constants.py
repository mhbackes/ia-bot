## ---------------------------------- TEAMS -----------------------------------
WHITE = 1
BLACK = -1
NONE = 0
## ---------------------------------- TEAMS -----------------------------------

## ---------------------------- NUMERIC CONSTANTS -----------------------------
POS_INF = 10000
NEG_INF = -10000
INF = POS_INF
## ---------------------------- NUMERIC CONSTANTS -----------------------------

## --------------------------- PIECE SQUARE TABLES ----------------------------
PIECE_SQUARE_TABLE_PAWN = {
                            WHITE :
                                [[  0,  0,  0,  0,  0,  0,  0,  0],
                                 [  5,  5,  5,-10,-10,  5,  5,  5],
                                 [  5, 15, 20, 20, 20, 20, 15,  5],
                                 [ 10, 20, 30, 40, 40, 30, 20, 10],
                                 [ 20, 30, 40, 60, 60, 40, 30, 20],
                                 [ 40, 50, 70, 80, 80, 70, 50, 40],
                                 [100,100,100,100,100,100,100,100],
                                 [INF,INF,INF,INF,INF,INF,INF,INF]],
                            BLACK :
                                [[INF,INF,INF,INF,INF,INF,INF,INF],
                                 [100,100,100,100,100,100,100,100],
                                 [ 40, 50, 70, 80, 80, 70, 50, 40],
                                 [ 15, 30, 40, 60, 60, 40, 30, 15],
                                 [ 10, 20, 30, 40, 40, 30, 20, 10],
                                 [  5, 15, 20, 20, 20, 20, 15,  5],
                                 [  5,  5,  5,-10,-10,  5,  5,  5],
                                 [  0,  0,  0,  0,  0,  0,  0,  0]],
                            }

PIECE_SQUARE_TABLE_KNIGHT = {
                            WHITE :
                                [[-15,-10, -5, -5, -5, -5,-10,-15],
                                 [-10,-10, -5,  0,  0, -5,-10,-10],
                                 [ -5,  5,  5,  8,  8,  5,  5, -5],
                                 [ -5,  0,  8, 18, 18,  8,  0, -5],
                                 [ -5,  5,  5,  8,  8,  5,  5, -5],
                                 [ -5,  0,  5,  5,  5,  5,  0, -5],
                                 [-10,-10, -5,  0,  0, -5,-10,-10],
                                 [-15,-10, -5, -5, -5, -5,-10,-15]],
                            BLACK :
                                [[-15,-10, -5, -5, -5, -5,-10,-15],
                                 [-10,-10, -5,  0,  0, -5,-10,-10],
                                 [ -5,  0,  5,  5,  5,  5,  0, -5],
                                 [ -5,  5,  5,  8,  8,  5,  5, -5],
                                 [ -5,  0,  8, 18, 18,  8,  0, -5],
                                 [ -5, -5, -5,  8,  8, -5, -5, -5],
                                 [-10,-10, -5,  0,  0, -5,-10,-10],
                                 [-15,-10, -5, -5, -5, -5,-10,-15]]
                            }

PIECE_SQUARE_TABLE_QUEEN = {
                            WHITE :
                                [[-10,-10,-10,-10,-10,-10,-10,-10],
                                 [ -5,  0,  0,  0,  0,  0,  0, -5],
                                 [ -5,  0,  0,  0,  0,  0,  0, -5],
                                 [  0,  0,  0,  0,  0,  0,  0, -5],
                                 [ -5,  0,  0,  5,  5,  0,  0, -5],
                                 [ -5,  0,  0,  0,  0,  0,  0, -5],
                                 [ -5,  5,  5, 10, 10,  5,  5, -5],
                                 [-10, -5, -5, -5, -5, -5, -5,-10]],
                            BLACK :
                                [[-10, -5, -5, -5, -5, -5, -5,-10],
                                 [ -5,  5,  5, 10, 10,  5,  5, -5],
                                 [ -5,  0,  0,  0,  0,  0,  0, -5],
                                 [ -5,  0,  0,  5,  5,  0,  0, -5],
                                 [ -5,  0,  0,  0,  0,  0,  0,  0],
                                 [ -5,  0,  0,  0,  0,  0,  0, -5],
                                 [ -5,  0,  0,  0,  0,  0,  0, -5],
                                 [-10,-10,-10,-10,-10,-10,-10,-10]]
                            }
## --------------------------- PIECE SQUARE TABLES -------------------------