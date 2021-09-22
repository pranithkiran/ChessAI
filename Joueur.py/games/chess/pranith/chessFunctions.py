import time

NEG_INF = -2147000000
POS_INF =  2147000000



WHITE = 1
BLACK = -1
PIECE_CODES = {'k' : -6, 'q' : -5, 'r' : -4, 'b' : -3, 'n' : -2, 'p' : -1,
               'K' :  6, 'Q' :  5, 'R' :  4, 'B' :  3, 'N' :  2, 'P' :  1}
PIECE_ALPHA = {-6  :'k', -5  :'q', -4  :'r',  -3 :'b', -2  :'n', -1  :'p',
                6  :'K',  5  :'Q',  4  :'R',   3 :'B',  2  :'N',  1  :'P'} 

pieces = [1, 2, 3, 4, 5, 6, 0, -1, -2, -3, -4, -5, -6]

def boardGenerator( fen_string ):
    '''
    converts the input FEN string to list of list of integers, where pieces are represented in integers
    '''
    board = []
    fen_sections = fen_string.split()
    rank_list = fen_sections[0].split('/')

    for rank in rank_list:
        rank_pieces = []

        for piece in rank:
            if piece.isdigit():
                for _ in range(int(piece)):
                    rank_pieces.append(0)
            else:
                rank_pieces.append( PIECE_CODES[piece] )
        board.append(rank_pieces)

    return board


def printBoard( board ):
    '''
    to visualize given FEN string in a 2D list 
    '''

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] < 0:
                print(" ",board[i][j], end = "")
            else:
                print("  ",board[i][j], end = "")
        print()


def copyBoard( origboard ) :
    '''
    makes a copy of given original board
    '''
    copy = [ [ origboard[i][j] for j in range(8) ] for i in range(8) ]
    return copy


def isOnBoard( i, j ):
    '''
    checks if the piece is on board or not
    '''
    if i < 0 or i > 7 or j < 0 or j > 7:
        return False
    else :
        return True


def nextBoard( board, move ) :
    '''
    PRE: move is a valid move.
    Updates the given board after making a move 
    '''
    i, j, xi, xj, promo = move

    tempBoard = copyBoard( board )

    piece = tempBoard[i][j]
    tempBoard[xi][xj] = piece
    tempBoard[i][j] = 0
    if promo != 0 and promo != 111 : # If this is a promotion
        tempBoard[xi][xj] = promo

    return tempBoard



STANDARD_FILE = {0 : 'a', 1 : 'b', 2 : 'c', 3 : 'd', 4 : 'e', 5 : 'f', 6 : 'g', 7 : 'h'}

def getUCI( move ):
    '''
    converts the move to the standard UCI form
    '''
    if move is None :
        return '-'
    i,j, xi,xj, promo = move
    ucim = STANDARD_FILE[j] + str(8-i) + STANDARD_FILE[xj] + str(8-xi)
    if promo != 0 and promo != 111 :
        ucim = ucim + PIECE_ALPHA[promo]
    return ucim




# -----------------------------------------------------------
PIECE_RAYS = {
2 : [ [2,1], [2,-1], [1,-2], [-1,-2], [-2,-1], [-2,1], [-1,2], [1,2] ], # Knight
3 : [ [1,1], [-1,1], [1,-1], [-1,-1] ],                                 # Bishop
4 : [ [1,0], [-1,0], [0,-1], [ 0, 1] ],                                 # Rook
5 : [ [1,1], [-1,1], [1,-1], [-1,-1], [1,0], [-1,0], [0,-1], [0,1] ],   # Queen
6 : [ [1,1], [-1,1], [1,-1], [-1,-1], [1,0], [-1,0], [0,-1], [0,1] ]    # King
}


def generatePieceMoves( pos, board ):
    '''
    PRE : There is a piece in pos AND piece is not a pawn.
    Generates the valid moves for a given piece
    '''
    piece_moves = []
    i , j = pos
    piece = board[i][j]
    if piece > 0:
        pcolor = WHITE
    elif piece < 0:
        pcolor = BLACK
    dirs = PIECE_RAYS[piece * pcolor]

    for d in dirs:
        steps = 1
        done = False

        while not done:
            xi = i + d[0] * steps     # There...
            xj = j + d[1] * steps

            if not isOnBoard(xi, xj):
                done = True
            else:
                if board[xi][xj] != 0 : # There is a piece there..
                    done = True
                    if board[xi][xj] * pcolor < 0 :  # If opposite piece
                        piece_moves.append((i, j, xi, xj, 111))
                else: # empty space
                    piece_moves.append((i, j, xi, xj, 0))
            
            if piece*pcolor == 2 or piece*pcolor == 6 :  # If piece is knight or king.
                done = True
            
            steps += 1

    return piece_moves



PAWN_MOVE    = {1 : [-1, 0],             -1 : [1, 0] }
PAWN_CAPTURE = {1 : [[-1, -1],[-1, 1]],  -1 : [[1, -1],[1, 1]] }
PAWN_HOME    = {1 : 6,                   -1 : 1 }
PAWN_PROMO   = {1 : 0,                   -1 : 7 }

def generatePawnMoves( pos , board ) :
    '''
    PRE: piece at pos is a pawn
    Generates legal valid moves for a given Pawn
    '''
    i , j = pos
    piece = board[i][j]
    pawn_moves = []

    # compute moves
    xi = i + PAWN_MOVE[piece][0]
    xj = j + PAWN_MOVE[piece][1]

    if isOnBoard(xi, xj) and board[xi][xj] == 0 :  # square is empty
        if xi == PAWN_PROMO[piece] :
            for promo in range(2,6) :
                pawn_moves.append((i, j, xi, xj, promo*piece))
        else :
            pawn_moves.append((i, j, xi, xj, 0))

        xi = xi + PAWN_MOVE[piece][0]
        xj = xj + PAWN_MOVE[piece][1]
        if i == PAWN_HOME[piece] and board[xi][xj] == 0 :
            pawn_moves.append((i, j, xi, xj, 0))    
        
    # compute captures
    for drn in PAWN_CAPTURE[piece] :
        xi = i + drn[0]
        xj = j + drn[1]
        if isOnBoard(xi, xj) and board[xi][xj] * piece < 0 :  # If opposite piece
            if xi == PAWN_PROMO[piece] :
                for promo in range(2,6) :
                    pawn_moves.append((i, j, xi, xj, promo*piece))
            else :
                pawn_moves.append((i, j, xi, xj, 111))

    return pawn_moves


def generateCastleMoves( pos , board ) :
    '''
    PRE: piece at pos is a king
    '''
    return []

# ------------------------

def generateAllMoves( board, color ) :
    '''
    All moves are generated from here
    '''
    moves = []
    for i in range(8) :
        for j in range(8) :
            piece = board[i][j] * color

            m = []
            if piece == 1 :
                m = generatePawnMoves( (i,j), board )
            elif piece > 1 :
                m = generatePieceMoves( (i,j), board )
            moves.extend(m)

            m = []
            if piece == 6 :
                m = generateCastleMoves( (i,j), board )
            moves.extend(m)

    return moves
# ------------------------


PIECE_WEIGHT = { 6 :  1000,  5 :  9,  4 :  5,  3 :  3,  2 :  3,  1 :  1, 
                -6 : -1000, -5 : -9, -4 : -5, -3 : -3, -2 : -3, -1 : -1, 0 : 0}

def eval_function( board, color ):
    '''
    Estimates the materialistic value of the given state, determines the chance of winning
    '''
    value = 0
    for r in range(8):
        for f in range(8):
            element = board[r][f]

            value += PIECE_WEIGHT[element] * color
               
    return value


def maximizer5( board, color, depth, alpha, beta, killer_moves ):

    '''
    implementing KILLER MOVES as the special feature.
    This is Maximizer function used in the Time Limited ID DL Minimax
    '''

    v = NEG_INF
    a = None
    a2 = None

    board_val = eval_function( board, color )
    if board_val > 500 or board_val < -500 :    # is board terminal
        return board_val, []

    if depth == 0:
        return board_val, []

    gen_moves = generateAllMoves( board, color )

    # --- KILLER MOVES! ----
    moves = []
    if depth+1 < len(killer_moves) :
        k_move = killer_moves[depth+1]
        if k_move in gen_moves :
            # push it to the front of the moves list
            moves = [ k_move ]
    moves.extend(gen_moves)
    # ---

    for move in moves:
        board2 = nextBoard( board, move )
        board2_val, board2_act = minimizer5( board2, color, depth-1, alpha, beta, killer_moves )

        if board2_val > v:
            v = board2_val
            a = move
            a2 = board2_act
        
        if v >= beta:
            a2.append(a)
            return v, a2
        
        if v > alpha:
            alpha = v

    a2.append(a)
    return v, a2


def minimizer5( board, color, depth, alpha, beta, killer_moves ):

    '''
    implemented KILLER MOVES as the special feature.
    This is Minimizer function used in the Time Limited ID DL Minimax Alpha beta prunning
    '''

    v = POS_INF
    a = None
    a2 = None

    board_val = eval_function( board, color )
    if board_val > 500 or board_val < -500 :    # is board terminal
        return board_val, []
    
    if depth == 0:
        return board_val, []

    gen_moves = generateAllMoves( board, -1*color )

    # --- KILLER MOVES! ----
    moves = []
    if depth+1 < len(killer_moves) :
        k_move = killer_moves[depth+1]
        if k_move in gen_moves :
            # push it to the front of the moves list
            moves = [ k_move ]
    moves.extend(gen_moves)
    # ---

    for move in moves:
        board2 = nextBoard( board, move )
        board2_val, board2_act = maximizer5( board2, color, depth-1, alpha, beta, killer_moves )

        if board2_val < v : 
            v = board2_val
            a = move
            a2 = board2_act

        if v <= alpha:
            a2.append(a)
            return v, a2

        if v < beta:
            beta = v

    a2.append(a)
    return v, a2



MAX_DEPTH = 3
def IterativeDeepeningDLMinimax( board, color ) :
    '''
    Iterative deepening Depth Limited (D = 3) Minimax implementation
    '''
    besta = None
    for d in range(1, MAX_DEPTH+1) :
        v1, la = maximizer3( board, color, d )
        la.reverse()
        plan = map(getUCI, la)
        # print("max3,", d, v1, list(plan))
        besta = list(plan)[0]
    return besta
    

def timeLimitedIDDLMinimax( board, color, time_rem, turn ):

    '''
    this Time Limited ID DL Minimax is for GAME 3
    '''
    besta = None
    time_turn = time_rem / ( max(2, (30-turn) ) ) 
    time_turn = time_turn / 1000000000     # change time_turn to seconds
    time_start = time.time()

    print('Here! ', end='')
    print(time_rem, time_turn, time_start) 

    depth = 1
    time_now = time.time()
    while time_now < ( time_start + (0.20 * time_turn) ) :
        v, la = maximizer4( board, color, depth, NEG_INF, POS_INF )
        depth += 1
        time_now = time.time()

    la.reverse()
    besta = getUCI( la[0] )
    
    print('Depth Reached = ', depth)
    return besta


def timeLimitedIDDLMinimax2( board, color, time_rem, turn, killer_moves ):
    '''
    this Time Limited ID DL Minimax is for GAME 3+, implemented KILLER MOVES FEATURE
    '''
    besta = None
    time_turn = time_rem / ( max(2, (30-turn) ) ) 
    time_turn = time_turn / 1000000000     # change time_turn to seconds
    time_start = time.time()

    print('This turn ', time_turn, 'sec')
    
    depth = 1
    time_now = time.time()
    while time_now < ( time_start + (0.20 * time_turn) ) :
        v, best_plan = maximizer5( board, color, depth, NEG_INF, POS_INF, killer_moves )
        depth += 1
        time_now = time.time()
 
    print('Depth Reached = ', depth)
    return best_plan