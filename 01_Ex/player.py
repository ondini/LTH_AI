import copy
import time

MAXTIME = 4.7 #time limit in seconds

class MyPlayer():
    '''alpha-beta pruning game player'''
    def __init__(self, my_color, opponent_color, board_size, evfun=0):
        self.my_color = my_color
        self.opponent_color = opponent_color
        self.evfun = evfun

        self.board_size = board_size
        self.depth = 0                                             # holds currnet depth in search tree
        self.maxdepth = 4                                          # holds max depth in search tree from iterative deepening
    
    def reset_atts(self):
        self.depth = 0
        self.maxdepth = 3
        
    def move(self,board):
        self.time = time.time() #starting time
        a = -float('Inf')       #alpha
        b =  float('Inf')       #beta
        
        maxsearched = (0,0)  
        #while True:
        #self.maxdepth += 1
        best_next = (-float('Inf'),(0,0))   #(best_successor_value, best_successor)

        for move in self.get_all_valid_moves(board, self.my_color):
            board_changed = self.get_board_copy(board)
            self.play_move(move, board_changed, self.my_color)
            
            value = self.minvalue(board_changed, a, b)
            if value == -float('Inf'):
                self.reset_atts()
                return maxsearched
                
            if value > best_next[0]:
                best_next = (value, move)
            #pepa = False
        self.depth = 0   
        maxsearched = best_next[1]
        self.reset_atts()
        return maxsearched
        
    def minvalue(self, board, a, b):
        '''
        Min-part of alpha-beta pruning.
        Returns the lowest-valued successor.
        '''
        if (time.time() - self.time) > MAXTIME:                                     #max time reached
            return -float('Inf')                               
    
        self.depth += 1                                                         #proceeded to next layer        
        moves = self.get_all_valid_moves(board,self.opponent_color)
        
        score = self.get_score(board)
        if (moves == None) or (self.depth == self.maxdepth) or (abs(score) > 1000):
            self.depth -= 1
            return score
            
        node_value = float('Inf')
        for move in moves:
            board_changed = self.get_board_copy(board)
            self.play_move(move, board_changed, self.opponent_color)
            
            returned_value = self.maxvalue(board_changed, a, b)
            
            if returned_value == -float('Inf'):
                self.depth =- 1
                return -float('Inf')
            
            node_value = min(node_value, returned_value)
            if node_value <= a:  
                self.depth -= 1
                return node_value                                       #no need to check other successors
            b = min(b, node_value)
        self.depth -= 1                                                 #exitting this layer
        return node_value
        
    def maxvalue(self, board, a, b):
        '''
        Maxpart of alpha-beta pruning.
        Returns the highest-valued successor.
        '''
        if (time.time() - self.time) > MAXTIME:                         #max time reached
            return -float('Inf')
            
        self.depth += 1                                                 #proceeded to next layer        
        moves = self.get_all_valid_moves(board, self.my_color)
        
        if (moves == None) or (self.depth == self.maxdepth):
            self.depth -= 1
            return self.get_score(board)
            
        node_value = -float('Inf')
        for move in moves:
            board_changed = self.get_board_copy(board)
            self.play_move(move, board_changed, self.my_color)
            
            returned_value = self.minvalue(board_changed, a, b)
            
            if returned_value == -float('Inf'):
                self.depth =- 1
                return -float('Inf')
                
            node_value = max(node_value, returned_value)
            if node_value >= b:
                self.depth -= 1
                return node_value
            a = max(a, node_value)
        self.depth -= 1
        return node_value

    def get_score(self, board):
        ''' 
        Return heuristically computed score of given board.
        '''

        return self.evaluation_function(board)             
               

    def get_all_valid_moves(self, board, players_color):

        valid_moves = []
        for col in range(self.board_size[1]):
            if board[0, col] == 0:
                valid_moves.append(col)
        return valid_moves
        
    def get_opponent(self, players_color):
        return self.opponent_color if players_color == self.my_color else self.my_color
    

    def get_board_copy(self, board):
        return copy.deepcopy(board)

    def play_move(self, move, board, players_color):
        for row in range(1, self.board_size[0]+1):
            if row == self.board_size[0] or board[row, move] != 0:
                board[row-1, move] = players_color
                break;

    
    def evaluation_function(self, state):
        my_fours = self.checkForStreak(state, self.my_color, 4)
        my_threes = self.checkForStreak(state, self.my_color, 3)
        my_twos = self.checkForStreak(state, self.my_color, 2)
        opponent_fours = self.checkForStreak(state, self.opponent_color, 4)
        opponent_threes = self.checkForStreak(state, self.opponent_color, 3)
        opponent_twos = self.checkForStreak(state, self.opponent_color, 2)
        if self.evfun == 0:
            return (my_fours * 100000 + my_threes * 100 + my_twos*2) - (opponent_threes * 100 + opponent_twos * 2) if opponent_fours == 0 else -100000 # (opponent_fours * 10 + opponent_threes * 5 + opponent_twos * 2)
        elif self.evfun == 1: 
            return (my_fours * 100 + my_threes * 5 + my_twos*2) - (opponent_fours * 100 + opponent_threes * 5 + opponent_twos * 2)
        elif self.evfun ==2:
            return (my_fours * 100000 + my_threes * 100 + my_twos) if opponent_fours == 0 else -100000
        else:
            return 100000 if my_fours > 0 else ((my_threes * 100 + my_twos*2) - ( opponent_threes * 100 + opponent_twos * 2) if opponent_fours == 0 else -100000)
        
    def checkForStreak(self, state, color, streak):
        count = 0
        for i in range(6):
            for j in range(7):
                if state[i][j] == color:
                    count += self.verticalStreak(i, j, state, streak)
                    count += self.horizontalStreak(i, j, state, streak)
                    count += self.diagonalCheck(i, j, state, streak)
        return count

    def verticalStreak(self, row, column, state, streak):
        consecutiveCount = 0
        for i in range(row, 6):
            if state[i, column] == state[row, column]:
                consecutiveCount += 1
            else:
                break
        if consecutiveCount >= streak:
            return 1
        else:
            return 0

    def horizontalStreak(self, row, column, state, streak):
        count = 0
        for j in range(column, 7):
            if state[row, j] == state[row, column]:
                count += 1
            else:
                break
        if count >= streak:
            return 1
        else:
            return 0

    def diagonalCheck(self, row, column, state, streak):
        total = 0
        count = 0
        j = column
        for i in range(row, 6):
            if j > 6:
                break
            elif state[i, j] == state[row, column]:
                count += 1
            else:
                break
            j += 1
        if count >= streak:
            total += 1
        count = 0
        j = column
        for i in range(row, -1, -1):
            if j > 6:
                break
            elif state[i,j] == state[row, column]:
                count += 1
            else:
                break
            j += 1
        if count >= streak:
            total += 1
        return total