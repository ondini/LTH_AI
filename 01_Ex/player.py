import copy
import time
import numpy as np

MAXTIME = 4.7 #time limit in seconds

class ABPlayer():
    '''alpha-beta pruning game player'''
    def __init__(self, my_color, opponent_color, board_size, it_deep=False):
        # game attributes
        self.my_color = my_color
        self.opponent_color = opponent_color
        self.board_size = board_size

        # a-b pruning attributes
        self.it_deep = it_deep
        self.depth = 0               # holds current depth in search tree
        self.maxdepth = 4           # holds max depth in search tree from iterative deepening
    
    def reset_atts(self):
        self.depth = 0
        self.maxdepth = 4

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

    def get_score(self, state):
        ''' 
        Return heuristically computed evaluation of given board.
        '''
        player_results = self.find_connected(state, self.my_color)
        opponent_results = self.find_connected(state, self.opponent_color)

        p4 = player_results[:,2].sum() # player's four-in-a-row count
        p3 = player_results[:,1].sum() # player's theree-in-a-row count
        p2 = player_results[:,0].sum() # player's two-in-a-row count

        o4 = opponent_results[:,2].sum() # opponent's four-in-a-row count
        o3 = opponent_results[:,1].sum() # ...
        o2 = opponent_results[:,0].sum()

        return (p4 * 1000 + p3 * 50 + p2) - (o3 * 50 + o2 * 2) if o4 == 0 else -1000

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

    def find_connected(self, board, c):
        directions = [(1,1), (1,-1),(1,0),(0,1)] # directions to explore
        explored = np.zeros([4, *self.board_size]) # explored nodes in each direction
        counts = np.zeros([4,4]) # couts of streaks of length 2, 3 and 4 in each direction
        for i in range(self.board_size[0]): # go through all the board
            for j in range(self.board_size[1]):
                if board[i][j] == c: # if the color is the same as the color we are looking for
                    for direction in range(4): # look for streaks in all the directions
                        if explored[direction][i][j] == 0: # if we haven't explored this direction through this node yet
                            explored[direction][i][j] = 1 # mark as explored and start exploring the direction
                        else: 
                            continue
                        for k in range(1, 5): # look for streaks of full length
                            # check if we are still in the board and if the color is the same
                            if (i + k * directions[direction][0] >= 0 and i + k * directions[direction][0] < self.board_size[0] and j + k * directions[direction][1] >= 0 and j + k * directions[direction][1] < self.board_size[1]):
                                if (board[i + k * directions[direction][0]][j + k * directions[direction][1]] == c ):
                                    # conditions satisfied, mark as explored
                                    explored[direction][i + k * directions[direction][0]][j + k * directions[direction][1]] = 1
                                else:
                                    break
                            else:
                                break

                        counts[direction][k-1] += 1 # add the found streak to the counter
        return counts[:,1:]

