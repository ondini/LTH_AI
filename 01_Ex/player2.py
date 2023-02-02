import copy
import time
import numpy as np

MAXTIME = 4.7 #time limit in seconds

class ABPlayer():
    '''alpha-beta pruning game player'''
    def __init__(self, my_color, opponent_color, board_size, k=0, it_deep=False):
        # game attributes
        self.my_color = my_color
        self.opponent_color = opponent_color
        self.board_size = board_size
        self.ka = k
        # a-b pruning attributes
        self.it_deep = it_deep
        self.depth = 0               # holds current depth in search tree
        self.maxdepth = 3           # holds max depth in search tree from iterative deepening
    
    def reset_atts(self):
        self.depth = 0
        self.maxdepth = 3

    def move(self,board):
        self.time = time.time() # starting time
        a = -float('Inf')       # alpha
        b =  float('Inf')       # beta
        
        maxsearched = (0,0) # best move found so far in ITD
        itd = True
        while itd:
            self.maxdepth += 1
            best_next = (-float('Inf'),(0,0))   #(best_successor_value, best_successor) # best successor found so far in current ITD round

            for move in self.get_all_valid_moves(board, self.my_color):
                board_changed = self.get_board_copy(board)
                self.play_move(move, board_changed, self.my_color)
                
                value = self.minvalue(board_changed, a, b)
                if value == -float('Inf'):
                    self.reset_atts()
                    return maxsearched
                    
                if value > best_next[0]:
                    best_next = (value, move)

            self.depth = 0   
            maxsearched = best_next[1]
            itd = self.it_deep
            
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
        my_fours = self.checkForStreak(board, self.my_color, 4)
        my_threes = self.checkForStreak(board, self.my_color, 3)
        my_twos = self.checkForStreak(board, self.my_color, 2)
        opponent_fours = self.checkForStreak(board, self.opponent_color, 4)
        opponent_threes = self.checkForStreak(board, self.opponent_color, 3)
        opponent_twos = self.checkForStreak(board, self.opponent_color, 2)

        #print(self.ka)
        if self.ka == 0:
            #print("returning")
            return (my_fours * 1000 + my_threes * 50 + my_twos) - (opponent_threes * 50 + opponent_twos * 2) if opponent_fours == 0 else -1000
        elif self.ka == 1:
            #print("returning aa")
            return (my_fours * 1000 + my_threes * 50 + my_twos) - (opponent_fours*-1000 * opponent_threes * 50 + opponent_twos)
        elif self.ka == 2:
            return 1000 if my_fours > 0 else ((my_threes * 50 + my_twos) - (opponent_threes * 50 + opponent_twos * 2) if opponent_fours == 0 else -1000)
          
               

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


    def find_connected(self, board, color, length):
        count = 0
        directions = [(1,1), (1,-1),(1,0),(0,1)]
        explored = np.zeros([4, *self.board_size])
        print(explored.shape)
        for i in range(self.board_size[0]):
            for j in range(self.board_size[0]):
                if state[i][j] == color:
                    for direction in range(4):
                        for k in range(1, length):
                            if (i + k * directions[direction][0] >= 0 and i + k * directions[direction][0] < self.board_size[0] and j + k * directions[direction][1] >= 0 and j + k * directions[direction][1] < self.board_size[1]):
                                if (state[i + k * directions[direction][0]][j + k * directions[direction][1]] == color and explored[direction][i + k * directions[direction][0]][j + k * directions[direction][1]] == 0):
                                    explored[direction][i + k * directions[direction][0]][j + k * directions[direction][1]] = 1
                                else:
                                    break
                            else:
                                break
                        consecutiveCount = 0
                        for i in range(row, 6):
                            if state[i, column] == state[row, column]:
                                consecutiveCount += 1
                        
                        count += self.verticalStreak(i, j, state, streak)
                        count += self.horizontalStreak(i, j, state, streak)
                        count += self.diagonalCheck(i, j, state, streak)
        return 0

